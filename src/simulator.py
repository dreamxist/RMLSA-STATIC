"""
Static RMLSA Simulator with Optimization Framework

This simulator implements TRUE static RMLSA optimization where all demands
are known in advance and assigned simultaneously using optimization algorithms
(metaheuristics) rather than sequential greedy heuristics.
"""
from src.core.network import Network
from src.core.solution import Solution, Assignment, create_empty_solution
from src.algorithms.sp_ff import sp_ff_assign
from src.metaheuristics.genetic_algorithm import GeneticAlgorithm
import time


class StaticOptimizer:
    """
    Optimizer for static RMLSA problem.

    In true static RMLSA, all demands are known in advance and the goal
    is to find an optimal assignment that minimizes spectrum usage
    (typically measured as maximum slot index used).

    This is fundamentally different from dynamic RMLSA where demands
    arrive and depart over time.
    """

    def __init__(self, topology, num_slots=320):
        """
        Initialize optimizer.

        Args:
            topology (nx.Graph): Network topology
            num_slots (int): Number of spectrum slots per link (default: 320)
        """
        self.topology = topology
        self.num_slots = num_slots

    def optimize(self, demands, algorithm='ga', verbose=True, **kwargs):
        """
        Optimize static RMLSA using specified algorithm.

        Args:
            demands (list): List of demand dictionaries
            algorithm (str): Algorithm to use:
                - 'ga': Genetic Algorithm (metaheuristic)
                - 'ff': First-Fit heuristic (baseline)
            verbose (bool): Print progress information
            **kwargs: Additional algorithm-specific parameters

        Returns:
            dict: Optimization results containing:
                - solution: Best Solution object found
                - metrics: Dictionary of solution metrics
                - execution_time: Optimization time in seconds
                - algorithm: Algorithm name
                - convergence: Algorithm-specific convergence data (for metaheuristics)
        """
        start_time = time.time()

        # Create network
        network = Network(self.topology, num_slots=self.num_slots)

        if verbose:
            print(f"\n{'='*80}")
            print(f"Static RMLSA Optimization")
            print(f"{'='*80}")
            print(f"Network: {len(self.topology.nodes())} nodes, {len(self.topology.edges())} links")
            print(f"Spectrum: {self.num_slots} slots per link")
            print(f"Demands: {len(demands)} total")
            print(f"Algorithm: {algorithm.upper()}")
            print(f"{'='*80}\n")

        # Run optimization based on algorithm
        if algorithm == 'ga':
            solution, convergence = self._optimize_ga(network, demands, verbose, **kwargs)
        elif algorithm == 'ff':
            solution, convergence = self._optimize_ff(network, demands, verbose, **kwargs)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        execution_time = time.time() - start_time

        # Get comprehensive metrics
        metrics = solution.get_metrics()

        results = {
            'solution': solution,
            'metrics': metrics,
            'execution_time': execution_time,
            'algorithm': algorithm,
            'convergence': convergence
        }

        if verbose:
            self._print_results(results)

        return results

    def _optimize_ga(self, network, demands, verbose, **kwargs):
        """Run Genetic Algorithm optimization."""
        ga = GeneticAlgorithm(
            network=network,
            demands=demands,
            population_size=kwargs.get('population_size', 50),
            generations=kwargs.get('generations', 100),
            crossover_rate=kwargs.get('crossover_rate', 0.8),
            mutation_rate=kwargs.get('mutation_rate', 0.2),
            elite_size=kwargs.get('elite_size', 2),
            k_paths=kwargs.get('k_paths', 3),
            tournament_size=kwargs.get('tournament_size', 3)
        )

        solution = ga.optimize(verbose=verbose)

        convergence = {
            'best_fitness_history': ga.best_fitness_history,
            'avg_fitness_history': ga.avg_fitness_history
        }

        return solution, convergence

    def _optimize_ff(self, network, demands, verbose, **kwargs):
        """
        Run First-Fit heuristic (baseline for comparison).

        Note: This is NOT true static optimization - it's a sequential
        greedy heuristic included as a baseline for comparison.
        """
        solution = create_empty_solution(network, demands)

        # Sort demands by bandwidth (descending)
        sorted_indices = sorted(
            range(len(demands)),
            key=lambda i: demands[i]['bandwidth'],
            reverse=True
        )

        if verbose:
            print(f"Running First-Fit heuristic...")

        for idx in sorted_indices:
            demand = demands[idx]
            result = sp_ff_assign(network, demand)

            if result:
                path = result['path']
                start_slot = result['start_slot']
                num_slots = result['num_slots']
                solution.set_assignment(idx, Assignment(idx, path, start_slot, num_slots))

        # No convergence data for greedy
        convergence = {}

        return solution, convergence

    def _print_results(self, results):
        """Print formatted results."""
        metrics = results['metrics']

        print(f"\n{'='*80}")
        print(f"OPTIMIZATION RESULTS")
        print(f"{'='*80}")
        print(f"Algorithm: {results['algorithm'].upper()}")
        print(f"Execution Time: {results['execution_time']:.2f} seconds")
        print()
        print(f"Solution Status:")
        print(f"  Valid: {metrics['is_valid']}")
        print(f"  Complete: {metrics['is_complete']}")
        print(f"  Assigned: {metrics['assigned_count']} / {metrics['total_demands']}")
        print()
        print(f"Spectrum Metrics:")
        print(f"  Max Slot Used: {metrics['max_slot_used']} slots")
        print(f"  Total Spectrum Consumption: {metrics['total_spectrum_consumption']} slot-links")
        print(f"  Spectrum Utilization: {metrics['spectrum_utilization']:.2f}%")
        print(f"  Fragmentation Index: {metrics['fragmentation_index']:.2f}")
        print()
        print(f"Path Metrics:")
        print(f"  Average Path Length: {metrics['avg_path_length']:.2f} hops")
        print(f"  Maximum Path Length: {metrics['max_path_length']} hops")
        print(f"{'='*80}\n")

    def compare_algorithms(self, demands, algorithms=None, verbose=True):
        """
        Compare multiple algorithms on the same demand set.

        Args:
            demands (list): List of demands
            algorithms (list): List of algorithm names to compare
                             Default: ['ff', 'ga']
            verbose (bool): Print progress

        Returns:
            dict: Results for each algorithm
        """
        if algorithms is None:
            algorithms = ['ff', 'ga']

        results = {}

        for alg in algorithms:
            if verbose:
                print(f"\n{'#'*80}")
                print(f"Running {alg.upper()}...")
                print(f"{'#'*80}")

            results[alg] = self.optimize(
                demands,
                algorithm=alg,
                verbose=verbose
            )

        # Print comparison table
        if verbose:
            self._print_comparison(results)

        return results

    def _print_comparison(self, results):
        """Print comparison table of all algorithms."""
        print(f"\n{'='*80}")
        print(f"ALGORITHM COMPARISON")
        print(f"{'='*80}\n")

        # Header
        print(f"{'Algorithm':<15} {'Assigned':<10} {'Max Slot':<10} {'Total Spec':<12} "
              f"{'Util %':<8} {'Time (s)':<10}")
        print(f"{'-'*80}")

        # Data rows
        for alg_name, result in results.items():
            m = result['metrics']
            print(
                f"{alg_name.upper():<15} "
                f"{m['assigned_count']:>3}/{m['total_demands']:<3} "
                f"{m['max_slot_used']:<10} "
                f"{m['total_spectrum_consumption']:<12} "
                f"{m['spectrum_utilization']:<7.2f}% "
                f"{result['execution_time']:<10.2f}"
            )

        print(f"{'='*80}\n")

        # Find best solution
        valid_results = {
            name: res for name, res in results.items()
            if res['metrics']['is_complete']
        }

        if valid_results:
            best_alg = min(
                valid_results.keys(),
                key=lambda k: valid_results[k]['metrics']['max_slot_used']
            )
            best_slot = valid_results[best_alg]['metrics']['max_slot_used']

            print(f"Best Solution: {best_alg.upper()} (Max Slot Used = {best_slot})")
            print(f"{'='*80}\n")


# Keep backward compatibility with old name
StaticSimulator = StaticOptimizer


if __name__ == "__main__":
    # Test optimizer
    from data.nsfnet import create_nsfnet_topology
    from data.demand_generator import generate_demand_set

    print("Testing Static RMLSA Optimizer...")

    # Create topology and optimizer
    topology = create_nsfnet_topology()
    optimizer = StaticOptimizer(topology, num_slots=320)

    # Generate test demands (reduced to ensure complete solutions)
    num_demands = 15
    demands = generate_demand_set(num_demands, seed=42)

    # Compare FF vs GA
    results = optimizer.compare_algorithms(
        demands,
        algorithms=['ff', 'ga'],
        verbose=True
    )
