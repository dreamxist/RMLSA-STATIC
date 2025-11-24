"""
Genetic Algorithm for Static RMLSA Optimization.

This module implements a genetic algorithm to find near-optimal solutions
for the static Routing, Modulation Level, and Spectrum Assignment (RMLSA) problem.
"""
import random
import numpy as np
from typing import List, Dict, Tuple
import networkx as nx

from ..core.solution import Solution, Assignment, create_empty_solution
from ..algorithms.sp_ff import sp_ff_assign
from ..core.routing import get_path_info
from data.modulation import calculate_required_slots


class GeneticAlgorithm:
    """
    Genetic Algorithm for optimizing static RMLSA solutions.

    The GA evolves a population of complete solutions through selection,
    crossover, and mutation operations to minimize spectrum usage.
    """

    def __init__(
        self,
        network,
        demands: List[Dict],
        population_size: int = 50,
        generations: int = 100,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.2,
        elite_size: int = 2,
        k_paths: int = 3,
        tournament_size: int = 3
    ):
        """
        Initialize the Genetic Algorithm.

        Args:
            network: Network instance
            demands: List of demand dictionaries
            population_size: Number of solutions in population
            generations: Number of generations to evolve
            crossover_rate: Probability of crossover
            mutation_rate: Probability of mutation
            elite_size: Number of best solutions to preserve (elitism)
            k_paths: Number of candidate paths to consider per demand
            tournament_size: Size of tournament for selection
        """
        self.network = network
        self.demands = demands
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.k_paths = k_paths
        self.tournament_size = tournament_size

        # Pre-compute k-shortest paths for each demand
        self.candidate_paths = self._compute_candidate_paths()

        # Evolution history
        self.best_fitness_history = []
        self.avg_fitness_history = []

    def _calculate_num_slots(self, path, demand):
        """
        Calculate number of slots needed for a demand on a specific path.

        Args:
            path: List of nodes forming the path
            demand: Demand dictionary with bandwidth

        Returns:
            Number of slots needed, or None if path is too long
        """
        path_info = get_path_info(self.network.topology, path)
        distance = path_info['distance']
        num_slots, _ = calculate_required_slots(demand['bandwidth'], distance)
        return num_slots

    def _compute_candidate_paths(self) -> Dict[int, List[List[int]]]:
        """
        Pre-compute k-shortest paths for each demand.

        Returns:
            Dictionary mapping demand index to list of candidate paths
        """
        candidate_paths = {}

        for idx, demand in enumerate(self.demands):
            source = demand['source']
            destination = demand['destination']

            try:
                # Compute k-shortest paths using networkx
                paths = list(nx.shortest_simple_paths(
                    self.network.topology,
                    source,
                    destination
                ))
                # Limit to k paths
                candidate_paths[idx] = paths[:self.k_paths]
            except nx.NetworkXNoPath:
                # No path exists
                candidate_paths[idx] = []

        return candidate_paths

    def _create_random_solution(self) -> Solution:
        """
        Create a random valid solution.

        Strategy:
        1. Shuffle demand order
        2. For each demand, try random path and random starting slot
        3. Use first-fit if random fails

        Returns:
            A Solution object (may not be complete if resources insufficient)
        """
        solution = create_empty_solution(self.network, self.demands)
        temp_network = self.network.__class__(
            self.network.topology,
            self.network.num_slots
        )

        # Random order
        demand_indices = list(range(len(self.demands)))
        random.shuffle(demand_indices)

        for idx in demand_indices:
            demand = self.demands[idx]
            paths = self.candidate_paths[idx]

            if not paths:
                continue

            assigned = False

            # Try random path
            path = random.choice(paths)
            num_slots = self._calculate_num_slots(path, demand)

            if num_slots is None:
                continue

            # Try random starting slot
            max_start = temp_network.num_slots - num_slots
            if max_start > 0:
                # Try a few random positions
                for _ in range(5):
                    start_slot = random.randint(0, max_start)
                    if temp_network.is_spectrum_available(path, start_slot, num_slots):
                        temp_network.allocate_spectrum(path, start_slot, num_slots)
                        solution.set_assignment(idx, Assignment(idx, path, start_slot, num_slots))
                        assigned = True
                        break

            # If random failed, try first-fit
            if not assigned:
                for start_slot in range(temp_network.num_slots - num_slots + 1):
                    if temp_network.is_spectrum_available(path, start_slot, num_slots):
                        temp_network.allocate_spectrum(path, start_slot, num_slots)
                        solution.set_assignment(idx, Assignment(idx, path, start_slot, num_slots))
                        break

        return solution

    def _create_greedy_solution(self) -> Solution:
        """
        Create a solution using First-Fit greedy heuristic.

        Returns:
            Solution created by greedy algorithm
        """
        solution = create_empty_solution(self.network, self.demands)
        temp_network = self.network.__class__(
            self.network.topology,
            self.network.num_slots
        )

        # Sort demands by bandwidth (descending)
        sorted_indices = sorted(
            range(len(self.demands)),
            key=lambda i: self.demands[i]['bandwidth'],
            reverse=True
        )

        for idx in sorted_indices:
            demand = self.demands[idx]
            result = sp_ff_assign(temp_network, demand)

            if result:
                path = result['path']
                start_slot = result['start_slot']
                num_slots = result['num_slots']
                solution.set_assignment(idx, Assignment(idx, path, start_slot, num_slots))

        return solution

    def _initialize_population(self) -> List[Solution]:
        """
        Create initial population.

        Mix of:
        - Greedy solution (First-Fit)
        - Random solutions

        Returns:
            List of Solution objects
        """
        population = []

        # Add greedy solution
        population.append(self._create_greedy_solution())

        # Fill rest with random solutions
        while len(population) < self.population_size:
            population.append(self._create_random_solution())

        return population

    def _tournament_selection(self, population: List[Solution]) -> Solution:
        """
        Select a solution using tournament selection.

        Args:
            population: Current population

        Returns:
            Selected solution
        """
        tournament = random.sample(population, self.tournament_size)
        return min(tournament, key=lambda s: s.calculate_fitness())

    def _crossover(self, parent1: Solution, parent2: Solution) -> Tuple[Solution, Solution]:
        """
        Perform crossover between two parent solutions.

        Strategy: Uniform crossover at demand level
        - For each demand, randomly inherit assignment from parent1 or parent2
        - Repair conflicts by reassigning conflicting demands

        Args:
            parent1: First parent solution
            parent2: Second parent solution

        Returns:
            Tuple of two offspring solutions
        """
        offspring1 = create_empty_solution(self.network, self.demands)
        offspring2 = create_empty_solution(self.network, self.demands)

        # Uniform crossover
        for idx in range(len(self.demands)):
            if random.random() < 0.5:
                # Offspring1 inherits from parent1, offspring2 from parent2
                if parent1.assignments[idx]:
                    offspring1.set_assignment(idx, parent1.assignments[idx].copy())
                if parent2.assignments[idx]:
                    offspring2.set_assignment(idx, parent2.assignments[idx].copy())
            else:
                # Offspring1 inherits from parent2, offspring2 from parent1
                if parent2.assignments[idx]:
                    offspring1.set_assignment(idx, parent2.assignments[idx].copy())
                if parent1.assignments[idx]:
                    offspring2.set_assignment(idx, parent1.assignments[idx].copy())

        # Repair conflicts
        self._repair_solution(offspring1)
        self._repair_solution(offspring2)

        return offspring1, offspring2

    def _repair_solution(self, solution: Solution):
        """
        Repair a solution to resolve spectrum conflicts.

        Strategy:
        1. Validate solution to find conflicts
        2. Remove conflicting assignments
        3. Reassign using greedy approach

        Args:
            solution: Solution to repair (modified in place)
        """
        is_valid, errors = solution.validate()

        if is_valid:
            return

        # Build temporary network with current assignments
        temp_network = self.network.__class__(
            self.network.topology,
            self.network.num_slots
        )

        # Track which demands to reassign
        conflicting_demands = set()

        # Apply all assignments and detect conflicts
        for idx, assignment in enumerate(solution.assignments):
            if assignment is None:
                continue

            if not temp_network.is_spectrum_available(
                assignment.path,
                assignment.start_slot,
                assignment.num_slots
            ):
                conflicting_demands.add(idx)
            else:
                temp_network.allocate_spectrum(
                    assignment.path,
                    assignment.start_slot,
                    assignment.num_slots
                )

        # Remove conflicting assignments
        for idx in conflicting_demands:
            solution.set_assignment(idx, None)

        # Reassign conflicting demands using first-fit
        for idx in conflicting_demands:
            demand = self.demands[idx]
            paths = self.candidate_paths[idx]

            for path in paths:
                num_slots = self._calculate_num_slots(path, demand)
                if num_slots is None:
                    continue

                for start_slot in range(temp_network.num_slots - num_slots + 1):
                    if temp_network.is_spectrum_available(path, start_slot, num_slots):
                        temp_network.allocate_spectrum(path, start_slot, num_slots)
                        solution.set_assignment(idx, Assignment(idx, path, start_slot, num_slots))
                        break
                if solution.assignments[idx] is not None:
                    break

    def _mutate(self, solution: Solution):
        """
        Mutate a solution.

        Mutation operators:
        1. Change route for a demand
        2. Shift spectrum allocation
        3. Reassign random demand

        Args:
            solution: Solution to mutate (modified in place)
        """
        # Choose mutation operator
        operator = random.choice(['change_route', 'shift_spectrum', 'reassign'])

        if operator == 'change_route':
            self._mutate_change_route(solution)
        elif operator == 'shift_spectrum':
            self._mutate_shift_spectrum(solution)
        else:
            self._mutate_reassign(solution)

    def _mutate_change_route(self, solution: Solution):
        """Change the route for a random demand."""
        # Pick a random assigned demand
        assigned_indices = [i for i, a in enumerate(solution.assignments) if a is not None]
        if not assigned_indices:
            return

        idx = random.choice(assigned_indices)
        paths = self.candidate_paths[idx]

        if len(paths) <= 1:
            return

        current_assignment = solution.assignments[idx]

        # Try a different path
        other_paths = [p for p in paths if p != current_assignment.path]
        if not other_paths:
            return

        new_path = random.choice(other_paths)

        # Remove current assignment
        solution.set_assignment(idx, None)

        # Build temp network without this demand
        temp_network = self.network.__class__(self.network.topology, self.network.num_slots)
        for i, a in enumerate(solution.assignments):
            if a is not None and i != idx:
                temp_network.allocate_spectrum(a.path, a.start_slot, a.num_slots)

        # Try to assign with new path
        demand = self.demands[idx]
        num_slots = self._calculate_num_slots(new_path, demand)
        if num_slots is None:
            return

        for start_slot in range(temp_network.num_slots - num_slots + 1):
            if temp_network.is_spectrum_available(new_path, start_slot, num_slots):
                solution.set_assignment(idx, Assignment(idx, new_path, start_slot, num_slots))
                break

    def _mutate_shift_spectrum(self, solution: Solution):
        """Shift the spectrum allocation for a random demand."""
        assigned_indices = [i for i, a in enumerate(solution.assignments) if a is not None]
        if not assigned_indices:
            return

        idx = random.choice(assigned_indices)
        current_assignment = solution.assignments[idx]

        # Remove current assignment
        solution.set_assignment(idx, None)

        # Build temp network
        temp_network = self.network.__class__(self.network.topology, self.network.num_slots)
        for i, a in enumerate(solution.assignments):
            if a is not None:
                temp_network.allocate_spectrum(a.path, a.start_slot, a.num_slots)

        # Try different starting slots
        num_slots = current_assignment.num_slots
        possible_slots = list(range(temp_network.num_slots - num_slots + 1))
        random.shuffle(possible_slots)

        for start_slot in possible_slots[:10]:  # Try up to 10 random positions
            if temp_network.is_spectrum_available(current_assignment.path, start_slot, num_slots):
                solution.set_assignment(
                    idx,
                    Assignment(idx, current_assignment.path, start_slot, num_slots)
                )
                break

    def _mutate_reassign(self, solution: Solution):
        """Completely reassign a random demand."""
        # Pick random demand (assigned or not)
        idx = random.randint(0, len(self.demands) - 1)

        # Remove if assigned
        solution.set_assignment(idx, None)

        # Build temp network
        temp_network = self.network.__class__(self.network.topology, self.network.num_slots)
        for i, a in enumerate(solution.assignments):
            if a is not None:
                temp_network.allocate_spectrum(a.path, a.start_slot, a.num_slots)

        # Reassign using greedy
        demand = self.demands[idx]
        paths = self.candidate_paths[idx]

        for path in paths:
            num_slots = self._calculate_num_slots(path, demand)
            if num_slots is None:
                continue

            for start_slot in range(temp_network.num_slots - num_slots + 1):
                if temp_network.is_spectrum_available(path, start_slot, num_slots):
                    temp_network.allocate_spectrum(path, start_slot, num_slots)
                    solution.set_assignment(idx, Assignment(idx, path, start_slot, num_slots))
                    return

    def optimize(self, verbose: bool = True) -> Solution:
        """
        Run the genetic algorithm optimization.

        Args:
            verbose: Whether to print progress

        Returns:
            Best solution found
        """
        if verbose:
            print(f"Genetic Algorithm: pop_size={self.population_size}, generations={self.generations}")

        # Initialize population
        population = self._initialize_population()

        # Evolution loop
        for generation in range(self.generations):
            # Evaluate fitness
            fitnesses = [sol.calculate_fitness() for sol in population]
            best_fitness = min(fitnesses)
            avg_fitness = np.mean([f for f in fitnesses if f != float('inf')])

            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)

            if verbose and generation % 10 == 0:
                best_sol = min(population, key=lambda s: s.calculate_fitness())
                print(
                    f"  Gen {generation:3d}: Best fitness={best_fitness:.0f}, "
                    f"Avg={avg_fitness:.0f}, Assigned={best_sol.get_assigned_count()}/{len(self.demands)}"
                )

            # Selection and reproduction
            new_population = []

            # Elitism: preserve best solutions
            population.sort(key=lambda s: s.calculate_fitness())
            new_population.extend([sol.copy() for sol in population[:self.elite_size]])

            # Generate offspring
            while len(new_population) < self.population_size:
                # Selection
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)

                # Crossover
                if random.random() < self.crossover_rate:
                    offspring1, offspring2 = self._crossover(parent1, parent2)
                else:
                    offspring1, offspring2 = parent1.copy(), parent2.copy()

                # Mutation
                if random.random() < self.mutation_rate:
                    self._mutate(offspring1)
                if random.random() < self.mutation_rate:
                    self._mutate(offspring2)

                new_population.append(offspring1)
                if len(new_population) < self.population_size:
                    new_population.append(offspring2)

            population = new_population

        # Return best solution
        best_solution = min(population, key=lambda s: s.calculate_fitness())

        if verbose:
            print(f"\nGA Complete: Best fitness={best_solution.calculate_fitness():.0f}")
            metrics = best_solution.get_metrics()
            print(f"  Assigned: {metrics['assigned_count']}/{metrics['total_demands']}")
            print(f"  Max slot used: {metrics['max_slot_used']}")
            print(f"  Total spectrum: {metrics['total_spectrum_consumption']}")

        return best_solution
