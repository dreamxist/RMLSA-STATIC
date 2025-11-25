import networkx as nx


def create_nsfnet():
    """Crea y retorna el grafo NSFNet con distancias en km."""
    G = nx.Graph()
    G.add_nodes_from(range(14))

    # (Node1, Node2, Distance)
    edges = [
        (0, 1, 1500),
        (0, 2, 2400),
        (1, 2, 900),
        (1, 3, 600),
        (2, 5, 1200),
        (3, 4, 800),
        (4, 5, 900),
        (5, 6, 1000),
        (5, 9, 1800),
        (6, 7, 600),
        (6, 10, 800),
        (7, 8, 300),
        (8, 9, 1300),
        (8, 11, 700),
        (8, 12, 500),
        (9, 10, 500),
        (9, 11, 800),
        (10, 11, 900),
        (11, 12, 900),
        (11, 13, 1000),
        (12, 13, 400),
    ]

    for u, v, d in edges:
        G.add_edge(u, v, weight=d, distance=d)

    return G


def get_node_names():
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
        13: "Washington DC",
    }


def get_path_distance(G, path):
    dist = 0
    for i in range(len(path) - 1):
        dist += G[path[i]][path[i + 1]]["distance"]
    return dist


def get_k_shortest_paths(G, source, target, k=3):
    """Wrapper optimizado para Yen's algorithm de NetworkX."""
    try:
        # shortest_simple_paths genera caminos ordenados por peso (distancia)
        generator = nx.shortest_simple_paths(G, source, target, weight="distance")
        paths = []
        for _ in range(k):
            paths.append(next(generator))
        return paths
    except (nx.NetworkXNoPath, StopIteration):
        return paths
