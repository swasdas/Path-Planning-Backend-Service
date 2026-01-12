"""Wall API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.wall import WallCreate, WallUpdate, WallResponse
from app.schemas.obstacle import ObstacleCreate, ObstacleCreateRequest, ObstacleResponse
from app.services.wall_service import WallService

router = APIRouter(prefix="/walls", tags=["walls"])

@router.post("/", response_model=WallResponse, status_code=201)
def create_wall(wall: WallCreate, db: Session = Depends(get_db)):
    """Create a new wall"""
    db_wall = WallService.create_wall(db, wall)
    # Manually construct response to avoid SQLAlchemy metadata conflict
    return WallResponse(
        id=db_wall.id,
        name=db_wall.name,
        width=db_wall.width,
        height=db_wall.height,
        surface_type=db_wall.surface_type,
        metadata_=db_wall.metadata_ or {},
        created_at=db_wall.created_at,
        updated_at=db_wall.updated_at
    )

@router.get("/", response_model=List[WallResponse])
def get_walls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all walls"""
    db_walls = WallService.get_walls(db, skip, limit)
    return [
        WallResponse(
            id=w.id,
            name=w.name,
            width=w.width,
            height=w.height,
            surface_type=w.surface_type,
            metadata_=w.metadata_ or {},
            created_at=w.created_at,
            updated_at=w.updated_at
        ) for w in db_walls
    ]

@router.get("/{wall_id}", response_model=WallResponse)
def get_wall(wall_id: int, db: Session = Depends(get_db)):
    """Get wall by ID"""
    db_wall = WallService.get_wall(db, wall_id)
    if not db_wall:
        raise HTTPException(status_code=404, detail="Wall not found")
    return WallResponse(
        id=db_wall.id,
        name=db_wall.name,
        width=db_wall.width,
        height=db_wall.height,
        surface_type=db_wall.surface_type,
        metadata_=db_wall.metadata_ or {},
        created_at=db_wall.created_at,
        updated_at=db_wall.updated_at
    )

@router.put("/{wall_id}", response_model=WallResponse)
def update_wall(wall_id: int, wall: WallUpdate, db: Session = Depends(get_db)):
    """Update wall"""
    db_wall = WallService.update_wall(db, wall_id, wall)
    if not db_wall:
        raise HTTPException(status_code=404, detail="Wall not found")
    return WallResponse(
        id=db_wall.id,
        name=db_wall.name,
        width=db_wall.width,
        height=db_wall.height,
        surface_type=db_wall.surface_type,
        metadata_=db_wall.metadata_ or {},
        created_at=db_wall.created_at,
        updated_at=db_wall.updated_at
    )

@router.delete("/{wall_id}", status_code=204)
def delete_wall(wall_id: int, db: Session = Depends(get_db)):
    """Delete wall"""
    if not WallService.delete_wall(db, wall_id):
        raise HTTPException(status_code=404, detail="Wall not found")

@router.post("/{wall_id}/obstacles", response_model=ObstacleResponse, status_code=201)
def add_obstacle(wall_id: int, obstacle: ObstacleCreateRequest, db: Session = Depends(get_db)):
    """Add obstacle to wall"""
    # Verify wall exists
    wall = WallService.get_wall(db, wall_id)
    if not wall:
        raise HTTPException(status_code=404, detail="Wall not found")

    # Create ObstacleCreate with wall_id from path
    obstacle_data = ObstacleCreate(wall_id=wall_id, **obstacle.model_dump())
    db_obstacle = WallService.add_obstacle(db, obstacle_data)
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

@router.get("/{wall_id}/obstacles", response_model=List[ObstacleResponse])
def get_obstacles(wall_id: int, db: Session = Depends(get_db)):
    """Get all obstacles for a wall"""
    db_obstacles = WallService.get_obstacles(db, wall_id)
    return [
        ObstacleResponse(
            id=o.id,
            wall_id=o.wall_id,
            name=o.name,
            obstacle_type=o.obstacle_type,
            x=o.x,
            y=o.y,
            width=o.width,
            height=o.height,
            radius=o.radius,
            vertices=o.vertices,
            metadata_=o.metadata_ or {},
            created_at=o.created_at,
            updated_at=o.updated_at
        ) for o in db_obstacles
    ]
