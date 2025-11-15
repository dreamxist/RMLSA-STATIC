"""
Spectrum assignment algorithms
"""


def first_fit(network, path, num_slots):
    """
    First-Fit spectrum assignment algorithm.

    Searches for the first available contiguous block of spectrum slots
    that satisfies the spectrum continuity constraint (same slots available
    on all links in the path).

    Args:
        network (Network): Network object managing spectrum state
        path (list): List of nodes forming the path
        num_slots (int): Number of contiguous slots required

    Returns:
        int or None: Starting slot index if successful, None if no fit found
    """
    # Try each starting position from slot 0 upward
    for start_slot in range(network.num_slots - num_slots + 1):
        if network.is_spectrum_available(path, start_slot, num_slots):
            return start_slot

    # No available block found
    return None


def calculate_watermark_increment(network, path, num_slots):
    """
    Calculate the watermark that would result from assigning spectrum
    on a given path using First-Fit.

    This is used by the k-SP-MW algorithm to choose the path that
    minimizes watermark growth.

    Args:
        network (Network): Network object managing spectrum state
        path (list): List of nodes forming the path
        num_slots (int): Number of contiguous slots required

    Returns:
        int or None: Resulting watermark if assignment succeeds,
                     None if assignment would fail (no available slots)
    """
    # Find where First-Fit would assign
    start_slot = first_fit(network, path, num_slots)

    if start_slot is None:
        # No fit possible - return None to indicate blocking
        return None

    # Calculate what the new max slot used would be
    end_slot = start_slot + num_slots
    current_max_slot = network.get_max_slot_used()

    # New max slot is the max of current and what this would create
    new_max_slot = max(current_max_slot, end_slot)

    return new_max_slot


def best_fit(network, path, num_slots):
    """
    Best-Fit spectrum assignment algorithm (optional - not used in this project).

    Finds the smallest available contiguous block that can fit the demand.
    This minimizes fragmentation.

    Args:
        network (Network): Network object managing spectrum state
        path (list): List of nodes forming the path
        num_slots (int): Number of contiguous slots required

    Returns:
        int or None: Starting slot index if successful, None if no fit found
    """
    best_start = None
    best_gap_size = float('inf')

    start_slot = 0
    while start_slot <= network.num_slots - num_slots:
        if network.is_spectrum_available(path, start_slot, num_slots):
            # Find the size of this available gap
            gap_size = num_slots
            test_slot = start_slot + num_slots
            while test_slot < network.num_slots and \
                  network.is_spectrum_available(path, start_slot, test_slot - start_slot + 1):
                gap_size += 1
                test_slot += 1

            # Update best if this gap is smaller
            if gap_size < best_gap_size:
                best_gap_size = gap_size
                best_start = start_slot

            # Skip to end of this gap
            start_slot = test_slot
        else:
            start_slot += 1

    return best_start


if __name__ == "__main__":
    # Test spectrum assignment
    from data.nsfnet import create_nsfnet_topology
    from src.core.network import Network

    print("Testing spectrum assignment algorithms...")

    # Create network
    topology = create_nsfnet_topology()
    network = Network(topology, num_slots=50)

    test_path = [0, 2, 5, 6]  # Seattle -> Salt Lake -> Denver -> Kansas City
    print(f"Test path: {test_path}")

    # Test First-Fit
    print("\n--- First-Fit Test ---")
    start1 = first_fit(network, test_path, num_slots=5)
    print(f"First-Fit for 5 slots: start at slot {start1}")

    if start1 is not None:
        network.allocate_spectrum(test_path, start1, 5)
        print(f"Allocated. Watermark: {network.get_max_watermark()}")

    # Allocate more
    start2 = first_fit(network, test_path, num_slots=3)
    print(f"First-Fit for 3 slots: start at slot {start2}")

    if start2 is not None:
        network.allocate_spectrum(test_path, start2, 3)
        print(f"Allocated. Watermark: {network.get_max_watermark()}")

    # Test watermark increment calculation
    print("\n--- Watermark Increment Test ---")
    wm = calculate_watermark_increment(network, test_path, num_slots=4)
    print(f"Watermark if we allocate 4 more slots: {wm}")

    # Test on another path
    test_path2 = [1, 2, 5]  # San Francisco -> Salt Lake -> Denver
    wm2 = calculate_watermark_increment(network, test_path2, num_slots=6)
    print(f"Watermark if we allocate 6 slots on different path: {wm2}")
