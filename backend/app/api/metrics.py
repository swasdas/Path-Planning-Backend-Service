"""Metrics API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.metrics import SystemStatsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/system", response_model=SystemStatsResponse)
def get_system_stats(db: Session = Depends(get_db)):
    """Get system-wide statistics"""
    return MetricsService.get_system_stats(db)

@router.get("/walls/{wall_id}")
def get_wall_metrics(wall_id: int, db: Session = Depends(get_db)):
    """Get metrics for a specific wall"""
    return MetricsService.get_wall_metrics(db, wall_id)
