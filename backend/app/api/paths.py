"""Path planning API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.trajectory import PathPlanRequest, TrajectoryResponse
from app.services.path_service import PathService

router = APIRouter(prefix="/paths", tags=["paths"])
path_service = PathService()

@router.post("/plan", response_model=TrajectoryResponse, status_code=201)
def plan_path(
    request: PathPlanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Plan path for a wall

    This endpoint calculates the optimal path for the robot to cover the wall
    while avoiding obstacles using the specified algorithm.
    """
    try:
        db_trajectory = path_service.plan_path(
            db,
            request.wall_id,
            request.algorithm_type,
            request.parameters
        )
        return TrajectoryResponse(
            id=db_trajectory.id,
            wall_id=db_trajectory.wall_id,
            name=db_trajectory.name,
            algorithm_type=db_trajectory.algorithm_type,
            status=db_trajectory.status,
            waypoints=db_trajectory.waypoints,
            total_distance=db_trajectory.total_distance,
            estimated_time=db_trajectory.estimated_time,
            coverage_percentage=db_trajectory.coverage_percentage,
            planning_time=db_trajectory.planning_time,
            execution_time=db_trajectory.execution_time,
            actual_distance=db_trajectory.actual_distance,
            parameters=db_trajectory.parameters,
            error_message=db_trajectory.error_message,
            metadata_=db_trajectory.metadata_ or {},
            created_at=db_trajectory.created_at,
            updated_at=db_trajectory.updated_at,
            completed_at=db_trajectory.completed_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Path planning failed: {str(e)}")

@router.get("/trajectories", response_model=List[TrajectoryResponse])
def get_trajectories(
    wall_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all trajectories, optionally filtered by wall_id"""
    db_trajectories = path_service.get_trajectories(db, wall_id, skip, limit)
    return [
        TrajectoryResponse(
            id=t.id,
            wall_id=t.wall_id,
            name=t.name,
            algorithm_type=t.algorithm_type,
            status=t.status,
            waypoints=t.waypoints,
            total_distance=t.total_distance,
            estimated_time=t.estimated_time,
            coverage_percentage=t.coverage_percentage,
            planning_time=t.planning_time,
            execution_time=t.execution_time,
            actual_distance=t.actual_distance,
            parameters=t.parameters,
            error_message=t.error_message,
            metadata_=t.metadata_ or {},
            created_at=t.created_at,
            updated_at=t.updated_at,
            completed_at=t.completed_at
        ) for t in db_trajectories
    ]

@router.get("/trajectories/{trajectory_id}", response_model=TrajectoryResponse)
def get_trajectory(trajectory_id: int, db: Session = Depends(get_db)):
    """Get trajectory by ID"""
    db_trajectory = path_service.get_trajectory(db, trajectory_id)
    if not db_trajectory:
        raise HTTPException(status_code=404, detail="Trajectory not found")
    return TrajectoryResponse(
        id=db_trajectory.id,
        wall_id=db_trajectory.wall_id,
        name=db_trajectory.name,
        algorithm_type=db_trajectory.algorithm_type,
        status=db_trajectory.status,
        waypoints=db_trajectory.waypoints,
        total_distance=db_trajectory.total_distance,
        estimated_time=db_trajectory.estimated_time,
        coverage_percentage=db_trajectory.coverage_percentage,
        planning_time=db_trajectory.planning_time,
        execution_time=db_trajectory.execution_time,
        actual_distance=db_trajectory.actual_distance,
        parameters=db_trajectory.parameters,
        error_message=db_trajectory.error_message,
        metadata_=db_trajectory.metadata_ or {},
        created_at=db_trajectory.created_at,
        updated_at=db_trajectory.updated_at,
        completed_at=db_trajectory.completed_at
    )
