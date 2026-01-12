from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, ForeignKey, Enum, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class AlgorithmType(str, enum.Enum):
    COVERAGE = "coverage"
    ASTAR = "astar"
    GENETIC = "genetic"
    HYBRID = "hybrid"

class TrajectoryStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNED = "planned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class Trajectory(Base):
    __tablename__ = "trajectories"

    id = Column(Integer, primary_key=True, index=True)
    wall_id = Column(Integer, ForeignKey("walls.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255))
    algorithm_type = Column(Enum(AlgorithmType), nullable=False)
    status = Column(Enum(TrajectoryStatus), default=TrajectoryStatus.PENDING)

    # Path data
    waypoints = Column(JSON, nullable=False)  # List of {x, y, z} points
    total_distance = Column(Float)  # meters
    estimated_time = Column(Float)  # seconds
    coverage_percentage = Column(Float)  # 0-100

    # Metrics
    planning_time = Column(Float)  # seconds
    execution_time = Column(Float, nullable=True)  # seconds
    actual_distance = Column(Float, nullable=True)  # meters

    # Algorithm parameters
    parameters = Column(JSON, default={})

    # Error handling
    error_message = Column(Text, nullable=True)

    metadata_ = Column("metadata", JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    wall = relationship("Wall", back_populates="trajectories")

    __table_args__ = (
        Index('idx_trajectory_wall', 'wall_id'),
        Index('idx_trajectory_status', 'status'),
        Index('idx_trajectory_algorithm', 'algorithm_type'),
    )
