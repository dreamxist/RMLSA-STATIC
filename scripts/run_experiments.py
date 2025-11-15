"""
Run RMLSA experiments with varying loads
Compares SP-FF vs k-SP-MW algorithms
"""
import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.nsfnet import create_nsfnet_topology
from data.demand_generator import generate_demand_set
from src.simulator import StaticSimulator


def run_experiments(demand_loads, num_trials=5, num_slots=320, k=3, output_file='results/metrics.csv'):
    """
    Run experiments for different demand loads.

    Args:
        demand_loads (list): List of number of demands to test (e.g., [50, 100, 150, 200])
        num_trials (int): Number of trials per load (for statistical averaging)
        num_slots (int): Number of spectrum slots per link
        k (int): Number of paths for k-SP-MW algorithm
        output_file (str): Output CSV filename for results

    Returns:
        pd.DataFrame: Results dataframe
    """
    print("="*80)
    print("RMLSA STATIC SIMULATION EXPERIMENTS")
    print("="*80)
    print(f"Configuration:")
    print(f"  Demand loads: {demand_loads}")
    print(f"  Trials per load: {num_trials}")
    print(f"  Spectrum slots: {num_slots}")
    print(f"  k-paths: {k}")
    print("="*80)

    # Create topology and simulator
    topology = create_nsfnet_topology()
    simulator = StaticSimulator(topology, num_slots=num_slots)

    # Store results
    all_results = []

    # Run experiments for each load
    for load in demand_loads:
        print(f"\n{'='*80}")
        print(f"Testing with {load} demands...")
        print(f"{'='*80}")

        load_results = {
            'sp_ff': {'watermarks': [], 'blocking_probs': [], 'utilizations': []},
            'ksp_mw': {'watermarks': [], 'blocking_probs': [], 'utilizations': []}
        }

        # Run multiple trials
        for trial in range(num_trials):
            print(f"\n  Trial {trial + 1}/{num_trials}...")

            # Generate demands with different seed for each trial
            seed = trial * 1000 + load
            demands = generate_demand_set(load, seed=seed)

            # Run both algorithms
            results = simulator.compare_algorithms(demands, k=k, verbose=False)

            # Store metrics
            for alg in ['sp_ff', 'ksp_mw']:
                load_results[alg]['watermarks'].append(results[alg]['max_watermark'])
                load_results[alg]['blocking_probs'].append(results[alg]['blocking_probability'])
                load_results[alg]['utilizations'].append(results[alg]['utilization'])

            print(f"    SP-FF:   Watermark={results['sp_ff']['max_watermark']}, "
                  f"Pb={results['sp_ff']['blocking_probability']:.4f}")
            print(f"    k-SP-MW: Watermark={results['ksp_mw']['max_watermark']}, "
                  f"Pb={results['ksp_mw']['blocking_probability']:.4f}")

        # Calculate statistics for this load
        print(f"\n  Results for {load} demands (averaged over {num_trials} trials):")

        for alg in ['sp_ff', 'ksp_mw']:
            avg_watermark = np.mean(load_results[alg]['watermarks'])
            std_watermark = np.std(load_results[alg]['watermarks'])
            avg_blocking = np.mean(load_results[alg]['blocking_probs'])
            std_blocking = np.std(load_results[alg]['blocking_probs'])
            avg_utilization = np.mean(load_results[alg]['utilizations'])

            print(f"\n  {alg.upper()}:")
            print(f"    Watermark: {avg_watermark:.2f} ± {std_watermark:.2f}")
            print(f"    Blocking Prob: {avg_blocking:.4f} ± {std_blocking:.4f}")
            print(f"    Utilization: {avg_utilization:.2f}%")

            # Store aggregated result
            all_results.append({
                'num_demands': load,
                'algorithm': alg,
                'avg_watermark': avg_watermark,
                'std_watermark': std_watermark,
                'avg_blocking_prob': avg_blocking,
                'std_blocking_prob': std_blocking,
                'avg_utilization': avg_utilization,
                'num_trials': num_trials
            })

    # Convert to DataFrame
    df_results = pd.DataFrame(all_results)

    # Save to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_results.to_csv(output_file, index=False)
    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}")

    return df_results


if __name__ == "__main__":
    # Define experimental parameters
    DEMAND_LOADS = [50, 100, 150, 200]  # Number of demands to test
    NUM_TRIALS = 5                       # Trials per load for statistical averaging
    NUM_SLOTS = 320                      # Spectrum slots per link
    K_PATHS = 3                          # Number of candidate paths for k-SP-MW

    # Run experiments
    results_df = run_experiments(
        demand_loads=DEMAND_LOADS,
        num_trials=NUM_TRIALS,
        num_slots=NUM_SLOTS,
        k=K_PATHS,
        output_file='results/metrics.csv'
    )

    # Display summary
    print("\n" + "="*80)
    print("EXPERIMENT SUMMARY")
    print("="*80)
    print(results_df.to_string(index=False))

    # Calculate improvements
    print("\n" + "="*80)
    print("IMPROVEMENTS (k-SP-MW vs SP-FF)")
    print("="*80)

    for load in DEMAND_LOADS:
        sp_ff_data = results_df[(results_df['num_demands'] == load) &
                                 (results_df['algorithm'] == 'sp_ff')].iloc[0]
        ksp_mw_data = results_df[(results_df['num_demands'] == load) &
                                  (results_df['algorithm'] == 'ksp_mw')].iloc[0]

        watermark_reduction = sp_ff_data['avg_watermark'] - ksp_mw_data['avg_watermark']
        watermark_reduction_pct = (watermark_reduction / sp_ff_data['avg_watermark']) * 100 if sp_ff_data['avg_watermark'] > 0 else 0

        blocking_reduction = sp_ff_data['avg_blocking_prob'] - ksp_mw_data['avg_blocking_prob']

        print(f"\nLoad = {load} demands:")
        print(f"  Watermark reduction: {watermark_reduction:.2f} slots ({watermark_reduction_pct:.2f}%)")
        print(f"  Blocking prob reduction: {blocking_reduction:.4f} ({blocking_reduction*100:.2f} pp)")
