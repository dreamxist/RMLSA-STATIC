"""
NSFNET Topology
14 nodes, 21 bidirectional links
Distances in kilometers (approximate real distances)
"""
import networkx as nx


def create_nsfnet_topology():
    """
    Creates the NSFNET topology as a NetworkX graph.

    Returns:
        nx.Graph: NSFNET topology with 14 nodes and 21 edges.
                  Each edge has a 'distance' attribute in km.
    """
    G = nx.Graph()

    # Add nodes (0-13)
    nodes = list(range(14))
    G.add_nodes_from(nodes)

    # Add edges with distances (in km)
    # Format: (node1, node2, distance_km)
    edges = [
        (0, 1, 1500),   # Seattle - San Francisco
        (0, 2, 2400),   # Seattle - Salt Lake City
        (1, 2, 900),    # San Francisco - Salt Lake City
        (1, 3, 600),    # San Francisco - San Diego
        (2, 5, 1200),   # Salt Lake City - Denver
        (3, 4, 800),    # San Diego - Phoenix
        (4, 5, 900),    # Phoenix - Denver
        (5, 6, 1000),   # Denver - Kansas City
        (5, 9, 1500),   # Denver - Houston
        (6, 7, 600),    # Kansas City - Champaign
        (6, 10, 500),   # Kansas City - Oklahoma
        (7, 8, 300),    # Champaign - Indianapolis
        (7, 11, 800),   # Champaign - Atlanta
        (8, 12, 400),   # Indianapolis - Pittsburgh
        (9, 10, 700),   # Houston - Oklahoma
        (9, 11, 1200),  # Houston - Atlanta
        (10, 11, 1100), # Oklahoma - Atlanta
        (11, 12, 900),  # Atlanta - Pittsburgh
        (11, 13, 600),  # Atlanta - Washington DC
        (12, 13, 300),  # Pittsburgh - Washington DC
        (12, 7, 500),   # Pittsburgh - Champaign
    ]

    # Add edges to graph
    for u, v, distance in edges:
        G.add_edge(u, v, distance=distance)

    return G


def get_node_names():
    """
    Returns a mapping of node IDs to city names.

    Returns:
        dict: Mapping of node_id -> city_name
    """
    return {
        0: "Seattle",
        1: "San Francisco",
        2: "Salt Lake City",
        3: "San Diego",
        4: "Phoenix",
        5: "Denver",
        6: "Kansas City",
        7: "Champaign",
        8: "Indianapolis",
        9: "Houston",
        10: "Oklahoma",
        11: "Atlanta",
        12: "Pittsburgh",
        13: "Washington DC"
    }


def get_path_distance(G, path):
    """
    Calculate total distance of a path in the network.

    Args:
        G (nx.Graph): Network graph
        path (list): List of nodes forming the path

    Returns:
        float: Total distance in km
    """
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += G[path[i]][path[i + 1]]['distance']
    return total_distance


if __name__ == "__main__":
    # Test the topology
    G = create_nsfnet_topology()
    print(f"NSFNET Topology:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"\nNode names:")
    for node_id, name in get_node_names().items():
        print(f"  {node_id}: {name}")

    # Test path distance
    test_path = [0, 2, 5, 6]  # Seattle -> Salt Lake -> Denver -> Kansas City
    distance = get_path_distance(G, test_path)
    print(f"\nExample path {test_path}: {distance} km")
