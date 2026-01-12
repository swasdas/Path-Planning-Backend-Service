"""Geometry utilities for obstacle handling"""
import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry
from typing import List, Tuple
from app.models.obstacle import ObstacleType

def create_shape(obstacle_data: dict) -> BaseGeometry:
    """Create a Shapely geometry from obstacle data"""
    obstacle_type = obstacle_data.get("obstacle_type")
    x = obstacle_data.get("x", 0)
    y = obstacle_data.get("y", 0)

    # Handle both string and enum types
    if isinstance(obstacle_type, str):
        obstacle_type = obstacle_type.lower()

    if obstacle_type == ObstacleType.RECTANGLE or obstacle_type == "rectangle":
        width = obstacle_data.get("width", 0)
        height = obstacle_data.get("height", 0)
        # Create rectangle from CENTER point (x, y)
        return box(x - width/2, y - height/2, x + width/2, y + height/2)

    elif obstacle_type == ObstacleType.CIRCLE or obstacle_type == "circle":
        radius = obstacle_data.get("radius", 0)
        # Create circle as polygon with many sides (x, y is CENTER)
        center = Point(x, y)
        return center.buffer(radius, resolution=16)

    elif obstacle_type == ObstacleType.POLYGON or obstacle_type == "polygon":
        vertices = obstacle_data.get("vertices", [])
        if len(vertices) < 3:
            raise ValueError("Polygon must have at least 3 vertices")
        return Polygon(vertices)

    else:
        raise ValueError(f"Unknown obstacle type: {obstacle_type}")

def point_in_shape(point: Tuple[float, float], shape: BaseGeometry) -> bool:
    """Check if a point is inside a shape"""
    return shape.contains(Point(point))

def distance_to_shape(point: Tuple[float, float], shape: BaseGeometry) -> float:
    """Calculate distance from point to shape"""
    return shape.distance(Point(point))

def grid_cells_in_shape(shape: BaseGeometry, grid_resolution: float,
                        wall_width: float, wall_height: float) -> List[Tuple[int, int]]:
    """Get all grid cells that intersect with a shape"""
    cells = []
    minx, miny, maxx, maxy = shape.bounds

    # Convert to grid coordinates
    min_col = max(0, int(minx / grid_resolution))
    min_row = max(0, int(miny / grid_resolution))
    max_col = min(int(wall_width / grid_resolution), int(maxx / grid_resolution) + 1)
    max_row = min(int(wall_height / grid_resolution), int(maxy / grid_resolution) + 1)

    for row in range(min_row, max_row):
        for col in range(min_col, max_col):
            # Check if cell center is inside shape
            cell_center_x = (col + 0.5) * grid_resolution
            cell_center_y = (row + 0.5) * grid_resolution
            if shape.contains(Point(cell_center_x, cell_center_y)):
                cells.append((row, col))

    return cells

def calculate_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_path_length(waypoints: List[dict]) -> float:
    """Calculate total path length"""
    if len(waypoints) < 2:
        return 0.0

    total = 0.0
    for i in range(len(waypoints) - 1):
        p1 = (waypoints[i]["x"], waypoints[i]["y"])
        p2 = (waypoints[i + 1]["x"], waypoints[i + 1]["y"])
        total += calculate_distance(p1, p2)

    return total
