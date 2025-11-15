"""
SP-FF Algorithm (Shortest Path - First Fit)
Benchmark algorithm for RMLSA problem
"""
from src.core.routing import get_shortest_path, get_path_info
from src.core.spectrum import first_fit
from data.modulation import calculate_required_slots


def sp_ff_assign(network, demand):
    """
    Assign a demand using SP-FF algorithm.

    Algorithm steps:
    1. Find the shortest path (SP) between source and destination
    2. Calculate required slots based on path distance and bandwidth
    3. Use First-Fit (FF) to assign spectrum on that path
    4. If successful, allocate and return assignment info
    5. If failed, return None (demand is blocked)

    Args:
        network (Network): Network object managing topology and spectrum
        demand (dict): Demand with 'source', 'destination', 'bandwidth'

    Returns:
        dict or None: Assignment info if successful, None if blocked
                      Assignment info contains:
                      - path: List of nodes
                      - start_slot: Starting slot index
                      - num_slots: Number of slots allocated
                      - modulation: Modulation format used
                      - distance: Path distance in km
    """
    source = demand['source']
    destination = demand['destination']
    bandwidth = demand['bandwidth']

    # Step 1: Find shortest path
    path = get_shortest_path(network.topology, source, destination)

    if path is None:
        # No route exists (shouldn't happen in connected network)
        return None

    # Get path information
    path_info = get_path_info(network.topology, path)
    distance = path_info['distance']

    # Step 2: Calculate required slots based on distance and bandwidth
    num_slots, modulation_format = calculate_required_slots(bandwidth, distance)

    if num_slots is None:
        # Distance too long for any modulation format
        return None

    # Step 3: Find spectrum using First-Fit
    start_slot = first_fit(network, path, num_slots)

    if start_slot is None:
        # No available spectrum - demand is blocked
        return None

    # Step 4: Allocate spectrum
    success = network.allocate_spectrum(path, start_slot, num_slots)

    if not success:
        # Allocation failed (shouldn't happen if first_fit succeeded)
        return None

    # Return assignment information
    assignment = {
        'path': path,
        'start_slot': start_slot,
        'num_slots': num_slots,
        'modulation': modulation_format,
        'distance': distance,
        'num_hops': path_info['num_hops']
    }

    return assignment


if __name__ == "__main__":
    # Test SP-FF algorithm
    from data.nsfnet import create_nsfnet_topology, get_node_names
    from src.core.network import Network
    from data.demand_generator import generate_demand_set

    print("Testing SP-FF Algorithm...")

    # Create network
    topology = create_nsfnet_topology()
    network = Network(topology, num_slots=100)
    node_names = get_node_names()

    # Generate a few test demands
    demands = generate_demand_set(num_demands=5, seed=42)

    print(f"\nProcessing {len(demands)} demands with SP-FF:\n")
    print("=" * 80)

    assigned = 0
    blocked = 0

    for demand in demands:
        print(f"\nDemand {demand['id']}: {node_names[demand['source']]} -> "
              f"{node_names[demand['destination']]}, {demand['bandwidth']} Gbps")

        result = sp_ff_assign(network, demand)

        if result:
            assigned += 1
            path_names = [node_names[n] for n in result['path']]
            print(f"  ✓ ASSIGNED")
            print(f"    Path: {' -> '.join(path_names)}")
            print(f"    Distance: {result['distance']} km")
            print(f"    Modulation: {result['modulation']}")
            print(f"    Slots: {result['start_slot']} - {result['start_slot'] + result['num_slots'] - 1}")
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
