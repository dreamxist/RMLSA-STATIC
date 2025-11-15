"""
Network class for managing topology and spectrum state
"""
import numpy as np
import networkx as nx


class Network:
    """
    Represents an Elastic Optical Network (EON) with flexible spectrum grid.

    Manages the network topology and the state of spectrum allocation
    on each link.
    """

    def __init__(self, topology, num_slots=320):
        """
        Initialize the network.

        Args:
            topology (nx.Graph): Network topology graph
            num_slots (int): Total number of spectrum slots per link (default: 320)
        """
        self.topology = topology.copy()
        self.num_slots = num_slots

        # Initialize spectrum state for each link
        # spectrum[link] is a boolean array: True = occupied, False = available
        self.spectrum = {}
        for u, v in self.topology.edges():
            # Store as tuple (min, max) for consistency
            link = (min(u, v), max(u, v))
            self.spectrum[link] = np.zeros(num_slots, dtype=bool)

    def _get_link_key(self, u, v):
        """Get consistent link key regardless of edge direction."""
        return (min(u, v), max(u, v))

    def is_spectrum_available(self, path, start_slot, num_slots):
        """
        Check if a spectrum block is available on all links of a path.

        Implements spectrum continuity constraint: the same slots must be
        available on ALL links in the path.

        Args:
            path (list): List of nodes forming the path
            start_slot (int): Starting slot index
            num_slots (int): Number of contiguous slots needed

        Returns:
            bool: True if spectrum is available on entire path, False otherwise
        """
        end_slot = start_slot + num_slots

        # Check bounds
        if end_slot > self.num_slots:
            return False

        # Check all links in the path
        for i in range(len(path) - 1):
            link = self._get_link_key(path[i], path[i + 1])

            # Check if any slot in the range is occupied
            if np.any(self.spectrum[link][start_slot:end_slot]):
                return False

        return True

    def allocate_spectrum(self, path, start_slot, num_slots):
        """
        Allocate spectrum slots on all links of a path.

        Args:
            path (list): List of nodes forming the path
            start_slot (int): Starting slot index
            num_slots (int): Number of contiguous slots to allocate

        Returns:
            bool: True if allocation succeeded, False otherwise
        """
        # First verify availability
        if not self.is_spectrum_available(path, start_slot, num_slots):
            return False

        # Allocate on all links
        end_slot = start_slot + num_slots
        for i in range(len(path) - 1):
            link = self._get_link_key(path[i], path[i + 1])
            self.spectrum[link][start_slot:end_slot] = True

        return True

    def deallocate_spectrum(self, path, start_slot, num_slots):
        """
        Deallocate spectrum slots on all links of a path.

        Args:
            path (list): List of nodes forming the path
            start_slot (int): Starting slot index
            num_slots (int): Number of contiguous slots to deallocate
        """
        end_slot = start_slot + num_slots
        for i in range(len(path) - 1):
            link = self._get_link_key(path[i], path[i + 1])
            self.spectrum[link][start_slot:end_slot] = False

    def get_max_watermark(self):
        """
        Get the maximum watermark across all links.

        Watermark = highest slot index used + 1 (for 0-indexed slots).

        Returns:
            int: Maximum watermark (highest used slot + 1) across all links
        """
        max_watermark = 0

        for link, slots in self.spectrum.items():
            # Find the highest occupied slot
            occupied_indices = np.where(slots)[0]
            if len(occupied_indices) > 0:
                link_watermark = occupied_indices[-1] + 1
                max_watermark = max(max_watermark, link_watermark)

        return max_watermark

    def get_link_watermark(self, link):
        """
        Get watermark for a specific link.

        Args:
            link (tuple): Link as (u, v) tuple

        Returns:
            int: Watermark for this link
        """
        link_key = self._get_link_key(link[0], link[1])
        slots = self.spectrum[link_key]
        occupied_indices = np.where(slots)[0]

        if len(occupied_indices) > 0:
            return occupied_indices[-1] + 1
        return 0

    def get_spectrum_utilization(self):
        """
        Calculate average spectrum utilization across all links.

        Returns:
            float: Utilization as percentage (0-100)
        """
        total_slots = 0
        used_slots = 0

        for link, slots in self.spectrum.items():
            total_slots += len(slots)
            used_slots += np.sum(slots)

        if total_slots == 0:
            return 0.0

        return (used_slots / total_slots) * 100.0

    def reset(self):
        """Reset all spectrum allocations to empty."""
        for link in self.spectrum:
            self.spectrum[link][:] = False


if __name__ == "__main__":
    # Test the Network class
    from data.nsfnet import create_nsfnet_topology

    print("Testing Network class...")

    # Create network
    topology = create_nsfnet_topology()
    network = Network(topology, num_slots=100)

    print(f"Network initialized with {network.num_slots} slots per link")
    print(f"Initial watermark: {network.get_max_watermark()}")
    print(f"Initial utilization: {network.get_spectrum_utilization():.2f}%")

    # Test allocation
    test_path = [0, 2, 5, 6]  # Seattle -> Salt Lake -> Denver -> Kansas City
    print(f"\nTesting allocation on path: {test_path}")

    # Allocate 5 slots starting at slot 10
    success = network.allocate_spectrum(test_path, start_slot=10, num_slots=5)
    print(f"Allocation (slots 10-14): {success}")
    print(f"Watermark after allocation: {network.get_max_watermark()}")
    print(f"Utilization: {network.get_spectrum_utilization():.2f}%")

    # Try to allocate overlapping slots (should fail)
    success = network.allocate_spectrum(test_path, start_slot=12, num_slots=5)
    print(f"Overlapping allocation (slots 12-16): {success}")

    # Allocate non-overlapping slots
    success = network.allocate_spectrum(test_path, start_slot=20, num_slots=3)
    print(f"Non-overlapping allocation (slots 20-22): {success}")
    print(f"Final watermark: {network.get_max_watermark()}")
