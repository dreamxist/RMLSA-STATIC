"""
k-SP-MW Algorithm (k-Shortest Paths - Minimum Watermark)
Proposed heuristic algorithm for RMLSA problem
"""
from src.core.routing import get_k_shortest_paths, get_path_info
from src.core.spectrum import first_fit, calculate_watermark_increment
from data.modulation import calculate_required_slots


def ksp_mw_assign(network, demand, k=3):
    """
    Assign a demand using k-SP-MW algorithm.

    Algorithm steps:
    1. Find k shortest paths between source and destination
    2. For each path:
       a. Calculate required slots based on path distance and bandwidth
       b. Calculate what the watermark would be if we assign on this path
    3. Choose the path that results in the minimum watermark
    4. Allocate spectrum on the chosen path
    5. If all paths fail, return None (demand is blocked)

    This heuristic aims to minimize spectrum usage (watermark) by choosing
    routes that pack spectrum more efficiently, even if they're not the
    shortest path.

    Args:
        network (Network): Network object managing topology and spectrum
        demand (dict): Demand with 'source', 'destination', 'bandwidth'
        k (int): Number of candidate paths to evaluate (default: 3)

    Returns:
        dict or None: Assignment info if successful, None if blocked
                      Assignment info contains:
                      - path: List of nodes
                      - start_slot: Starting slot index
                      - num_slots: Number of slots allocated
                      - modulation: Modulation format used
                      - distance: Path distance in km
                      - watermark: Resulting watermark
    """
    source = demand['source']
    destination = demand['destination']
    bandwidth = demand['bandwidth']

    # Step 1: Find k shortest paths
    paths = get_k_shortest_paths(network.topology, source, destination, k=k)

    if not paths:
        # No route exists
        return None

    # Step 2: Evaluate each path
    best_path = None
    best_watermark = float('inf')
    best_start_slot = None
    best_num_slots = None
    best_modulation = None
    best_distance = None
    best_num_hops = None

    for path in paths:
        # Get path info
        path_info = get_path_info(network.topology, path)
        distance = path_info['distance']

        # Calculate required slots
        num_slots, modulation_format = calculate_required_slots(bandwidth, distance)

        if num_slots is None:
            # This path is too long for this bandwidth
            continue

        # Calculate watermark increment
        new_watermark = calculate_watermark_increment(network, path, num_slots)

        if new_watermark is None:
            # No spectrum available on this path
            continue

        # Check if this is the best path so far
        if new_watermark < best_watermark:
            best_watermark = new_watermark
            best_path = path
            best_num_slots = num_slots
            best_modulation = modulation_format
            best_distance = distance
            best_num_hops = path_info['num_hops']

    # Step 3: If no viable path found, demand is blocked
    if best_path is None:
        return None

    # Step 4: Allocate spectrum on the best path
    best_start_slot = first_fit(network, best_path, best_num_slots)

    if best_start_slot is None:
        # This shouldn't happen (calculate_watermark_increment said it was ok)
        return None

    success = network.allocate_spectrum(best_path, best_start_slot, best_num_slots)

    if not success:
        # This shouldn't happen either
        return None

    # Return assignment information
    assignment = {
        'path': best_path,
        'start_slot': best_start_slot,
        'num_slots': best_num_slots,
        'modulation': best_modulation,
        'distance': best_distance,
        'num_hops': best_num_hops,
        'watermark': best_watermark
    }

    return assignment


if __name__ == "__main__":
    # Test k-SP-MW algorithm
    from data.nsfnet import create_nsfnet_topology, get_node_names
    from src.core.network import Network
    from data.demand_generator import generate_demand_set

    print("Testing k-SP-MW Algorithm...")

    # Create network
    topology = create_nsfnet_topology()
    network = Network(topology, num_slots=100)
    node_names = get_node_names()

    # Generate test demands
    demands = generate_demand_set(num_demands=5, seed=42)

    print(f"\nProcessing {len(demands)} demands with k-SP-MW (k=3):\n")
    print("=" * 80)

    assigned = 0
    blocked = 0

    for demand in demands:
        print(f"\nDemand {demand['id']}: {node_names[demand['source']]} -> "
              f"{node_names[demand['destination']]}, {demand['bandwidth']} Gbps")

        result = ksp_mw_assign(network, demand, k=3)

        if result:
            assigned += 1
            path_names = [node_names[n] for n in result['path']]
            print(f"  ✓ ASSIGNED")
            print(f"    Path: {' -> '.join(path_names)}")
            print(f"    Distance: {result['distance']} km")
            print(f"    Modulation: {result['modulation']}")
            print(f"    Slots: {result['start_slot']} - {result['start_slot'] + result['num_slots'] - 1}")
            print(f"    Watermark after: {result['watermark']}")
        else:
            blocked += 1
            print(f"  ✗ BLOCKED")

    print("\n" + "=" * 80)
    print(f"Summary:")
    print(f"  Assigned: {assigned}")
    print(f"  Blocked: {blocked}")
    print(f"  Blocking Rate: {blocked / len(demands) * 100:.2f}%")
    print(f"  Max Slot Used: {network.get_max_slot_used()}")
    print(f"  Utilization: {network.get_spectrum_utilization():.2f}%")
