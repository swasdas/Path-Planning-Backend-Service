from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from app.models.trajectory import AlgorithmType, TrajectoryStatus

class Waypoint(BaseModel):
    x: float
    y: float
    z: Optional[float] = 0.0

class PathPlanRequest(BaseModel):
    wall_id: int
    algorithm_type: AlgorithmType = AlgorithmType.HYBRID
    parameters: Optional[Dict] = Field(default_factory=dict, description="Algorithm-specific parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "wall_id": 1,
                "algorithm_type": "hybrid",
                "parameters": {
                    "grid_resolution": 0.1,
                    "ga_population": 50,
                    "ga_generations": 30
                }
            }
        }

class TrajectoryResponse(BaseModel):
    id: int
    wall_id: int
    name: Optional[str]
    algorithm_type: AlgorithmType
    status: TrajectoryStatus
    waypoints: List[Dict]
    total_distance: Optional[float]
    estimated_time: Optional[float]
    coverage_percentage: Optional[float]
    planning_time: Optional[float]
    execution_time: Optional[float]
    actual_distance: Optional[float]
    parameters: Dict
    error_message: Optional[str]
    metadata_: Optional[Dict] = Field(None, alias="metadata", serialization_alias="metadata")
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True
