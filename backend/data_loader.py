import pandas as pd
import numpy as np
import os
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def normalize_name(name):
    if pd.isna(name):
        return ""
    name = str(name).lower()
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

class DataLoader:
    def __init__(self):
        self.cap_data = pd.DataFrame()
        self.region_data = pd.DataFrame()
        self.package_data = pd.DataFrame()
        
        self.options = {
            "categories": [],
            "branches": [],
            "seat_allocations": [],
            "seat_scopes": ["HU", "OHU", "STATE"],
            "rounds": ["CAP1", "CAP2", "CAP3"],
            "recruiters": [],
            "regions": ["Mumbai", "Navi Mumbai", "Pune", "Others"]
        }
        
    def load_data(self):
        cap1_path = os.path.join(DATA_DIR, 'mht_cet_cap1_clean.csv')
        cap2_path = os.path.join(DATA_DIR, 'cap2_clean.csv')
        cap3_path = os.path.join(DATA_DIR, 'cap3_clean.csv')
        region_path = os.path.join(DATA_DIR, 'colleges_by_region.csv')
        package_path = os.path.join(DATA_DIR, 'college_packages.csv')
        
        cap_dfs = []
        for path, round_name in [(cap1_path, 'CAP1'), (cap2_path, 'CAP2'), (cap3_path, 'CAP3')]:
            if os.path.exists(path):
                df = pd.read_csv(path)
                df['cap_round'] = round_name
                # Filter to academic year 2025 if column exists
                if 'academic_year' in df.columns:
                    df = df[df['academic_year'] == 2025]
                cap_dfs.append(df)
                
        if cap_dfs:
            self.cap_data = pd.concat(cap_dfs, ignore_index=True)
            self.cap_data['normalized_name'] = self.cap_data['college_name'].apply(normalize_name)
            
            # Extract options
            if 'category' in self.cap_data.columns:
                self.options['categories'] = sorted(self.cap_data['category'].dropna().unique().tolist())
            if 'branch_name' in self.cap_data.columns:
                self.options['branches'] = sorted(self.cap_data['branch_name'].dropna().unique().tolist())
            if 'seat_allocation_type' in self.cap_data.columns:
                self.options['seat_allocations'] = sorted(self.cap_data['seat_allocation_type'].dropna().unique().tolist())
                
        if os.path.exists(region_path):
            self.region_data = pd.read_csv(region_path)
            self.region_data['normalized_name'] = self.region_data['college_name'].apply(normalize_name)
            
        if os.path.exists(package_path):
            self.package_data = pd.read_csv(package_path)
            self.package_data['normalized_name'] = self.package_data['college_name'].apply(normalize_name)
            
            recruiters_set = set()
            if 'top_recruiters' in self.package_data.columns:
                for rec_list in self.package_data['top_recruiters'].dropna():
                    recs = [r.strip() for r in str(rec_list).split(',')]
                    recruiters_set.update(r for r in recs if r)
            self.options['recruiters'] = sorted(list(recruiters_set))

    def get_options(self):
        return self.options
    
    def search(self, req):
        if self.cap_data.empty:
            return []
            
        # 1. Filter Cap Data
        df = self.cap_data.copy()
        
        # Determine percentile cutoff
        target_percentile = req.percentile
        if req.percentile_buffer > 0:
            target_percentile += req.percentile_buffer
            
        df = df[df['cutoff_percentile'] <= target_percentile]
        
        if req.categories:
            df = df[df['category'].isin(req.categories)]
            
        if req.branches:
            df = df[df['branch_name'].isin(req.branches)]
            
        if req.seat_allocations:
            df = df[df['seat_allocation_type'].isin(req.seat_allocations)]

        if req.seat_scopes:
            df = df[df['seat_scope'].isin(req.seat_scopes)]
            
        if req.rounds:
            df = df[df['cap_round'].isin(req.rounds)]
            
        # Group by college and branch to aggregate cutoffs
        # We need to map other info (region, package) to these groups
        
        # 2. Add Region Data
        if not self.region_data.empty:
            df = pd.merge(df, self.region_data[['normalized_name', 'region', 'latitude', 'longitude']], 
                          on='normalized_name', how='left')
        else:
            df['region'] = None
            df['latitude'] = None
            df['longitude'] = None
            
        # 3. Add Package Data
        if not self.package_data.empty:
            pkg_cols = ['normalized_name', 'highest_package_lpa', 'average_package_lpa', 'median_package_lpa', 'placement_percentage', 'top_recruiters']
            # Make sure columns exist
            available_pkg_cols = [c for c in pkg_cols if c in self.package_data.columns]
            df = pd.merge(df, self.package_data[available_pkg_cols], on='normalized_name', how='left')
        else:
            df['highest_package_lpa'] = None
            df['average_package_lpa'] = None
            df['median_package_lpa'] = None
            df['placement_percentage'] = None
            df['top_recruiters'] = None
            
        # 4. Filter by Region
        if req.regions:
            df = df[df['region'].isin(req.regions)]

        # 5. Filter by Recruiters
        if req.recruiters:
            def match_recruiter(val):
                if pd.isna(val):
                    return False
                recs = [r.strip() for r in str(val).split(',')]
                if req.recruiter_match == 'ANY':
                    return any(r in recs for r in req.recruiters)
                else: # ALL
                    return all(r in recs for r in req.recruiters)
            
            df = df[df['top_recruiters'].apply(match_recruiter)]
            
        # 5. Distance Calculation
        from geopy.distance import geodesic
        if req.lat is not None and req.lng is not None:
            user_coords = (req.lat, req.lng)
            def calc_dist(row):
                if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                    return None
                try:
                    return geodesic(user_coords, (row['latitude'], row['longitude'])).km
                except:
                    return None
            df['distance_km'] = df.apply(calc_dist, axis=1)
        else:
            df['distance_km'] = None
            
        # 6. Build response
        # Group by college_code and branch_code
        results = []
        
        # Sort beforehand if needed to pick the "best" cutoff per group or we just return all cutoffs in the group
        
        grouped = df.groupby(['college_code', 'branch_code'])
        for (ccode, bcode), group in grouped:
            first_row = group.iloc[0]
            
            # Pre-calculate Placement and Distance scores for this college
            # Placement (0-100)
            avg_pkg = float(first_row['average_package_lpa']) if pd.notna(first_row.get('average_package_lpa')) else 0.0
            placement_score = min((avg_pkg / 15.0) * 100.0, 100.0)
            
            # Distance (0-100)
            dist_km = float(first_row['distance_km']) if pd.notna(first_row.get('distance_km')) else None
            distance_score = 0.0
            if dist_km is not None:
                distance_score = max(0.0, 100.0 - (dist_km / 5.0))
            
            cutoffs = []
            for _, row in group.iterrows():
                cutoff_perc = float(row.get('cutoff_percentile', 0)) if pd.notna(row.get('cutoff_percentile')) else 0.0
                
                # Cutoff compatibility score (0-100)
                cutoff_score = max(0.0, 100.0 - ((req.percentile - cutoff_perc) * 3.0))
                
                # Final recommendation score
                rec_score = (placement_score * 0.5) + (distance_score * 0.3) + (cutoff_score * 0.2)
                
                cutoffs.append({
                    "cap_round": str(row.get('cap_round', '')),
                    "category": str(row.get('category', '')),
                    "seat_scope": str(row.get('seat_scope', '')),
                    "cutoff_rank": float(row.get('cutoff_rank', 0)) if pd.notna(row.get('cutoff_rank')) else 0.0,
                    "cutoff_percentile": cutoff_perc,
                    "recommendation_score": rec_score
                })
                
            c_name = str(first_row.get('college_name', ''))
            b_name = str(first_row.get('branch_name', ''))
            
            res = {
                "college_code": str(ccode),
                "college_name": c_name,
                "branch_code": str(bcode),
                "branch_name": b_name,
                "region": str(first_row['region']) if pd.notna(first_row.get('region')) else None,
                "distance_km": float(first_row['distance_km']) if pd.notna(first_row.get('distance_km')) else None,
                "highest_package_lpa": float(first_row['highest_package_lpa']) if pd.notna(first_row.get('highest_package_lpa')) else None,
                "average_package_lpa": float(first_row['average_package_lpa']) if pd.notna(first_row.get('average_package_lpa')) else None,
                "median_package_lpa": float(first_row['median_package_lpa']) if pd.notna(first_row.get('median_package_lpa')) else None,
                "placement_percentage": float(first_row['placement_percentage']) if pd.notna(first_row.get('placement_percentage')) else None,
                "top_recruiters": str(first_row['top_recruiters']) if pd.notna(first_row.get('top_recruiters')) else None,
                "cutoffs": cutoffs
            }
            results.append(res)
            
        # 7. Sorting
        if req.sort_by:
            if req.sort_by == "Recommendation Score":
                results.sort(key=lambda x: max([c['recommendation_score'] for c in x['cutoffs']] + [0]), reverse=True)
            elif req.sort_by == "Closest":
                results.sort(key=lambda x: (x['distance_km'] is None, x['distance_km']))
            elif req.sort_by == "Farthest":
                results.sort(key=lambda x: (x['distance_km'] is None, x['distance_km']), reverse=True)
            elif req.sort_by == "Highest Package":
                results.sort(key=lambda x: (x['highest_package_lpa'] is not None, x['highest_package_lpa']), reverse=True)
            elif req.sort_by == "Highest Placement %":
                results.sort(key=lambda x: (x['placement_percentage'] is None, x['placement_percentage']), reverse=True)
            elif req.sort_by == "Highest Cutoff":
                results.sort(key=lambda x: max([c['cutoff_percentile'] for c in x['cutoffs']] + [0]), reverse=True)
            elif req.sort_by == "Lowest Cutoff":
                results.sort(key=lambda x: min([c['cutoff_percentile'] for c in x['cutoffs']] + [100]))
            elif req.sort_by == "Alphabetical":
                results.sort(key=lambda x: x['college_name'])
                
        return results

data_loader = DataLoader()
data_loader.load_data()
