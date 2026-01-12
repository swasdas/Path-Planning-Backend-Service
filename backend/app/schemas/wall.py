from pydantic import BaseModel, Field, field_serializer
from typing import Optional, Dict, List
from datetime import datetime

class WallBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    width: float = Field(..., gt=0, description="Width in meters")
    height: float = Field(..., gt=0, description="Height in meters")
    surface_type: str = Field(default="standard", max_length=50)
    metadata_: Optional[Dict] = Field(default_factory=dict, alias="metadata", serialization_alias="metadata")

class WallCreate(WallBase):
    pass

class WallUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    width: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    surface_type: Optional[str] = Field(None, max_length=50)
    metadata_: Optional[Dict] = Field(None, alias="metadata", serialization_alias="metadata")

class WallResponse(WallBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True
