"""A* pathfinding algorithm"""
import heapq
from typing import List, Tuple, Dict, Optional
from app.algorithms.grid import GridManager
import math

class AStarPlanner:
    """Implements A* pathfinding algorithm"""

    def __init__(self, grid: GridManager):
        self.grid = grid

    def plan(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Dict[str, float]]:
        """
        Find shortest path from start to goal using A*

        Args:
            start: Starting grid cell (row, col)
            goal: Goal grid cell (row, col)

        Returns:
            List of waypoints as {x, y, z} dicts
        """
        if not self.grid.is_free(*start) or not self.grid.is_free(*goal):
            return []

        # Priority queue: (f_score, counter, node)
        open_set = []
        counter = 0
        heapq.heappush(open_set, (0, counter, start))

        # Track where we came from
        came_from = {}

        # Cost from start
        g_score = {start: 0}

        # Estimated total cost
        f_score = {start: self._heuristic(start, goal)}

        while open_set:
            current_f, _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current)

            for neighbor in self.grid.get_neighbors(*current, diagonal=True):
                # Calculate tentative g_score
                tentative_g = g_score[current] + self._cost(current, neighbor)

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    # This path is better
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self._heuristic(neighbor, goal)
                    f_score[neighbor] = f

                    counter += 1
                    heapq.heappush(open_set, (f, counter, neighbor))

        # No path found
        return []

    def _heuristic(self, node: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Euclidean distance heuristic"""
        dr = abs(node[0] - goal[0])
        dc = abs(node[1] - goal[1])
        return math.sqrt(dr * dr + dc * dc)

    def _cost(self, node1: Tuple[int, int], node2: Tuple[int, int]) -> float:
        """Cost to move from node1 to node2"""
        # Diagonal moves cost sqrt(2), orthogonal moves cost 1
        dr = abs(node1[0] - node2[0])
        dc = abs(node1[1] - node2[1])
        if dr + dc == 2:  # Diagonal
            return math.sqrt(2)
        return 1.0

    def _reconstruct_path(self, came_from: dict, current: Tuple[int, int]) -> List[Dict[str, float]]:
        """Reconstruct path from came_from dictionary"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()

        # Convert to waypoints
        waypoints = []
        for row, col in path:
            x, y = self.grid.grid_to_world(row, col)
            waypoints.append({"x": x, "y": y, "z": 0.0})

        return waypoints

    def find_nearest_free_cell(self, target: Tuple[int, int], max_search_radius: int = 10) -> Optional[Tuple[int, int]]:
        """Find nearest free cell to target"""
        if self.grid.is_free(*target):
            return target

        # Search in expanding circles
        for radius in range(1, max_search_radius + 1):
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    row, col = target[0] + dr, target[1] + dc
                    if self.grid.is_valid(row, col) and self.grid.is_free(row, col):
                        return (row, col)

        return None
