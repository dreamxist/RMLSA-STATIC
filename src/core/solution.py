"""
Solution representation for static RMLSA optimization.

In static RMLSA, a solution represents a complete assignment of all demands
to routes and spectrum slots. This module provides the Solution class and
related utilities for representing, validating, and evaluating solutions.
"""
import copy
import numpy as np
from typing import List, Dict, Tuple, Optional


class Assignment:
    """
    Represents the assignment of a single demand.

    Attributes:
        demand_id: Identifier for the demand
        path: List of nodes forming the route
        start_slot: Starting spectrum slot index
        num_slots: Number of contiguous slots allocated
    """

    def __init__(self, demand_id: int, path: List[int], start_slot: int, num_slots: int):
        self.demand_id = demand_id
        self.path = path
        self.start_slot = start_slot
        self.num_slots = num_slots

    @property
    def end_slot(self):
        """End slot index (exclusive)."""
        return self.start_slot + self.num_slots

    def __repr__(self):
        return f"Assignment(demand={self.demand_id}, path={self.path}, slots={self.start_slot}-{self.end_slot})"

    def copy(self):
        """Create a deep copy of this assignment."""
        return Assignment(
            demand_id=self.demand_id,
            path=self.path.copy(),
            start_slot=self.start_slot,
            num_slots=self.num_slots
        )


