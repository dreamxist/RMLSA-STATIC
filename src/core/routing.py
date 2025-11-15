"""
Routing algorithms for path computation
"""
import networkx as nx
from data.nsfnet import get_path_distance


def get_k_shortest_paths(graph, source, target, k=3, weight='distance'):
    """
    Find k shortest paths between source and target using Yen's algorithm.

    Args:
        graph (nx.Graph): Network topology
        source (int): Source node ID
        target (int): Target node ID
        k (int): Number of paths to find (default: 3)
        weight (str): Edge attribute to use as weight (default: 'distance')

    Returns:
        list: List of up to k paths, each path is a list of nodes.
              Returns fewer than k paths if not enough exist.
              Returns empty list if no path exists.
    """
    if source == target:
        return [[source]]

    try:
        # NetworkX provides shortest_simple_paths which implements Yen's algorithm
        paths_generator = nx.shortest_simple_paths(graph, source, target, weight=weight)

        # Get up to k paths
        paths = []
        for i, path in enumerate(paths_generator):
            if i >= k:
                break
            paths.append(path)

        return paths

    except nx.NetworkXNoPath:
        # No path exists between source and target
        return []


def get_shortest_path(graph, source, target, weight='distance'):
    """
    Find the shortest path between source and target.

    Args:
        graph (nx.Graph): Network topology
        source (int): Source node ID
        target (int): Target node ID
        weight (str): Edge attribute to use as weight (default: 'distance')

    Returns:
        list: Shortest path as list of nodes, or None if no path exists
    """
    try:
        path = nx.shortest_path(graph, source, target, weight=weight)
        return path
    except nx.NetworkXNoPath:
        return None


def get_path_info(graph, path):
    """
    Get detailed information about a path.

    Args:
        graph (nx.Graph): Network topology
        path (list): List of nodes forming the path

    Returns:
        dict: Path information containing:
              - distance: Total distance in km
              - num_hops: Number of hops (links)
              - nodes: List of nodes in path
    """
    if not path:
        return None

    distance = get_path_distance(graph, path)
    num_hops = len(path) - 1

    return {
        'distance': distance,
        'num_hops': num_hops,
        'nodes': path
    }


if __name__ == "__main__":
    # Test routing algorithms
    from data.nsfnet import create_nsfnet_topology, get_node_names

    print("Testing routing algorithms...")
    topology = create_nsfnet_topology()
    node_names = get_node_names()

    # Test case: Seattle (0) to Washington DC (13)
    source, target = 0, 13
    print(f"\nFinding paths from {node_names[source]} to {node_names[target]}:")

    # Get k=3 shortest paths
    k = 3
    paths = get_k_shortest_paths(topology, source, target, k=k)

    print(f"\nFound {len(paths)} path(s):")
    for i, path in enumerate(paths, 1):
        info = get_path_info(topology, path)
        path_names = [node_names[n] for n in path]
        print(f"\nPath {i}:")
        print(f"  Nodes: {' -> '.join(path_names)}")
        print(f"  Distance: {info['distance']} km")
        print(f"  Hops: {info['num_hops']}")

    # Test shortest path only
    print("\n" + "="*70)
    shortest = get_shortest_path(topology, source, target)
    if shortest:
        info = get_path_info(topology, shortest)
        print(f"Shortest path: {shortest}")
        print(f"Distance: {info['distance']} km")
