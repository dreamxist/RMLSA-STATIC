"""
Simulated Annealing for Static RMLSA Optimization.

This module implements simulated annealing to find near-optimal solutions
for the static Routing, Modulation Level, and Spectrum Assignment (RMLSA) problem.
"""
import random
import math
import numpy as np
from typing import List, Dict
import networkx as nx

from ..core.solution import Solution, Assignment, create_empty_solution
from ..algorithms.ksp_mw import ksp_mw_assign
from ..core.routing import get_path_info
from data.modulation import calculate_required_slots


class SimulatedAnnealing:
    """
    Simulated Annealing for optimizing static RMLSA solutions.

    SA uses probabilistic acceptance of worse solutions to escape local optima,
    gradually reducing the acceptance probability (cooling) over time.
    """

    def __init__(
        self,
        network,
        demands: List[Dict],
        initial_temperature: float = 1000.0,
        final_temperature: float = 0.1,
        cooling_rate: float = 0.95,
        iterations_per_temp: int = 100,
        k_paths: int = 3
    ):
        """
        Initialize Simulated Annealing.

        Args:
            network: Network instance
            demands: List of demand dictionaries
            initial_temperature: Starting temperature
            final_temperature: Stopping temperature
            cooling_rate: Temperature reduction factor (geometric cooling)
            iterations_per_temp: Number of iterations at each temperature
            k_paths: Number of candidate paths to consider per demand
        """
        self.network = network
        self.demands = demands
        self.initial_temperature = initial_temperature
        self.final_temperature = final_temperature
        self.cooling_rate = cooling_rate
        self.iterations_per_temp = iterations_per_temp
        self.k_paths = k_paths

        # Pre-compute k-shortest paths
        self.candidate_paths = self._compute_candidate_paths()

        # Evolution history
        self.temperature_history = []
        self.best_fitness_history = []
        self.current_fitness_history = []
        self.acceptance_rate_history = []

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
        """Pre-compute k-shortest paths for each demand."""
        candidate_paths = {}

        for idx, demand in enumerate(self.demands):
            source = demand['source']
            destination = demand['destination']

            try:
                paths = list(nx.shortest_simple_paths(
                    self.network.topology,
                    source,
                    destination
                ))
                candidate_paths[idx] = paths[:self.k_paths]
            except nx.NetworkXNoPath:
                candidate_paths[idx] = []

        return candidate_paths

    def _create_initial_solution(self) -> Solution:
        """
        Create initial solution using greedy heuristic.

        Returns:
            Initial Solution
        """
        solution = create_empty_solution(self.network, self.demands)
        temp_network = self.network.__class__(
            self.network.topology,
            self.network.num_slots
        )

        # Sort demands by bandwidth (descending) for greedy construction
        sorted_indices = sorted(
            range(len(self.demands)),
            key=lambda i: self.demands[i]['bandwidth'],
            reverse=True
        )

        for idx in sorted_indices:
            demand = self.demands[idx]
            result = ksp_mw_assign(temp_network, demand, k=self.k_paths)

            if result:
                # Result is a dict with 'path', 'start_slot', 'num_slots', etc.
                path = result['path']
                start_slot = result['start_slot']
                num_slots = result['num_slots']
                solution.set_assignment(idx, Assignment(idx, path, start_slot, num_slots))

        return solution

    def _generate_neighbor(self, solution: Solution) -> Solution:
        """
        Generate a neighbor solution using local search operators.

        Neighborhood operators:
        1. Change route for one demand
        2. Shift spectrum allocation for one demand
        3. Swap spectrum allocations between two demands
        4. Reassign one demand completely

        Args:
            solution: Current solution

        Returns:
            Neighbor solution
        """
        neighbor = solution.copy()

        # Choose operator randomly
        operator = random.choice([
            'change_route',
            'shift_spectrum',
            'swap_assignments',
            'reassign'
        ])

        if operator == 'change_route':
            self._neighbor_change_route(neighbor)
        elif operator == 'shift_spectrum':
            self._neighbor_shift_spectrum(neighbor)
        elif operator == 'swap_assignments':
            self._neighbor_swap_assignments(neighbor)
        else:
            self._neighbor_reassign(neighbor)

        return neighbor

    def _neighbor_change_route(self, solution: Solution):
        """Change route for a random demand."""
        assigned_indices = [i for i, a in enumerate(solution.assignments) if a is not None]
        if not assigned_indices:
            return

        idx = random.choice(assigned_indices)
        paths = self.candidate_paths[idx]

        if len(paths) <= 1:
            return

        current_assignment = solution.assignments[idx]
        other_paths = [p for p in paths if p != current_assignment.path]
        if not other_paths:
            return

        new_path = random.choice(other_paths)

        # Build temp network without this demand
        temp_network = self.network.__class__(self.network.topology, self.network.num_slots)
        for i, a in enumerate(solution.assignments):
            if a is not None and i != idx:
                temp_network.allocate_spectrum(a.path, a.start_slot, a.num_slots)

        # Try to assign with new path
        solution.set_assignment(idx, None)
        demand = self.demands[idx]
        num_slots = self._calculate_num_slots(new_path, demand)

        if num_slots is None:
            return

        for start_slot in range(temp_network.num_slots - num_slots + 1):
            if temp_network.is_spectrum_available(new_path, start_slot, num_slots):
                solution.set_assignment(idx, Assignment(idx, new_path, start_slot, num_slots))
                return

    def _neighbor_shift_spectrum(self, solution: Solution):
        """Shift spectrum allocation for a random demand."""
        assigned_indices = [i for i, a in enumerate(solution.assignments) if a is not None]
        if not assigned_indices:
            return

        idx = random.choice(assigned_indices)
        current_assignment = solution.assignments[idx]

        # Build temp network without this demand
        temp_network = self.network.__class__(self.network.topology, self.network.num_slots)
        for i, a in enumerate(solution.assignments):
            if a is not None and i != idx:
                temp_network.allocate_spectrum(a.path, a.start_slot, a.num_slots)

        # Remove current
        solution.set_assignment(idx, None)

        # Try nearby slots (local search)
        num_slots = current_assignment.num_slots
        current_start = current_assignment.start_slot

        # Try slots within +/- 10 of current
        search_range = range(
            max(0, current_start - 10),
            min(temp_network.num_slots - num_slots + 1, current_start + 10)
        )

        for start_slot in search_range:
            if temp_network.is_spectrum_available(current_assignment.path, start_slot, num_slots):
                solution.set_assignment(
                    idx,
                    Assignment(idx, current_assignment.path, start_slot, num_slots)
                )
                return

    def _neighbor_swap_assignments(self, solution: Solution):
        """Swap spectrum slots between two demands (if compatible)."""
        assigned_indices = [i for i, a in enumerate(solution.assignments) if a is not None]
        if len(assigned_indices) < 2:
            return

        # Pick two random demands
        idx1, idx2 = random.sample(assigned_indices, 2)
        assign1 = solution.assignments[idx1]
        assign2 = solution.assignments[idx2]

        # Try to swap their spectrum allocations (keep paths, swap slots)
        # This only works if demands have same number of slots
        if assign1.num_slots != assign2.num_slots:
            return

        # Build temp network without these two demands
        temp_network = self.network.__class__(self.network.topology, self.network.num_slots)
        for i, a in enumerate(solution.assignments):
            if a is not None and i != idx1 and i != idx2:
                temp_network.allocate_spectrum(a.path, a.start_slot, a.num_slots)

        # Check if swap is feasible
        swap1_valid = temp_network.is_spectrum_available(
            assign1.path, assign2.start_slot, assign1.num_slots
        )
        swap2_valid = temp_network.is_spectrum_available(
            assign2.path, assign1.start_slot, assign2.num_slots
        )

        if swap1_valid and swap2_valid:
            # Perform swap
            solution.set_assignment(
                idx1,
                Assignment(idx1, assign1.path, assign2.start_slot, assign1.num_slots)
            )
            solution.set_assignment(
                idx2,
                Assignment(idx2, assign2.path, assign1.start_slot, assign2.num_slots)
            )

    def _neighbor_reassign(self, solution: Solution):
        """Completely reassign a random demand."""
        # Pick random demand
        idx = random.randint(0, len(self.demands) - 1)

        # Build temp network without this demand
        temp_network = self.network.__class__(self.network.topology, self.network.num_slots)
        for i, a in enumerate(solution.assignments):
            if a is not None and i != idx:
                temp_network.allocate_spectrum(a.path, a.start_slot, a.num_slots)

        # Remove current
        solution.set_assignment(idx, None)

        # Reassign using first-fit on random path
        demand = self.demands[idx]
        paths = self.candidate_paths[idx]

        if not paths:
            return

        path = random.choice(paths)

        # Calculate required slots based on path distance
        path_info = get_path_info(self.network.topology, path)
        distance = path_info['distance']
        num_slots, _ = calculate_required_slots(demand['bandwidth'], distance)

        if num_slots is None:
            return

        for start_slot in range(temp_network.num_slots - num_slots + 1):
            if temp_network.is_spectrum_available(path, start_slot, num_slots):
                temp_network.allocate_spectrum(path, start_slot, num_slots)
                solution.set_assignment(idx, Assignment(idx, path, start_slot, num_slots))
                return

    def _acceptance_probability(self, current_fitness: float, neighbor_fitness: float, temperature: float) -> float:
        """
        Calculate acceptance probability using Metropolis criterion.

        Args:
            current_fitness: Current solution fitness
            neighbor_fitness: Neighbor solution fitness
            temperature: Current temperature

        Returns:
            Acceptance probability [0, 1]
        """
        # Always accept better solutions
        if neighbor_fitness < current_fitness:
            return 1.0

        # Handle infinite fitness (infeasible solutions)
        if current_fitness == float('inf') or neighbor_fitness == float('inf'):
            return 0.0

        # Accept worse solutions with probability exp(-delta / T)
        delta = neighbor_fitness - current_fitness
        return math.exp(-delta / temperature)

    def optimize(self, verbose: bool = True) -> Solution:
        """
        Run simulated annealing optimization.

        Args:
            verbose: Whether to print progress

        Returns:
            Best solution found
        """
        if verbose:
            print(f"Simulated Annealing: T0={self.initial_temperature}, Tf={self.final_temperature}")

        # Initialize
        current_solution = self._create_initial_solution()
        current_fitness = current_solution.calculate_fitness()

        best_solution = current_solution.copy()
        best_fitness = current_fitness

        temperature = self.initial_temperature
        iteration = 0

        # Main SA loop
        while temperature > self.final_temperature:
            accepted_count = 0

            for _ in range(self.iterations_per_temp):
                # Generate neighbor
                neighbor = self._generate_neighbor(current_solution)
                neighbor_fitness = neighbor.calculate_fitness()

                # Acceptance decision
                accept_prob = self._acceptance_probability(
                    current_fitness,
                    neighbor_fitness,
                    temperature
                )

                if random.random() < accept_prob:
                    # Accept neighbor
                    current_solution = neighbor
                    current_fitness = neighbor_fitness
                    accepted_count += 1

                    # Update best
                    if current_fitness < best_fitness:
                        best_solution = current_solution.copy()
                        best_fitness = current_fitness

                iteration += 1

            # Record history
            acceptance_rate = accepted_count / self.iterations_per_temp
            self.temperature_history.append(temperature)
            self.best_fitness_history.append(best_fitness)
            self.current_fitness_history.append(current_fitness)
            self.acceptance_rate_history.append(acceptance_rate)

            if verbose and len(self.temperature_history) % 10 == 0:
                print(
                    f"  T={temperature:7.2f}: Best={best_fitness:.0f}, "
                    f"Current={current_fitness:.0f}, Accept={acceptance_rate:.2%}"
                )

            # Cool down
            temperature *= self.cooling_rate

        if verbose:
            print(f"\nSA Complete: Best fitness={best_fitness:.0f}")
            metrics = best_solution.get_metrics()
            print(f"  Assigned: {metrics['assigned_count']}/{metrics['total_demands']}")
            print(f"  Max slot used: {metrics['max_slot_used']}")
            print(f"  Total spectrum: {metrics['total_spectrum_consumption']}")

        return best_solution
