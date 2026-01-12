"""Grid representation and management for path planning"""
import numpy as np
from typing import List, Tuple, Optional
from app.algorithms.geometry import create_shape, grid_cells_in_shape

class GridManager:
    """Manages grid representation of wall and obstacles"""

    def __init__(self, width: float, height: float, resolution: float = 0.1):
        """
        Initialize grid manager

        Args:
            width: Wall width in meters
            height: Wall height in meters
            resolution: Grid cell size in meters (default 0.1m = 10cm)
        """
        self.width = width
        self.height = height
        self.resolution = resolution

        # Calculate grid dimensions
        self.cols = int(np.ceil(width / resolution))
        self.rows = int(np.ceil(height / resolution))

        # Initialize grid (0 = free, 1 = occupied)
        self.grid = np.zeros((self.rows, self.cols), dtype=np.int8)

    def add_obstacles(self, obstacles: List[dict]):
        """Add obstacles to the grid"""
        for obstacle in obstacles:
            shape = create_shape(obstacle)
            occupied_cells = grid_cells_in_shape(
                shape, self.resolution, self.width, self.height
            )
            for row, col in occupied_cells:
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    self.grid[row, col] = 1

    def is_free(self, row: int, col: int) -> bool:
        """Check if a grid cell is free"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row, col] == 0
        return False

    def is_valid(self, row: int, col: int) -> bool:
        """Check if coordinates are within grid bounds"""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates"""
        col = int(x / self.resolution)
        row = int(y / self.resolution)
        return row, col

    def grid_to_world(self, row: int, col: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates (center of cell)"""
        x = (col + 0.5) * self.resolution
        y = (row + 0.5) * self.resolution
        return x, y

    def get_neighbors(self, row: int, col: int, diagonal: bool = True) -> List[Tuple[int, int]]:
        """Get valid free neighbors of a cell"""
        neighbors = []

        # 4-connectivity (up, down, left, right)
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # Add diagonal moves for 8-connectivity
        if diagonal:
            moves.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

        for dr, dc in moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid(new_row, new_col) and self.is_free(new_row, new_col):
                neighbors.append((new_row, new_col))

        return neighbors

    def get_free_cells(self) -> List[Tuple[int, int]]:
        """Get all free cells in the grid"""
        free_cells = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row, col] == 0:
                    free_cells.append((row, col))
        return free_cells

    def calculate_coverage(self, visited_cells: set) -> float:
        """Calculate coverage percentage"""
        total_free = np.sum(self.grid == 0)
        if total_free == 0:
            return 100.0
        return (len(visited_cells) / total_free) * 100.0

    def __repr__(self):
        return f"GridManager({self.rows}x{self.cols}, resolution={self.resolution}m)"
