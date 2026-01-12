"""Wall management service"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.wall import Wall
from app.models.obstacle import Obstacle
from app.schemas.wall import WallCreate, WallUpdate
from app.schemas.obstacle import ObstacleCreate, ObstacleUpdate

class WallService:
    """Service for wall operations"""

    @staticmethod
    def create_wall(db: Session, wall_data: WallCreate) -> Wall:
        """Create a new wall"""
        wall = Wall(**wall_data.model_dump(by_alias=False))
        db.add(wall)
        db.commit()
        db.refresh(wall)
        return wall

    @staticmethod
    def get_wall(db: Session, wall_id: int) -> Optional[Wall]:
        """Get wall by ID"""
        return db.query(Wall).filter(Wall.id == wall_id).first()

    @staticmethod
    def get_walls(db: Session, skip: int = 0, limit: int = 100) -> List[Wall]:
        """Get all walls"""
        return db.query(Wall).offset(skip).limit(limit).all()

    @staticmethod
    def update_wall(db: Session, wall_id: int, wall_data: WallUpdate) -> Optional[Wall]:
        """Update wall"""
        wall = db.query(Wall).filter(Wall.id == wall_id).first()
        if wall:
            update_data = wall_data.model_dump(exclude_unset=True, by_alias=False)
            for key, value in update_data.items():
                setattr(wall, key, value)
            db.commit()
            db.refresh(wall)
        return wall

    @staticmethod
    def delete_wall(db: Session, wall_id: int) -> bool:
        """Delete wall"""
        wall = db.query(Wall).filter(Wall.id == wall_id).first()
        if wall:
            db.delete(wall)
            db.commit()
            return True
        return False

    @staticmethod
    def add_obstacle(db: Session, obstacle_data: ObstacleCreate) -> Obstacle:
        """Add obstacle to wall"""
        obstacle = Obstacle(**obstacle_data.model_dump(by_alias=False))
        db.add(obstacle)
        db.commit()
        db.refresh(obstacle)
        return obstacle

    @staticmethod
    def get_obstacles(db: Session, wall_id: int) -> List[Obstacle]:
        """Get all obstacles for a wall"""
        return db.query(Obstacle).filter(Obstacle.wall_id == wall_id).all()

    @staticmethod
    def update_obstacle(db: Session, obstacle_id: int,
                       obstacle_data: ObstacleUpdate) -> Optional[Obstacle]:
        """Update obstacle"""
        obstacle = db.query(Obstacle).filter(Obstacle.id == obstacle_id).first()
        if obstacle:
            update_data = obstacle_data.model_dump(exclude_unset=True, by_alias=False)
            for key, value in update_data.items():
                setattr(obstacle, key, value)
            db.commit()
            db.refresh(obstacle)
        return obstacle

    @staticmethod
    def delete_obstacle(db: Session, obstacle_id: int) -> bool:
        """Delete obstacle"""
        obstacle = db.query(Obstacle).filter(Obstacle.id == obstacle_id).first()
        if obstacle:
            db.delete(obstacle)
            db.commit()
            return True
        return False
