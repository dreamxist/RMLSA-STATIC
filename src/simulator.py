"""
Static RMLSA Simulator
Simulates static (offline) RMLSA problem where all demands are known in advance
"""
from src.core.network import Network
from src.algorithms.sp_ff import sp_ff_assign
from src.algorithms.ksp_mw import ksp_mw_assign
import time


class StaticSimulator:
    """
    Simulator for static RMLSA problem.

    In the static scenario, all demands are known in advance and are
    processed in a specific order (typically sorted by bandwidth).
    """

    def __init__(self, topology, num_slots=320):
        """
        Initialize simulator.

        Args:
            topology (nx.Graph): Network topology
            num_slots (int): Number of spectrum slots per link (default: 320)
        """
        self.topology = topology
        self.num_slots = num_slots

    def run_simulation(self, demands, algorithm='sp_ff', k=3, verbose=False):
        """
        Run static RMLSA simulation.

        Algorithm steps:
        1. Sort demands by bandwidth (descending) - process larger demands first
        2. Create fresh network state
        3. Process each demand in order using the specified algorithm
        4. Collect metrics

        Args:
            demands (list): List of demand dictionaries
            algorithm (str): Algorithm to use ('sp_ff' or 'ksp_mw')
            k (int): Number of paths for k-SP-MW (default: 3)
            verbose (bool): Print detailed progress (default: False)

        Returns:
            dict: Simulation results containing:
                  - assigned: Number of demands assigned
                  - blocked: Number of demands blocked
                  - blocking_probability: Blocking rate (0-1)
                  - max_watermark: Maximum watermark achieved
                  - utilization: Spectrum utilization percentage
                  - assignments: List of assignment details
                  - execution_time: Simulation time in seconds
        """
        start_time = time.time()

        # Step 1: Sort demands by bandwidth (descending)
        # This is a key heuristic: process larger/harder demands first
        sorted_demands = sorted(demands, key=lambda d: d['bandwidth'], reverse=True)

        # Step 2: Create fresh network
        network = Network(self.topology, num_slots=self.num_slots)

        # Step 3: Process demands
        assigned_count = 0
        blocked_count = 0
        assignments = []

        for i, demand in enumerate(sorted_demands):
            if verbose:
                print(f"Processing demand {i+1}/{len(sorted_demands)}: "
                      f"{demand['source']} -> {demand['destination']}, "
                      f"{demand['bandwidth']} Gbps")

            # Apply algorithm
            if algorithm == 'sp_ff':
                result = sp_ff_assign(network, demand)
            elif algorithm == 'ksp_mw':
                result = ksp_mw_assign(network, demand, k=k)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")

            # Record result
            if result:
                assigned_count += 1
                assignments.append({
                    'demand_id': demand['id'],
                    'assigned': True,
                    **result
                })
                if verbose:
                    print(f"  ✓ Assigned (watermark: {network.get_max_watermark()})")
            else:
                blocked_count += 1
                assignments.append({
                    'demand_id': demand['id'],
                    'assigned': False
                })
                if verbose:
                    print(f"  ✗ Blocked")

        # Step 4: Calculate metrics
        execution_time = time.time() - start_time

        results = {
            'assigned': assigned_count,
            'blocked': blocked_count,
            'total': len(demands),
            'blocking_probability': blocked_count / len(demands) if len(demands) > 0 else 0,
            'max_watermark': network.get_max_watermark(),
            'utilization': network.get_spectrum_utilization(),
            'assignments': assignments,
            'execution_time': execution_time,
            'algorithm': algorithm
        }

        return results

    def compare_algorithms(self, demands, k=3, verbose=False):
        """
        Run simulation with both algorithms and compare results.

        Args:
            demands (list): List of demand dictionaries
            k (int): Number of paths for k-SP-MW
            verbose (bool): Print detailed progress

        Returns:
            dict: Comparison results with 'sp_ff' and 'ksp_mw' keys
        """
        print("Running SP-FF algorithm...")
        sp_ff_results = self.run_simulation(demands, algorithm='sp_ff', verbose=verbose)

        print("\nRunning k-SP-MW algorithm...")
        ksp_mw_results = self.run_simulation(demands, algorithm='ksp_mw', k=k, verbose=verbose)

        return {
            'sp_ff': sp_ff_results,
            'ksp_mw': ksp_mw_results
        }


if __name__ == "__main__":
    # Test simulator
    from data.nsfnet import create_nsfnet_topology
    from data.demand_generator import generate_demand_set

    print("Testing Static RMLSA Simulator...")
    print("=" * 80)

    # Create topology and simulator
    topology = create_nsfnet_topology()
    simulator = StaticSimulator(topology, num_slots=100)

    # Generate test demands
    num_demands = 20
    demands = generate_demand_set(num_demands, seed=42)

    print(f"\nSimulating {num_demands} demands...\n")

    # Compare algorithms
    results = simulator.compare_algorithms(demands, k=3, verbose=False)

    # Print comparison
    print("\n" + "=" * 80)
    print("RESULTS COMPARISON")
    print("=" * 80)

    for alg_name, alg_results in results.items():
        print(f"\n{alg_name.upper()}:")
        print(f"  Assigned: {alg_results['assigned']} / {alg_results['total']}")
        print(f"  Blocked: {alg_results['blocked']} / {alg_results['total']}")
        print(f"  Blocking Probability: {alg_results['blocking_probability']:.4f}")
        print(f"  Max Watermark: {alg_results['max_watermark']} slots")
        print(f"  Utilization: {alg_results['utilization']:.2f}%")
        print(f"  Execution Time: {alg_results['execution_time']:.4f} seconds")

    print("\n" + "=" * 80)
    print("IMPROVEMENTS (k-SP-MW vs SP-FF):")
    watermark_improvement = results['sp_ff']['max_watermark'] - results['ksp_mw']['max_watermark']
    blocking_improvement = results['sp_ff']['blocking_probability'] - results['ksp_mw']['blocking_probability']

    print(f"  Watermark reduction: {watermark_improvement} slots "
          f"({watermark_improvement / max(results['sp_ff']['max_watermark'], 1) * 100:.2f}%)")
    print(f"  Blocking probability reduction: {blocking_improvement:.4f} "
          f"({blocking_improvement * 100:.2f} percentage points)")
