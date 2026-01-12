"""Hybrid planner combining coverage, A*, and genetic algorithms"""
from typing import List, Dict
from app.algorithms.grid import GridManager
from app.algorithms.coverage import CoveragePlanner
from app.algorithms.astar import AStarPlanner
from app.algorithms.genetic import GeneticOptimizer

class HybridPlanner:
    """Combines multiple algorithms for optimal path planning"""

    def __init__(self, grid: GridManager, ga_params: dict = None):
        self.grid = grid
        self.coverage = CoveragePlanner(grid)
        self.astar = AStarPlanner(grid)

        # Genetic algorithm parameters
        ga_params = ga_params or {}
        self.genetic = GeneticOptimizer(
            grid,
            population_size=ga_params.get("population_size", 50),
            generations=ga_params.get("generations", 30),
            mutation_rate=ga_params.get("mutation_rate", 0.1),
            crossover_rate=ga_params.get("crossover_rate", 0.8)
        )

    def plan(self) -> List[Dict[str, float]]:
        """
        Generate optimal path using hybrid approach:
        1. Use coverage planner for full coverage
        2. Identify disconnected sections
        3. Use A* to connect sections
        4. Use genetic algorithm to optimize order

        Returns:
            List of optimized waypoints
        """
        # Step 1: Generate coverage path with obstacles
        coverage_waypoints = self.coverage.plan_with_obstacles()

        if not coverage_waypoints:
            return []

        # Step 2: Identify gaps and connect with A*
        connected_waypoints = self._connect_gaps(coverage_waypoints)

        # Step 3: Optimize with genetic algorithm if enough waypoints
        if len(connected_waypoints) > 10:
            optimized_waypoints = self.genetic.optimize(connected_waypoints)
            return optimized_waypoints
        else:
            return connected_waypoints

    def _connect_gaps(self, waypoints: List[Dict]) -> List[Dict]:
        """Connect gaps in coverage path using A*"""
        if len(waypoints) <= 1:
            return waypoints

        connected = [waypoints[0]]
        threshold = self.grid.resolution * 3  # Max gap before using A*

        for i in range(1, len(waypoints)):
            prev = waypoints[i - 1]
            curr = waypoints[i]

            # Calculate distance
            dx = curr["x"] - prev["x"]
            dy = curr["y"] - prev["y"]
            distance = (dx * dx + dy * dy) ** 0.5

            # If gap is large, use A* to connect
            if distance > threshold:
                prev_grid = self.grid.world_to_grid(prev["x"], prev["y"])
                curr_grid = self.grid.world_to_grid(curr["x"], curr["y"])

                astar_path = self.astar.plan(prev_grid, curr_grid)
                if astar_path:
                    # Add A* path (excluding first point which is already in connected)
                    connected.extend(astar_path[1:])
                else:
                    # If A* fails, just add current point
                    connected.append(curr)
            else:
                connected.append(curr)

        return connected

    def plan_simple(self) -> List[Dict[str, float]]:
        """
        Simplified planning without genetic optimization
        Faster but potentially less optimal
        """
        coverage_waypoints = self.coverage.plan_with_obstacles()
        if not coverage_waypoints:
            return []

        return self._connect_gaps(coverage_waypoints)
