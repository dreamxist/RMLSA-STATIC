import random


class DemandGenerator:
    def __init__(self, num_nodes, seed=42):
        self.num_nodes = num_nodes
        self.rng = random.Random(seed)

    def generate_exponential(self, num_demands, avg_bw=100.0):
        demands = []
        for i in range(num_demands):
            src = self.rng.randint(0, self.num_nodes - 1)
            dst = self.rng.randint(0, self.num_nodes - 1)
            while src == dst:
                dst = self.rng.randint(0, self.num_nodes - 1)

            # Distribución exponencial para el ancho de banda
            bw = int(self.rng.expovariate(1.0 / avg_bw))
            bw = max(10, min(bw, 1000))  # Clampear entre 10Gbps y 1Tbps

            demands.append(
                {"id": i, "source": src, "destination": dst, "bandwidth": bw}
            )
        return demands

    def generate_full_mesh(self, topology, avg_bw=100.0):
        """Genera tráfico entre todos los pares (N*(N-1))."""
        demands = []
        nodes = list(topology.nodes())
        counter = 0
        for u in nodes:
            for v in nodes:
                if u != v:
                    bw = int(self.rng.expovariate(1.0 / avg_bw))
                    bw = max(25, bw)
                    demands.append(
                        {"id": counter, "source": u, "destination": v, "bandwidth": bw}
                    )
                    counter += 1
        return demands
