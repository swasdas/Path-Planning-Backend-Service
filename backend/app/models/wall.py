from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Wall(Base):
    __tablename__ = "walls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    width = Column(Float, nullable=False)  # meters
    height = Column(Float, nullable=False)  # meters
    surface_type = Column(String(50), default="standard")
    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    obstacles = relationship("Obstacle", back_populates="wall", cascade="all, delete-orphan")
    trajectories = relationship("Trajectory", back_populates="wall", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_wall_dimensions', 'width', 'height'),
    )
