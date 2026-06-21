import { create } from 'zustand';

export interface CutoffInfo {
  cap_round: string;
  category: string;
  seat_scope: string;
  cutoff_rank: number;
  cutoff_percentile: number;
  recommendation_score?: number;
}

export interface CollegeResponse {
  college_code: string;
  college_name: string;
  branch_code: string;
  branch_name: string;
  region: string | null;
  distance_km: number | null;
  highest_package_lpa: number | null;
  average_package_lpa: number | null;
  median_package_lpa: number | null;
  placement_percentage: number | null;
  top_recruiters: string | null;
  cutoffs: CutoffInfo[];
}

export interface OptionsResponse {
  categories: string[];
  branches: string[];
  seat_allocations: string[];
  seat_scopes: string[];
  rounds: string[];
  recruiters: string[];
  regions: string[];
}

export interface SearchState {
  percentile: number;
  percentile_buffer: number;
  categories: string[];
  branches: string[];
  seat_allocations: string[];
  seat_scopes: string[];
  rounds: string[];
  regions: string[];
  recruiters: string[];
  recruiter_match: string;
  lat: number | null;
  lng: number | null;
  sort_by: string;
  
  options: OptionsResponse | null;
  results: CollegeResponse[];
  loading: boolean;
  error: string | null;

  setFilter: (key: keyof SearchState, value: any) => void;
  fetchOptions: () => Promise<void>;
  search: () => Promise<void>;
  getLocation: () => void;
}

export const useSearchStore = create<SearchState>((set, get) => ({
  percentile: 90,
  percentile_buffer: 2,
  categories: [],
  branches: [],
  seat_allocations: [],
  seat_scopes: [],
  rounds: [],
  regions: [],
  recruiters: [],
  recruiter_match: "ANY",
  lat: null,
  lng: null,
  sort_by: "",
  
  options: null,
  results: [],
  loading: false,
  error: null,

  setFilter: (key, value) => set((state) => ({ ...state, [key]: value })),

  fetchOptions: async () => {
    try {
      const res = await fetch("/api/options");
      if (!res.ok) throw new Error("Failed to fetch options");
      const data = await res.json();
      set({ options: data });
    } catch (err: any) {
      console.error(err);
      set({ error: err.message });
    }
  },

  search: async () => {
    set({ loading: true, error: null });
    try {
      const state = get();
      const payload = {
        percentile: state.percentile,
        percentile_buffer: state.percentile_buffer,
        categories: state.categories,
        branches: state.branches,
        seat_allocations: state.seat_allocations,
        seat_scopes: state.seat_scopes,
        rounds: state.rounds,
        regions: state.regions,
        recruiters: state.recruiters,
        recruiter_match: state.recruiter_match,
        lat: state.lat,
        lng: state.lng,
        sort_by: state.sort_by
      };
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Failed to search");
      const data = await res.json();
      set({ results: data, loading: false });
    } catch (err: any) {
      console.error(err);
      set({ error: err.message, loading: false });
    }
  },

  getLocation: () => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          set({ lat: position.coords.latitude, lng: position.coords.longitude });
          // optionally trigger search
          get().search();
        },
        (error) => {
          console.warn("Location error:", error.message);
          set({ error: "Location access denied or unavailable." });
        }
      );
    } else {
      set({ error: "Geolocation is not supported by this browser." });
    }
  }
}));