class Solution:
    """
    Represents a complete solution for static RMLSA.

    A solution consists of assignments for all (or subset of) demands.
    For true static RMLSA, all demands should be assigned.
    """

    def __init__(self, network, demands: List[Dict]):
        """
        Initialize a solution.

        Args:
            network: Network instance
            demands: List of demand dictionaries
        """
        self.network = network
        self.demands = demands
        self.assignments: List[Optional[Assignment]] = [None] * len(demands)
        self._fitness = None
        self._is_valid = None

    def set_assignment(self, demand_index: int, assignment: Assignment):
        """
        Set the assignment for a specific demand.

        Args:
            demand_index: Index of the demand in the demands list
            assignment: Assignment object or None to unassign
        """
        self.assignments[demand_index] = assignment
        # Invalidate cached fitness and validity
        self._fitness = None
        self._is_valid = None

    def get_assignment(self, demand_index: int) -> Optional[Assignment]:
        """Get the assignment for a specific demand."""
        return self.assignments[demand_index]

    def is_complete(self) -> bool:
        """Check if all demands are assigned."""
        return all(a is not None for a in self.assignments)

    def get_assigned_count(self) -> int:
        """Get number of assigned demands."""
        return sum(1 for a in self.assignments if a is not None)

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the solution for constraint satisfaction.

        Checks:
        1. Spectrum continuity: same slots on all links of a path
        2. Spectrum contiguity: slots are contiguous
        3. No spectrum conflicts: no overlapping assignments on same link

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Build spectrum occupancy map
        spectrum_map = {}
        for link in self.network.topology.edges():
            link_key = (min(link[0], link[1]), max(link[0], link[1]))
            spectrum_map[link_key] = [[] for _ in range(self.network.num_slots)]

        # Check each assignment
        for idx, assignment in enumerate(self.assignments):
            if assignment is None:
                continue

            demand = self.demands[idx]

            # Verify path connects source to destination
            if len(assignment.path) < 2:
                errors.append(f"Demand {idx}: Path too short: {assignment.path}")
                continue

            if assignment.path[0] != demand['source'] or assignment.path[-1] != demand['destination']:
                errors.append(
                    f"Demand {idx}: Path {assignment.path} does not connect "
                    f"{demand['source']} to {demand['destination']}"
                )

            # Check spectrum bounds
            if assignment.start_slot < 0 or assignment.end_slot > self.network.num_slots:
                errors.append(
                    f"Demand {idx}: Slots {assignment.start_slot}-{assignment.end_slot} "
                    f"out of bounds (max={self.network.num_slots})"
                )
                continue

            # Check for spectrum conflicts on each link
            for i in range(len(assignment.path) - 1):
                u, v = assignment.path[i], assignment.path[i + 1]
                link_key = (min(u, v), max(u, v))

                # Check if link exists
                if link_key not in spectrum_map:
                    errors.append(f"Demand {idx}: Link {link_key} does not exist in topology")
                    continue

                # Check each slot for conflicts
                for slot in range(assignment.start_slot, assignment.end_slot):
                    if spectrum_map[link_key][slot]:
                        # Conflict detected
                        conflicting = spectrum_map[link_key][slot]
                        errors.append(
                            f"Demand {idx}: Spectrum conflict on link {link_key}, slot {slot} "
                            f"with demands {conflicting}"
                        )
                    else:
                        # Mark slot as occupied
                        spectrum_map[link_key][slot].append(idx)

        is_valid = len(errors) == 0
        self._is_valid = is_valid
        return is_valid, errors

    def calculate_fitness(self) -> float:
        """
        Calculate solution fitness (lower is better).

        For static RMLSA, the primary objective is typically:
        - Minimize maximum slot index used (spectrum compactness)

        Secondary objectives:
        - Minimize total spectrum consumption
        - Minimize number of unassigned demands (penalty)

        Returns:
            float: Fitness value (lower is better)
        """
        if self._fitness is not None:
            return self._fitness

        # Large penalty for invalid or incomplete solutions
        is_valid, _ = self.validate()
        if not is_valid:
            self._fitness = float('inf')
            return self._fitness

        unassigned_count = len(self.demands) - self.get_assigned_count()
        if unassigned_count > 0:
            # Penalty for unassigned demands
            self._fitness = float('inf') - (len(self.demands) - unassigned_count)
            return self._fitness

        # Calculate max slot used across all assignments
        max_slot = 0
        total_spectrum = 0

        for assignment in self.assignments:
            if assignment is not None:
                max_slot = max(max_slot, assignment.end_slot)
                # Count spectrum consumption
                path_length = len(assignment.path) - 1
                total_spectrum += assignment.num_slots * path_length

        # Primary objective: minimize max slot used
        # Secondary objective: minimize total spectrum (weighted less)
        fitness = max_slot * 1000 + total_spectrum

        self._fitness = fitness
        return fitness

    def apply_to_network(self):
        """
        Apply this solution's assignments to the network.

        This resets the network and allocates spectrum according
        to all assignments in this solution.
        """
        self.network.reset()

        for assignment in self.assignments:
            if assignment is not None:
                success = self.network.allocate_spectrum(
                    assignment.path,
                    assignment.start_slot,
                    assignment.num_slots
                )
                if not success:
                    raise ValueError(f"Failed to apply {assignment} to network")

    def copy(self):
        """Create a deep copy of this solution."""
        new_solution = Solution(self.network, self.demands)
        new_solution.assignments = [
            a.copy() if a is not None else None
            for a in self.assignments
        ]
        return new_solution

    def get_metrics(self) -> Dict:
        """
        Get comprehensive metrics for this solution.

        Returns:
            Dictionary with various solution metrics
        """
        # Apply to network to calculate network-level metrics
        self.apply_to_network()

        is_valid, errors = self.validate()

        # Calculate path length and distance statistics
        path_lengths = []
        path_distances = []
        for assignment in self.assignments:
            if assignment is not None:
                path_lengths.append(len(assignment.path) - 1)
                # Calculate distance for this path
                path_distance = 0
                for i in range(len(assignment.path) - 1):
                    u, v = assignment.path[i], assignment.path[i + 1]
                    path_distance += self.network.topology[u][v]['distance']
                path_distances.append(path_distance)

        avg_path_length = np.mean(path_lengths) if path_lengths else 0
        max_path_length = max(path_lengths) if path_lengths else 0
        total_distance = sum(path_distances) if path_distances else 0
        avg_path_distance = np.mean(path_distances) if path_distances else 0

        return {
            'is_valid': is_valid,
            'is_complete': self.is_complete(),
            'assigned_count': self.get_assigned_count(),
            'total_demands': len(self.demands),
            'fitness': self.calculate_fitness(),
            'max_slot_used': self.network.get_max_slot_used(),
            'total_spectrum_consumption': self.network.get_total_spectrum_consumption(),
            'spectrum_utilization': self.network.get_spectrum_utilization(),
            'fragmentation_index': self.network.get_fragmentation_index(),
            'avg_path_length': avg_path_length,
            'max_path_length': max_path_length,
            'total_distance_km': total_distance,
            'avg_path_distance_km': avg_path_distance,
            'validation_errors': errors
        }

    def __repr__(self):
        assigned = self.get_assigned_count()
        total = len(self.demands)
        fitness = self.calculate_fitness()
        return f"Solution(assigned={assigned}/{total}, fitness={fitness:.2f})"


def create_empty_solution(network, demands: List[Dict]) -> Solution:
    """
    Create an empty solution with no assignments.

    Args:
        network: Network instance
        demands: List of demands

    Returns:
        Empty Solution object
    """
    return Solution(network, demands)
