from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class ObstacleType(str, enum.Enum):
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    POLYGON = "polygon"

class Obstacle(Base):
    __tablename__ = "obstacles"

    id = Column(Integer, primary_key=True, index=True)
    wall_id = Column(Integer, ForeignKey("walls.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255))
    obstacle_type = Column(Enum(ObstacleType), nullable=False)

    # Position: CENTER coordinates for all obstacle types (rectangle, circle, polygon)
    x = Column(Float, nullable=False)  # X coordinate of center in meters
    y = Column(Float, nullable=False)  # Y coordinate of center in meters

    # For rectangles
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)

    # For circles
    radius = Column(Float, nullable=True)

    # For polygons and complex shapes
    vertices = Column(JSON, nullable=True)  # List of [x, y] coordinates

    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    wall = relationship("Wall", back_populates="obstacles")

    __table_args__ = (
        Index('idx_obstacle_wall', 'wall_id'),
        Index('idx_obstacle_type', 'obstacle_type'),
    )
