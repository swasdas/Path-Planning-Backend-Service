from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base

class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String(100), nullable=False)  # e.g., "api_latency", "algorithm_performance"
    metric_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50))  # e.g., "ms", "seconds", "meters"
    tags = Column(JSON, default={})  # Additional metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    module = Column(String(100))
    function = Column(String(100))
    trajectory_id = Column(Integer, nullable=True)
    wall_id = Column(Integer, nullable=True)
    extra_data = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
