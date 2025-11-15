#!/usr/bin/env python3
"""
Experimentos de Optimización Estática RMLSA

Este script ejecuta experimentos comparando diferentes algoritmos de optimización
estática (GA, SA, Greedy baselines) en el problema RMLSA.

Métricas correctas:
- Max Slot Used (compacidad espectral)
- Total Spectrum Consumption
- Fragmentation Index
"""

import sys
import time
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.nsfnet import create_nsfnet_topology
from data.demand_generator import generate_demand_set
from src.simulator import StaticOptimizer


def run_experiments(
    demand_sizes=[10, 20, 30, 40, 50],
    trials=3,
    algorithms=['greedy_ff', 'greedy_mw', 'sa', 'ga']
):
    """
    Ejecutar experimentos de optimización.

    Args:
        demand_sizes: Lista de tamaños de conjuntos de demandas a probar
        trials: Número de repeticiones por tamaño
        algorithms: Algoritmos a comparar
    """
    print("=" * 80)
    print("EXPERIMENTOS DE OPTIMIZACIÓN ESTÁTICA RMLSA")
    print("=" * 80)
    print(f"Tamaños de demandas: {demand_sizes}")
    print(f"Trials por tamaño: {trials}")
    print(f"Algoritmos: {algorithms}")
    print("=" * 80)
    print()

    # Create topology and optimizer
    topology = create_nsfnet_topology()
    optimizer = StaticOptimizer(topology, num_slots=320)

    # Store results
    results = []

    for num_demands in demand_sizes:
        print(f"\n{'#' * 80}")
        print(f"# PROBANDO CON {num_demands} DEMANDAS")
        print(f"{'#' * 80}\n")

        for trial in range(trials):
            print(f"Trial {trial + 1}/{trials}...")

            # Generate demands with different seed per trial
            seed = trial + num_demands * 100
            demands = generate_demand_set(num_demands, seed=seed)

            for alg in algorithms:
                print(f"  Ejecutando {alg.upper()}...", end=" ", flush=True)

                start_time = time.time()

                # Configure parameters based on algorithm
                if alg == 'ga':
                    params = {
                        'population_size': min(50, num_demands * 2),
                        'generations': 50
                    }
                elif alg == 'sa':
                    params = {
                        'initial_temperature': 1000.0,
                        'cooling_rate': 0.95,
                        'iterations_per_temp': 50
                    }
                else:
                    params = {}

                # Run optimization
                result = optimizer.optimize(
                    demands,
                    algorithm=alg,
                    verbose=False,
                    **params
                )

                exec_time = time.time() - start_time
                m = result['metrics']

                print(f"✓ Max Slot={m['max_slot_used']:3d}, "
                      f"Assigned={m['assigned_count']:2d}/{m['total_demands']:2d}, "
                      f"Time={exec_time:.2f}s")

                # Store result
                results.append({
                    'num_demands': num_demands,
                    'trial': trial + 1,
                    'algorithm': alg,
                    'max_slot_used': m['max_slot_used'],
                    'total_spectrum': m['total_spectrum_consumption'],
                    'assigned': m['assigned_count'],
                    'total': m['total_demands'],
                    'utilization': m['spectrum_utilization'],
                    'fragmentation': m['fragmentation_index'],
                    'avg_path_length': m['avg_path_length'],
                    'execution_time': exec_time,
                    'is_complete': m['is_complete']
                })

    # Create results dataframe
    df = pd.DataFrame(results)

    # Save to CSV
    output_dir = Path(__file__).parent.parent / 'results'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / 'optimization_results.csv'
    df.to_csv(output_file, index=False)

    print(f"\n{'=' * 80}")
    print(f"Resultados guardados en: {output_file}")
    print(f"{'=' * 80}\n")

    # Print summary statistics
    print_summary(df)

    return df


def print_summary(df):
    """Imprimir resumen de resultados"""
    print("\n" + "=" * 80)
    print("RESUMEN DE RESULTADOS")
    print("=" * 80)

    # Group by demand size and algorithm
    summary = df.groupby(['num_demands', 'algorithm']).agg({
        'max_slot_used': ['mean', 'std'],
        'total_spectrum': ['mean', 'std'],
        'assigned': 'mean',
        'total': 'first',
        'execution_time': 'mean'
    }).round(2)

    print("\nMax Slot Used (promedio ± std):")
    print("-" * 80)
    pivot = df.pivot_table(
        values='max_slot_used',
        index='num_demands',
        columns='algorithm',
        aggfunc=['mean', 'std']
    )
    print(pivot)

    print("\nTiempo de Ejecución (segundos):")
    print("-" * 80)
    exec_pivot = df.pivot_table(
        values='execution_time',
        index='num_demands',
        columns='algorithm',
        aggfunc='mean'
    )
    print(exec_pivot.round(3))

    print("\nDemandas Asignadas (promedio):")
    print("-" * 80)
    assigned_pivot = df.pivot_table(
        values='assigned',
        index='num_demands',
        columns='algorithm',
        aggfunc='mean'
    )
    print(assigned_pivot)

    # Find best algorithm per demand size
    print("\nMejor Algoritmo por Tamaño de Demandas:")
    print("-" * 80)
    for num_demands in sorted(df['num_demands'].unique()):
        subset = df[df['num_demands'] == num_demands]
        best = subset.groupby('algorithm')['max_slot_used'].mean().idxmin()
        best_value = subset.groupby('algorithm')['max_slot_used'].mean().min()
        print(f"  {num_demands} demandas: {best.upper()} (max_slot_used={best_value:.1f})")


if __name__ == "__main__":
    # Run experiments
    run_experiments(
        demand_sizes=[10, 20, 30, 40, 50],
        trials=3,
        algorithms=['greedy_ff', 'greedy_mw', 'sa', 'ga']
    )

    print("\n" + "=" * 80)
    print("EXPERIMENTOS COMPLETADOS")
    print("=" * 80)
