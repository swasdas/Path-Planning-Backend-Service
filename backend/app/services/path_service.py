"""Path planning service"""
import time
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.models.wall import Wall
from app.models.trajectory import Trajectory, AlgorithmType, TrajectoryStatus
from app.algorithms import GridManager, CoveragePlanner, AStarPlanner, GeneticOptimizer, HybridPlanner
from app.algorithms.geometry import calculate_path_length
from app.cache import get_redis_client
from app.config import settings

class PathService:
    """Service for path planning operations"""

    def __init__(self):
        self.redis = get_redis_client()

    def plan_path(self, db: Session, wall_id: int, algorithm_type: AlgorithmType,
                  parameters: Dict = None) -> Trajectory:
        """
        Plan path for a wall

        Args:
            db: Database session
            wall_id: Wall ID
            algorithm_type: Algorithm to use
            parameters: Algorithm parameters

        Returns:
            Trajectory object
        """
        # Check cache
        cache_key = f"path:{wall_id}:{algorithm_type}:{str(parameters)}"
        cached = self.redis.get(cache_key)
        if cached:
            return self._trajectory_from_cache(db, cached, wall_id)

        # Load wall and obstacles
        wall = db.query(Wall).filter(Wall.id == wall_id).first()
        if not wall:
            raise ValueError(f"Wall {wall_id} not found")

        # Start timing
        start_time = time.time()

        # Create grid
        resolution = parameters.get("grid_resolution", settings.grid_resolution) if parameters else settings.grid_resolution
        grid = GridManager(wall.width, wall.height, resolution)

        # Add obstacles
        obstacles_data = [
            {
                "obstacle_type": obs.obstacle_type,
                "x": obs.x,
                "y": obs.y,
                "width": obs.width,
                "height": obs.height,
                "radius": obs.radius,
                "vertices": obs.vertices
            }
            for obs in wall.obstacles
        ]
        grid.add_obstacles(obstacles_data)

        # Plan path based on algorithm
        waypoints = self._execute_algorithm(grid, algorithm_type, parameters)

        # Calculate metrics
        planning_time = time.time() - start_time
        total_distance = calculate_path_length(waypoints)
        coverage = grid.calculate_coverage(set(
            grid.world_to_grid(wp["x"], wp["y"]) for wp in waypoints
        ))
        estimated_time = total_distance / 0.5  # Assume 0.5 m/s speed

        # Create trajectory
        trajectory = Trajectory(
            wall_id=wall_id,
            name=f"{algorithm_type.value.upper()} Path",
            algorithm_type=algorithm_type,
            status=TrajectoryStatus.PLANNED,
            waypoints=waypoints,
            total_distance=total_distance,
            estimated_time=estimated_time,
            coverage_percentage=coverage,
            planning_time=planning_time,
            parameters=parameters or {}
        )

        db.add(trajectory)
        db.commit()
        db.refresh(trajectory)

        # Cache result
        self.redis.set(cache_key, {
            "algorithm_type": algorithm_type.value,
            "waypoints": waypoints,
            "metrics": {
                "total_distance": total_distance,
                "coverage": coverage,
                "planning_time": planning_time
            }
        }, ttl=3600)

        return trajectory

    def _execute_algorithm(self, grid: GridManager, algorithm_type: AlgorithmType,
                          parameters: Dict = None) -> List[Dict]:
        """Execute specific algorithm"""
        parameters = parameters or {}

        if algorithm_type == AlgorithmType.COVERAGE:
            planner = CoveragePlanner(grid)
            return planner.plan_with_obstacles()

        elif algorithm_type == AlgorithmType.ASTAR:
            planner = AStarPlanner(grid)
            # For A*, need start and goal
            start = parameters.get("start", (0, 0))
            goal = parameters.get("goal", (grid.rows - 1, grid.cols - 1))
            return planner.plan(start, goal)

        elif algorithm_type == AlgorithmType.GENETIC:
            # Start with coverage, then optimize
            coverage = CoveragePlanner(grid)
            initial_path = coverage.plan_with_obstacles()
            optimizer = GeneticOptimizer(
                grid,
                population_size=parameters.get("population_size", settings.ga_population_size),
                generations=parameters.get("generations", settings.ga_generations),
                mutation_rate=parameters.get("mutation_rate", settings.ga_mutation_rate),
                crossover_rate=parameters.get("crossover_rate", settings.ga_crossover_rate)
            )
            return optimizer.optimize(initial_path)

        elif algorithm_type == AlgorithmType.HYBRID:
            planner = HybridPlanner(grid, ga_params=parameters)
            return planner.plan()

        else:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")

    def _trajectory_from_cache(self, db: Session, cached_data: dict, wall_id: int) -> Trajectory:
        """Create trajectory from cached data"""
        algorithm_type = AlgorithmType(cached_data.get("algorithm_type", "coverage"))
        trajectory = Trajectory(
            wall_id=wall_id,
            name=f"Cached {algorithm_type.value.upper()} Path",
            algorithm_type=algorithm_type,
            status=TrajectoryStatus.PLANNED,
            waypoints=cached_data["waypoints"],
            total_distance=cached_data["metrics"]["total_distance"],
            coverage_percentage=cached_data["metrics"]["coverage"],
            planning_time=cached_data["metrics"]["planning_time"]
        )
        db.add(trajectory)
        db.commit()
        db.refresh(trajectory)
        return trajectory

    def get_trajectory(self, db: Session, trajectory_id: int) -> Optional[Trajectory]:
        """Get trajectory by ID"""
        return db.query(Trajectory).filter(Trajectory.id == trajectory_id).first()

    def get_trajectories(self, db: Session, wall_id: Optional[int] = None,
                        skip: int = 0, limit: int = 100) -> List[Trajectory]:
        """Get trajectories"""
        query = db.query(Trajectory)
        if wall_id:
            query = query.filter(Trajectory.wall_id == wall_id)
        return query.offset(skip).limit(limit).all()
