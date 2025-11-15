"""
Generate visualization plots from simulation results
"""
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def plot_watermark_comparison(df, output_file='results/watermark_comparison.png'):
    """
    Plot watermark comparison between SP-FF and k-SP-MW.

    Args:
        df (pd.DataFrame): Results dataframe
        output_file (str): Output filename for plot
    """
    # Separate data by algorithm
    sp_ff_data = df[df['algorithm'] == 'sp_ff'].sort_values('num_demands')
    ksp_mw_data = df[df['algorithm'] == 'ksp_mw'].sort_values('num_demands')

    # Create figure
    plt.figure(figsize=(10, 6))

    # Plot lines with error bars
    plt.errorbar(sp_ff_data['num_demands'],
                 sp_ff_data['avg_watermark'],
                 yerr=sp_ff_data['std_watermark'],
                 marker='o', markersize=8, linewidth=2,
                 capsize=5, capthick=2,
                 label='SP-FF (Benchmark)',
                 color='#E74C3C')

    plt.errorbar(ksp_mw_data['num_demands'],
                 ksp_mw_data['avg_watermark'],
                 yerr=ksp_mw_data['std_watermark'],
                 marker='s', markersize=8, linewidth=2,
                 capsize=5, capthick=2,
                 label='k-SP-MW (Proposed)',
                 color='#3498DB')

    # Labels and title
    plt.xlabel('Number of Demands', fontsize=14, fontweight='bold')
    plt.ylabel('Maximum Watermark (slots)', fontsize=14, fontweight='bold')
    plt.title('Spectrum Efficiency: Watermark Comparison', fontsize=16, fontweight='bold')

    # Grid and legend
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=12, loc='upper left')

    # Tight layout and save
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Watermark plot saved to: {output_file}")
    plt.close()


def plot_blocking_probability(df, output_file='results/blocking_probability.png'):
    """
    Plot blocking probability comparison between SP-FF and k-SP-MW.

    Args:
        df (pd.DataFrame): Results dataframe
        output_file (str): Output filename for plot
    """
    # Separate data by algorithm
    sp_ff_data = df[df['algorithm'] == 'sp_ff'].sort_values('num_demands')
    ksp_mw_data = df[df['algorithm'] == 'ksp_mw'].sort_values('num_demands')

    # Create figure
    plt.figure(figsize=(10, 6))

    # Plot lines with error bars
    plt.errorbar(sp_ff_data['num_demands'],
                 sp_ff_data['avg_blocking_prob'],
                 yerr=sp_ff_data['std_blocking_prob'],
                 marker='o', markersize=8, linewidth=2,
                 capsize=5, capthick=2,
                 label='SP-FF (Benchmark)',
                 color='#E74C3C')

    plt.errorbar(ksp_mw_data['num_demands'],
                 ksp_mw_data['avg_blocking_prob'],
                 yerr=ksp_mw_data['std_blocking_prob'],
                 marker='s', markersize=8, linewidth=2,
                 capsize=5, capthick=2,
                 label='k-SP-MW (Proposed)',
                 color='#3498DB')

    # Labels and title
    plt.xlabel('Number of Demands', fontsize=14, fontweight='bold')
    plt.ylabel('Blocking Probability', fontsize=14, fontweight='bold')
    plt.title('Network Reliability: Blocking Probability Comparison', fontsize=16, fontweight='bold')

    # Grid and legend
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=12, loc='upper left')

    # Tight layout and save
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Blocking probability plot saved to: {output_file}")
    plt.close()


def plot_combined_comparison(df, output_file='results/combined_comparison.png'):
    """
    Create a combined figure with both metrics side by side.

    Args:
        df (pd.DataFrame): Results dataframe
        output_file (str): Output filename for plot
    """
    # Separate data by algorithm
    sp_ff_data = df[df['algorithm'] == 'sp_ff'].sort_values('num_demands')
    ksp_mw_data = df[df['algorithm'] == 'ksp_mw'].sort_values('num_demands')

    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: Watermark
    ax1.errorbar(sp_ff_data['num_demands'],
                 sp_ff_data['avg_watermark'],
                 yerr=sp_ff_data['std_watermark'],
                 marker='o', markersize=8, linewidth=2,
                 capsize=5, capthick=2,
                 label='SP-FF',
                 color='#E74C3C')

    ax1.errorbar(ksp_mw_data['num_demands'],
                 ksp_mw_data['avg_watermark'],
                 yerr=ksp_mw_data['std_watermark'],
                 marker='s', markersize=8, linewidth=2,
                 capsize=5, capthick=2,
                 label='k-SP-MW',
                 color='#3498DB')

    ax1.set_xlabel('Number of Demands', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Maximum Watermark (slots)', fontsize=12, fontweight='bold')
    ax1.set_title('(a) Spectrum Efficiency', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(fontsize=11)

    # Plot 2: Blocking Probability
    ax2.errorbar(sp_ff_data['num_demands'],
                 sp_ff_data['avg_blocking_prob'],
                 yerr=sp_ff_data['std_blocking_prob'],
                 marker='o', markersize=8, linewidth=2,
                 capsize=5, capthick=2,
                 label='SP-FF',
                 color='#E74C3C')

    ax2.errorbar(ksp_mw_data['num_demands'],
                 ksp_mw_data['avg_blocking_prob'],
                 yerr=ksp_mw_data['std_blocking_prob'],
                 marker='s', markersize=8, linewidth=2,
                 capsize=5, capthick=2,
                 label='k-SP-MW',
                 color='#3498DB')

    ax2.set_xlabel('Number of Demands', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Blocking Probability', fontsize=12, fontweight='bold')
    ax2.set_title('(b) Network Reliability', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(fontsize=11)

    # Overall title
    fig.suptitle('RMLSA Algorithm Comparison: SP-FF vs k-SP-MW',
                 fontsize=16, fontweight='bold', y=1.00)

    # Tight layout and save
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Combined comparison plot saved to: {output_file}")
    plt.close()


def generate_all_plots(input_file='results/metrics.csv'):
    """
    Generate all visualization plots from results file.

    Args:
        input_file (str): Input CSV file with simulation results
    """
    print("="*80)
    print("GENERATING VISUALIZATION PLOTS")
    print("="*80)

    # Load results
    if not os.path.exists(input_file):
        print(f"Error: Results file not found: {input_file}")
        print("Please run 'python scripts/run_experiments.py' first.")
        return

    df = pd.read_csv(input_file)
    print(f"Loaded results from: {input_file}")
    print(f"  Rows: {len(df)}")
    print(f"  Algorithms: {df['algorithm'].unique()}")
    print(f"  Demand loads: {sorted(df['num_demands'].unique())}")

    # Generate plots
    print("\nGenerating plots...")
    plot_watermark_comparison(df)
    plot_blocking_probability(df)
    plot_combined_comparison(df)

    print("\n" + "="*80)
    print("All plots generated successfully!")
    print("="*80)


if __name__ == "__main__":
    generate_all_plots('results/metrics.csv')
