from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime

class MetricsResponse(BaseModel):
    metric_type: str
    metric_name: str
    value: float
    unit: str
    tags: Dict
    timestamp: datetime

    class Config:
        from_attributes = True

class SystemStatsResponse(BaseModel):
    total_walls: int
    total_trajectories: int
    avg_planning_time: float
    avg_coverage: float
    success_rate: float
    algorithm_stats: Dict[str, int]
