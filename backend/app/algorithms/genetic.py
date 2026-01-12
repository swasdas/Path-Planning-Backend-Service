"""Genetic Algorithm for path optimization"""
import random
import numpy as np
from typing import List, Dict, Tuple
from app.algorithms.grid import GridManager
from app.algorithms.geometry import calculate_path_length

class GeneticOptimizer:
    """Genetic algorithm to optimize path order"""

    def __init__(self, grid: GridManager, population_size: int = 50,
                 generations: int = 30, mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8):
        self.grid = grid
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate

    def optimize(self, waypoints: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """
        Optimize waypoint order using genetic algorithm

        Args:
            waypoints: Initial waypoints

        Returns:
            Optimized waypoints
        """
        if len(waypoints) <= 2:
            return waypoints

        # Deduplicate input waypoints first (coverage planner might generate duplicates with A* paths)
        waypoints = self._deduplicate_waypoints(waypoints)

        # Handle edge cases
        if not waypoints or len(waypoints) <= 2:
            return waypoints if waypoints else []

        # Keep first and last waypoints fixed
        fixed_start = waypoints[0]
        fixed_end = waypoints[-1]
        optimizable = waypoints[1:-1]

        if len(optimizable) <= 1:
            return waypoints

        # Initialize population with random permutations
        population = self._initialize_population(optimizable)

        best_fitness = float('-inf')
        best_individual = None

        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = [self._fitness(ind, fixed_start, fixed_end) for ind in population]

            # Track best
            max_fitness_idx = np.argmax(fitness_scores)
            if fitness_scores[max_fitness_idx] > best_fitness:
                best_fitness = fitness_scores[max_fitness_idx]
                best_individual = population[max_fitness_idx].copy()

            # Selection
            selected = self._selection(population, fitness_scores)

            # Create next generation
            next_generation = []

            # Elitism - keep best individual
            next_generation.append(best_individual.copy())

            while len(next_generation) < self.population_size:
                parent1 = random.choice(selected)
                parent2 = random.choice(selected)

                if random.random() < self.crossover_rate:
                    child = self._crossover(parent1, parent2)
                else:
                    child = parent1.copy()

                if random.random() < self.mutation_rate:
                    child = self._mutate(child)

                next_generation.append(child)

            population = next_generation

        # Return best solution with deduplication
        # Safety check: if no valid solution found, return original waypoints
        if best_individual is None:
            return waypoints

        optimized_path = [fixed_start] + best_individual + [fixed_end]
        return self._deduplicate_waypoints(optimized_path)

    def _initialize_population(self, waypoints: List[Dict]) -> List[List[Dict]]:
        """Create initial population with random permutations"""
        population = []
        for _ in range(self.population_size):
            individual = waypoints.copy()
            random.shuffle(individual)
            population.append(individual)
        return population

    def _fitness(self, individual: List[Dict], start: Dict, end: Dict) -> float:
        """
        Calculate fitness score for an individual
        Higher is better - balances short distance with smooth turns
        """
        # Construct full path
        full_path = [start] + individual + [end]

        # Calculate total distance (lower is better)
        distance = calculate_path_length(full_path)

        if distance == 0:
            return 0

        # Calculate smoothness (total angle change in radians)
        total_angle_change = self._calculate_smoothness(full_path)

        # Normalize smoothness to [0, 1] range where 1 = perfectly smooth
        # Max possible angle change per turn = π radians, N-2 turns for N points
        max_possible_angle = max(len(full_path) - 2, 1) * 3.14159
        normalized_smoothness = max(0, 1 - (total_angle_change / max_possible_angle))

        # Balance distance and smoothness
        # Distance weight: 10000 (shorter paths get higher scores)
        # Smoothness weight: 5000 (smoother paths get bonus)
        # This means smoothness can contribute up to 33% of fitness
        fitness = (10000.0 / distance) + (normalized_smoothness * 5000)

        return fitness

    def _calculate_smoothness(self, path: List[Dict]) -> float:
        """
        Calculate total angle change along the path in radians
        Lower value = smoother path (fewer/gentler turns)

        Returns:
            Total angle change in radians
        """
        if len(path) < 3:
            return 0.0

        total_angle_change = 0.0

        for i in range(1, len(path) - 1):
            # Calculate vectors for segments before and after this point
            v1 = np.array([path[i]["x"] - path[i-1]["x"],
                          path[i]["y"] - path[i-1]["y"]])
            v2 = np.array([path[i+1]["x"] - path[i]["x"],
                          path[i+1]["y"] - path[i]["y"]])

            # Get vector magnitudes
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            # Only calculate angle if both vectors have length
            if norm1 > 1e-6 and norm2 > 1e-6:
                # Normalize vectors
                v1 = v1 / norm1
                v2 = v2 / norm2

                # Calculate angle using dot product (range: 0 to π radians)
                cos_angle = np.clip(np.dot(v1, v2), -1.0, 1.0)
                angle = np.arccos(cos_angle)
                total_angle_change += angle

        return total_angle_change

    def _selection(self, population: List[List[Dict]], fitness_scores: List[float]) -> List[List[Dict]]:
        """Tournament selection"""
        selected = []
        tournament_size = 3

        for _ in range(len(population) // 2):
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[np.argmax(tournament_fitness)]
            selected.append(population[winner_idx])

        return selected

    def _crossover(self, parent1: List[Dict], parent2: List[Dict]) -> List[Dict]:
        """
        Ordered crossover (OX)
        Note: Uses object identity for crossover. Deduplication by coordinates
        happens at the input/output stages, not during genetic operations.
        """
        size = len(parent1)
        if size <= 2:
            return parent1.copy()

        # Select two crossover points
        point1 = random.randint(0, size - 2)
        point2 = random.randint(point1 + 1, size)

        # Create child
        child = [None] * size

        # Copy segment from parent1
        child[point1:point2] = parent1[point1:point2]

        # Create a set of items already in child (by object identity)
        in_child = set(id(item) for item in child if item is not None)

        # Fill remaining positions from parent2
        child_idx = point2 % size
        for item in parent2[point2:] + parent2[:point2]:
            # Use object identity for comparison during crossover
            if id(item) not in in_child:
                child[child_idx] = item
                in_child.add(id(item))
                child_idx = (child_idx + 1) % size

        return child

    def _mutate(self, individual: List[Dict]) -> List[Dict]:
        """Swap mutation"""
        if len(individual) <= 1:
            return individual

        mutated = individual.copy()
        idx1, idx2 = random.sample(range(len(mutated)), 2)
        mutated[idx1], mutated[idx2] = mutated[idx2], mutated[idx1]

        return mutated

    def _deduplicate_waypoints(self, waypoints: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """
        Remove duplicate waypoints by coordinates

        Args:
            waypoints: List of waypoints

        Returns:
            List of unique waypoints
        """
        if not waypoints:
            return waypoints

        seen = set()
        unique = []

        for wp in waypoints:
            # Round to 1mm precision to handle floating point errors
            coord = (round(wp["x"], 3), round(wp["y"], 3))
            if coord not in seen:
                seen.add(coord)
                unique.append(wp)

        return unique
