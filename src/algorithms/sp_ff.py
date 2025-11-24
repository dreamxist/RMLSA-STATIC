"""
KSP-FF Algorithm (K-Shortest Paths - First Fit)
Benchmark algorithm for RMLSA problem
"""
import networkx as nx
from src.core.routing import get_path_info
from src.core.spectrum import first_fit
from data.modulation import calculate_required_slots


def sp_ff_assign(network, demand, k=3):
    """
    Assign a demand using K-Shortest Paths with First-Fit algorithm.

    Algorithm steps:
    1. Find k shortest paths between source and destination
    2. For each path, try to assign using First-Fit
    3. Return first successful assignment
    4. If all paths fail, return None (demand is blocked)

    Args:
        network (Network): Network object managing topology and spectrum
        demand (dict): Demand with 'source', 'destination', 'bandwidth'
        k (int): Number of shortest paths to try (default: 3)

    Returns:
        dict or None: Assignment info if successful, None if blocked
    """
    source = demand['source']
    destination = demand['destination']
    bandwidth = demand['bandwidth']

    # Step 1: Find k shortest paths
    try:
        paths = list(nx.shortest_simple_paths(
            network.topology, source, destination
        ))[:k]
    except nx.NetworkXNoPath:
        return None

    if not paths:
        return None

    # Step 2: Try each path with First-Fit
    for path in paths:
        path_info = get_path_info(network.topology, path)
        distance = path_info['distance']

        num_slots, modulation_format = calculate_required_slots(bandwidth, distance)

        if num_slots is None:
            continue

        start_slot = first_fit(network, path, num_slots)

        if start_slot is not None:
            success = network.allocate_spectrum(path, start_slot, num_slots)

            if success:
                return {
                    'path': path,
                    'start_slot': start_slot,
                    'num_slots': num_slots,
                    'modulation': modulation_format,
                    'distance': distance,
                    'num_hops': path_info['num_hops']
                }

    return None


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
