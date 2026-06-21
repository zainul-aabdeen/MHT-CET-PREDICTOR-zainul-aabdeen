from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    percentile: float
    percentile_buffer: float = 0.0
    categories: List[str] = []
    branches: List[str] = []
    seat_allocations: List[str] = []
    seat_scopes: List[str] = []       # HU, OHU, STATE
    rounds: List[str] = []
    regions: List[str] = []
    recruiters: List[str] = []
    recruiter_match: str = "ANY"  # "ANY" or "ALL"
    lat: Optional[float] = None
    lng: Optional[float] = None
    sort_by: Optional[str] = None

class CutoffInfo(BaseModel):
    cap_round: str
    category: str
    seat_scope: str
    cutoff_rank: float
    cutoff_percentile: float
    recommendation_score: Optional[float] = None

class CollegeResponse(BaseModel):
    college_code: str
    college_name: str
    branch_code: str
    branch_name: str
    region: Optional[str] = None
    distance_km: Optional[float] = None
    
    highest_package_lpa: Optional[float] = None
    average_package_lpa: Optional[float] = None
    median_package_lpa: Optional[float] = None
    placement_percentage: Optional[float] = None
    top_recruiters: Optional[str] = None
    
    cutoffs: List[CutoffInfo] = []

class OptionsResponse(BaseModel):
    categories: List[str]
    branches: List[str]
    seat_allocations: List[str]
    seat_scopes: List[str]
    rounds: List[str]
    recruiters: List[str]
    regions: List[str]
