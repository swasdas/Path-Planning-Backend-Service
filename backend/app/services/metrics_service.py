"""Metrics service"""
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.trajectory import Trajectory, TrajectoryStatus
from app.models.wall import Wall
from app.schemas.metrics import SystemStatsResponse

class MetricsService:
    """Service for metrics operations"""

    @staticmethod
    def get_system_stats(db: Session) -> SystemStatsResponse:
        """Get system-wide statistics"""
        # Total walls
        total_walls = db.query(func.count(Wall.id)).scalar()

        # Total trajectories
        total_trajectories = db.query(func.count(Trajectory.id)).scalar()

        # Average planning time
        avg_planning_time = db.query(func.avg(Trajectory.planning_time)).scalar() or 0.0

        # Average coverage
        avg_coverage = db.query(func.avg(Trajectory.coverage_percentage)).scalar() or 0.0

        # Success rate
        completed = db.query(func.count(Trajectory.id)).filter(
            Trajectory.status == TrajectoryStatus.COMPLETED
        ).scalar()
        success_rate = (completed / total_trajectories * 100) if total_trajectories > 0 else 0.0

        # Algorithm stats
        algorithm_stats = {}
        for algo_type in ["coverage", "astar", "genetic", "hybrid"]:
            count = db.query(func.count(Trajectory.id)).filter(
                Trajectory.algorithm_type == algo_type
            ).scalar()
            algorithm_stats[algo_type] = count

        return SystemStatsResponse(
            total_walls=total_walls,
            total_trajectories=total_trajectories,
            avg_planning_time=avg_planning_time,
            avg_coverage=avg_coverage,
            success_rate=success_rate,
            algorithm_stats=algorithm_stats
        )

    @staticmethod
    def get_wall_metrics(db: Session, wall_id: int) -> Dict:
        """Get metrics for a specific wall"""
        trajectories = db.query(Trajectory).filter(Trajectory.wall_id == wall_id).all()

        if not trajectories:
            return {
                "wall_id": wall_id,
                "total_paths": 0,
                "avg_distance": 0.0,
                "avg_coverage": 0.0,
                "avg_planning_time": 0.0
            }

        total_paths = len(trajectories)
        avg_distance = sum(t.total_distance or 0 for t in trajectories) / total_paths
        avg_coverage = sum(t.coverage_percentage or 0 for t in trajectories) / total_paths
        avg_planning_time = sum(t.planning_time or 0 for t in trajectories) / total_paths

        return {
            "wall_id": wall_id,
            "total_paths": total_paths,
            "avg_distance": avg_distance,
            "avg_coverage": avg_coverage,
            "avg_planning_time": avg_planning_time
        }
