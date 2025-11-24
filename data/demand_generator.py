"""
Demand generation for network simulations
"""
import numpy as np
import pandas as pd


class DemandGenerator:
    """
    Generate connection demands for RMLSA simulation.

    In the static scenario, demands are generated all at once and
    represent a fixed set of connection requests to be assigned.
    """

    def __init__(self, num_nodes, seed=None):
        """
        Initialize demand generator.

        Args:
            num_nodes (int): Number of nodes in the network
            seed (int, optional): Random seed for reproducibility
        """
        self.num_nodes = num_nodes
        self.rng = np.random.RandomState(seed)

    def generate_uniform_demands(self, num_demands, bandwidth_range=(25, 100)):
        """
        Generate demands with uniform random distribution.

        Args:
            num_demands (int): Number of demands to generate
            bandwidth_range (tuple): (min, max) bandwidth in Gbps

        Returns:
            list: List of demand dictionaries, each containing:
                  - id: Demand ID
                  - source: Source node
                  - destination: Destination node
                  - bandwidth: Requested bandwidth in Gbps
        """
        demands = []

        for i in range(num_demands):
            # Select random source and destination (must be different)
            source = self.rng.randint(0, self.num_nodes)
            destination = self.rng.randint(0, self.num_nodes)

            # Ensure source != destination
            while destination == source:
                destination = self.rng.randint(0, self.num_nodes)

            # Generate bandwidth uniformly in range
            bandwidth = self.rng.randint(bandwidth_range[0], bandwidth_range[1] + 1)

            demand = {
                'id': i,
                'source': source,
                'destination': destination,
                'bandwidth': bandwidth
            }
            demands.append(demand)

        return demands

    def generate_all_pairs(self, bandwidth_range=(25, 100)):
        """
        Generate demands for ALL possible source-destination pairs.

        For a network with N nodes, this generates N*(N-1) demands
        (one for each directed pair where source != destination).

        Args:
            bandwidth_range (tuple): (min, max) bandwidth in Gbps

        Returns:
            list: List of demand dictionaries (N*(N-1) demands)
        """
        demands = []
        demand_id = 0

        for source in range(self.num_nodes):
            for destination in range(self.num_nodes):
                if source != destination:
                    bandwidth = self.rng.randint(bandwidth_range[0], bandwidth_range[1] + 1)
                    demand = {
                        'id': demand_id,
                        'source': source,
                        'destination': destination,
                        'bandwidth': bandwidth
                    }
                    demands.append(demand)
                    demand_id += 1

        return demands

    def generate_exponential_bandwidth(self, num_demands, mean_bandwidth=50):
        """
        Generate demands with exponentially distributed bandwidth.

        This models traffic where most demands are small, with occasional
        large demands (more realistic for some network scenarios).

        Args:
            num_demands (int): Number of demands to generate
            mean_bandwidth (float): Mean bandwidth in Gbps

        Returns:
            list: List of demand dictionaries
        """
        demands = []

        for i in range(num_demands):
            # Random source and destination
            source = self.rng.randint(0, self.num_nodes)
            destination = self.rng.randint(0, self.num_nodes)

            while destination == source:
                destination = self.rng.randint(0, self.num_nodes)

            # Exponentially distributed bandwidth, clipped to reasonable range
            bandwidth = self.rng.exponential(mean_bandwidth)
            bandwidth = max(10, min(200, int(bandwidth)))  # Clip to [10, 200] Gbps

            demand = {
                'id': i,
                'source': source,
                'destination': destination,
                'bandwidth': bandwidth
            }
            demands.append(demand)

        return demands

    def save_demands(self, demands, filename):
        """
        Save demands to CSV file.

        Args:
            demands (list): List of demand dictionaries
            filename (str): Output CSV filename
        """
        df = pd.DataFrame(demands)
        df.to_csv(filename, index=False)
        print(f"Saved {len(demands)} demands to {filename}")

    def load_demands(self, filename):
        """
        Load demands from CSV file.

        Args:
            filename (str): Input CSV filename

        Returns:
            list: List of demand dictionaries
        """
        df = pd.read_csv(filename)
        demands = df.to_dict('records')
        return demands


def generate_demand_set(num_demands, num_nodes=14, bandwidth_range=(25, 100), seed=None):
    """
    Convenience function to generate a demand set.

    Args:
        num_demands (int): Number of demands
        num_nodes (int): Number of nodes in network (default: 14 for NSFNET)
        bandwidth_range (tuple): (min, max) bandwidth in Gbps
        seed (int, optional): Random seed

    Returns:
        list: List of demand dictionaries
    """
    generator = DemandGenerator(num_nodes, seed=seed)
    return generator.generate_uniform_demands(num_demands, bandwidth_range)


def generate_all_pairs_demand_set(num_nodes=14, bandwidth_range=(25, 100), seed=None):
    """
    Generate demands for ALL possible source-destination pairs.

    For NSFNET (14 nodes): generates 14*13 = 182 demands.

    Args:
        num_nodes (int): Number of nodes in network (default: 14 for NSFNET)
        bandwidth_range (tuple): (min, max) bandwidth in Gbps
        seed (int, optional): Random seed

    Returns:
        list: List of demand dictionaries (num_nodes * (num_nodes-1) demands)
    """
    generator = DemandGenerator(num_nodes, seed=seed)
    return generator.generate_all_pairs(bandwidth_range)


if __name__ == "__main__":
    # Test demand generation
    print("Testing demand generation...")

    # Generate 10 demands
    generator = DemandGenerator(num_nodes=14, seed=42)
    demands = generator.generate_uniform_demands(num_demands=10, bandwidth_range=(25, 100))

    print(f"\nGenerated {len(demands)} demands:")
    print("-" * 70)
    print(f"{'ID':<5} {'Source':<10} {'Dest':<10} {'Bandwidth (Gbps)':<20}")
    print("-" * 70)

    for d in demands:
        print(f"{d['id']:<5} {d['source']:<10} {d['destination']:<10} {d['bandwidth']:<20}")

    # Test exponential distribution
    print("\n" + "="*70)
    print("Testing exponential bandwidth distribution...")
    demands_exp = generator.generate_exponential_bandwidth(num_demands=10, mean_bandwidth=50)

    bandwidths = [d['bandwidth'] for d in demands_exp]
    print(f"Mean bandwidth: {np.mean(bandwidths):.2f} Gbps")
    print(f"Std bandwidth: {np.std(bandwidths):.2f} Gbps")
    print(f"Min/Max: {min(bandwidths)} / {max(bandwidths)} Gbps")

    # Test save/load
    print("\n" + "="*70)
    test_file = "/tmp/test_demands.csv"
    generator.save_demands(demands, test_file)
    loaded = generator.load_demands(test_file)
    print(f"Loaded {len(loaded)} demands from file")
