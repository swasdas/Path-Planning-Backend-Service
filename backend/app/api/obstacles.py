"""Obstacle API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.obstacle import ObstacleUpdate, ObstacleResponse
from app.services.wall_service import WallService

router = APIRouter(prefix="/obstacles", tags=["obstacles"])

@router.put("/{obstacle_id}", response_model=ObstacleResponse)
def update_obstacle(obstacle_id: int, obstacle: ObstacleUpdate, db: Session = Depends(get_db)):
    """Update obstacle"""
    db_obstacle = WallService.update_obstacle(db, obstacle_id, obstacle)
    if not db_obstacle:
        raise HTTPException(status_code=404, detail="Obstacle not found")
    return ObstacleResponse(
        id=db_obstacle.id,
        wall_id=db_obstacle.wall_id,
        name=db_obstacle.name,
        obstacle_type=db_obstacle.obstacle_type,
        x=db_obstacle.x,
        y=db_obstacle.y,
        width=db_obstacle.width,
        height=db_obstacle.height,
        radius=db_obstacle.radius,
        vertices=db_obstacle.vertices,
        metadata_=db_obstacle.metadata_ or {},
        created_at=db_obstacle.created_at,
        updated_at=db_obstacle.updated_at
    )

@router.delete("/{obstacle_id}", status_code=204)
def delete_obstacle(obstacle_id: int, db: Session = Depends(get_db)):
    """Delete obstacle"""
    if not WallService.delete_obstacle(db, obstacle_id):
        raise HTTPException(status_code=404, detail="Obstacle not found")
