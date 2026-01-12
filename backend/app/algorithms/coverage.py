"""Boustrophedon (lawn-mower) coverage path planning"""
from typing import List, Tuple, Dict
from app.algorithms.grid import GridManager
from app.algorithms.astar import AStarPlanner

class CoveragePlanner:
    """Implements boustrophedon coverage algorithm"""

    def __init__(self, grid: GridManager):
        self.grid = grid

    def plan(self, start_row: int = 0, start_col: int = 0) -> List[Dict[str, float]]:
        """
        Generate coverage path using boustrophedon pattern

        Args:
            start_row: Starting row
            start_col: Starting column

        Returns:
            List of waypoints as {x, y, z} dicts
        """
        waypoints = []
        visited = set()

        # Start from bottom-left, sweep right, then alternate
        current_row = start_row
        direction = 1  # 1 for right, -1 for left

        while current_row < self.grid.rows:
            # Determine column range based on direction
            if direction == 1:
                col_range = range(0, self.grid.cols)
            else:
                col_range = range(self.grid.cols - 1, -1, -1)

            # Sweep across the row
            row_has_free = False
            for col in col_range:
                if self.grid.is_free(current_row, col):
                    row_has_free = True
                    if (current_row, col) not in visited:
                        x, y = self.grid.grid_to_world(current_row, col)
                        waypoints.append({"x": x, "y": y, "z": 0.0})
                        visited.add((current_row, col))

            # Move to next row
            current_row += 1
            direction *= -1  # Alternate direction

            # If no free cells found in this row, try to find next valid row
            if not row_has_free:
                while current_row < self.grid.rows:
                    if any(self.grid.is_free(current_row, c) for c in range(self.grid.cols)):
                        break
                    current_row += 1

        return waypoints

    def plan_with_obstacles(self) -> List[Dict[str, float]]:
        """
        Generate coverage path handling obstacles by splitting into sections
        and using A* to navigate around obstacles

        Returns:
            List of waypoints as {x, y, z} dicts
        """
        waypoints = []
        visited = set()
        astar = AStarPlanner(self.grid)

        for row in range(self.grid.rows):
            # Find continuous free segments in this row
            segments = self._find_free_segments(row)

            # Alternate direction for each row
            if row % 2 == 1:
                segments.reverse()

            for segment_start, segment_end in segments:
                # Collect waypoints for this segment
                segment_waypoints = []

                if row % 2 == 0:
                    # Left to right
                    for col in range(segment_start, segment_end + 1):
                        if (row, col) not in visited and self.grid.is_free(row, col):
                            x, y = self.grid.grid_to_world(row, col)
                            segment_waypoints.append({"x": x, "y": y, "z": 0.0})
                            visited.add((row, col))
                else:
                    # Right to left
                    for col in range(segment_end, segment_start - 1, -1):
                        if (row, col) not in visited and self.grid.is_free(row, col):
                            x, y = self.grid.grid_to_world(row, col)
                            segment_waypoints.append({"x": x, "y": y, "z": 0.0})
                            visited.add((row, col))

                # If there are existing waypoints and we have new segment waypoints,
                # connect them using A* if obstacle is in the way
                if waypoints and segment_waypoints:
                    last_point = waypoints[-1]
                    next_point = segment_waypoints[0]

                    # Check if we need to navigate around obstacle
                    if self._needs_navigation(last_point, next_point):
                        # Use A* to find path around obstacle
                        start_grid = self.grid.world_to_grid(last_point["x"], last_point["y"])
                        end_grid = self.grid.world_to_grid(next_point["x"], next_point["y"])

                        # A* might return empty list if no path found
                        connecting_path = astar.plan(start_grid, end_grid)

                        # Add connecting path, excluding start (already in waypoints) and end (in segment_waypoints)
                        if connecting_path and len(connecting_path) > 2:
                            waypoints.extend(connecting_path[1:-1])

                # Add all segment waypoints
                waypoints.extend(segment_waypoints)

        return waypoints

    def _find_free_segments(self, row: int) -> List[Tuple[int, int]]:
        """Find continuous free segments in a row"""
        segments = []
        start = None

        for col in range(self.grid.cols):
            if self.grid.is_free(row, col):
                if start is None:
                    start = col
            else:
                if start is not None:
                    segments.append((start, col - 1))
                    start = None

        # Add final segment if row ends with free cells
        if start is not None:
            segments.append((start, self.grid.cols - 1))

        return segments

    def _needs_navigation(self, point1: Dict[str, float], point2: Dict[str, float]) -> bool:
        """
        Check if direct path between points crosses an obstacle
        Uses line-of-sight check by sampling points along the line

        Args:
            point1: Start point {x, y, z}
            point2: End point {x, y, z}

        Returns:
            True if obstacle is in the way, False otherwise
        """
        x1, y1 = point1["x"], point1["y"]
        x2, y2 = point2["x"], point2["y"]

        # Calculate number of steps based on distance and grid resolution
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        steps = max(int(distance / self.grid.resolution) + 1, 2)

        # Sample points along the line
        for i in range(steps + 1):
            t = i / steps
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            # Check if this point is in an obstacle
            row, col = self.grid.world_to_grid(x, y)
            if self.grid.is_valid(row, col) and not self.grid.is_free(row, col):
                return True  # Obstacle detected in path

        return False  # Clear path
