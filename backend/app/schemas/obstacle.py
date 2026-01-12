from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from datetime import datetime
from app.models.obstacle import ObstacleType

class ObstacleBase(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    obstacle_type: ObstacleType
    x: float = Field(..., description="X coordinate of obstacle CENTER in meters")
    y: float = Field(..., description="Y coordinate of obstacle CENTER in meters")

    # For rectangles
    width: Optional[float] = Field(None, gt=0, description="Width in meters (for rectangles)")
    height: Optional[float] = Field(None, gt=0, description="Height in meters (for rectangles)")

    # For circles
    radius: Optional[float] = Field(None, gt=0, description="Radius in meters (for circles)")

    # For polygons
    vertices: Optional[List[List[float]]] = Field(None, description="List of [x, y] coordinates (for polygons)")

    metadata_: Optional[Dict] = Field(default_factory=dict, alias="metadata", serialization_alias="metadata")

    @field_validator('vertices')
    @classmethod
    def validate_vertices(cls, v, info):
        if v is not None:
            if len(v) < 3:
                raise ValueError("Polygon must have at least 3 vertices")
            for vertex in v:
                if len(vertex) != 2:
                    raise ValueError("Each vertex must have exactly 2 coordinates [x, y]")
        return v

class ObstacleCreateRequest(ObstacleBase):
    """Schema for creating an obstacle via wall endpoint (wall_id from path)"""
    pass

class ObstacleCreate(ObstacleBase):
    """Schema for creating an obstacle with wall_id"""
    wall_id: int

class ObstacleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    radius: Optional[float] = Field(None, gt=0)
    vertices: Optional[List[List[float]]] = None
    metadata_: Optional[Dict] = Field(None, alias="metadata")

class ObstacleResponse(ObstacleBase):
    id: int
    wall_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True
