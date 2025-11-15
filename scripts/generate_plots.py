#!/usr/bin/env python3
"""
Generación de Gráficos para Resultados de Optimización RMLSA

Genera visualizaciones de:
- Max Slot Used vs Número de Demandas
- Tiempo de Ejecución vs Número de Demandas
- Comparación de Algoritmos
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_results():
    """Cargar resultados de experimentos"""
    results_file = Path(__file__).parent.parent / 'results' / 'optimization_results.csv'
    if not results_file.exists():
        print(f"Error: No se encontró {results_file}")
        print("Ejecuta primero: python3 scripts/run_optimization_experiments.py")
        sys.exit(1)

    df = pd.read_csv(results_file)
    return df

def plot_max_slot_comparison(df):
    """Gráfico de Max Slot Used vs Número de Demandas"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Calcular promedio y std por algoritmo y tamaño
    summary = df.groupby(['num_demands', 'algorithm'])['max_slot_used'].agg(['mean', 'std']).reset_index()

    # Plot para cada algoritmo
    algorithms = ['greedy_ff', 'greedy_mw', 'sa', 'ga']
    colors = {'greedy_ff': '#FF6B6B', 'greedy_mw': '#4ECDC4', 'sa': '#45B7D1', 'ga': '#96CEB4'}
    markers = {'greedy_ff': 'o', 'greedy_mw': 's', 'sa': '^', 'ga': 'D'}
    labels = {
        'greedy_ff': 'Greedy First-Fit',
        'greedy_mw': 'Greedy Min-Growth',
        'sa': 'Simulated Annealing',
        'ga': 'Genetic Algorithm'
    }

    for alg in algorithms:
        data = summary[summary['algorithm'] == alg]
        ax.errorbar(data['num_demands'], data['mean'], yerr=data['std'],
                   marker=markers[alg], markersize=8, linewidth=2,
                   capsize=5, capthick=2,
                   label=labels[alg], color=colors[alg])

    ax.set_xlabel('Número de Demandas', fontsize=12, fontweight='bold')
    ax.set_ylabel('Max Slot Used (promedio)', fontsize=12, fontweight='bold')
    ax.set_title('Comparación de Algoritmos: Uso de Espectro', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(summary['num_demands'].unique())

    plt.tight_layout()
    output_file = Path(__file__).parent.parent / 'results' / 'max_slot_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Guardado: {output_file}")
    plt.close()

def plot_execution_time(df):
    """Gráfico de Tiempo de Ejecución"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Calcular promedio por algoritmo y tamaño
    summary = df.groupby(['num_demands', 'algorithm'])['execution_time'].mean().reset_index()

    algorithms = ['greedy_ff', 'greedy_mw', 'sa', 'ga']
    colors = {'greedy_ff': '#FF6B6B', 'greedy_mw': '#4ECDC4', 'sa': '#45B7D1', 'ga': '#96CEB4'}
    markers = {'greedy_ff': 'o', 'greedy_mw': 's', 'sa': '^', 'ga': 'D'}
    labels = {
        'greedy_ff': 'Greedy First-Fit',
        'greedy_mw': 'Greedy Min-Growth',
        'sa': 'Simulated Annealing',
        'ga': 'Genetic Algorithm'
    }

    for alg in algorithms:
        data = summary[summary['algorithm'] == alg]
        ax.plot(data['num_demands'], data['execution_time'],
               marker=markers[alg], markersize=8, linewidth=2,
               label=labels[alg], color=colors[alg])

    ax.set_xlabel('Número de Demandas', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tiempo de Ejecución (segundos)', fontsize=12, fontweight='bold')
    ax.set_title('Comparación de Tiempos de Ejecución', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks(summary['num_demands'].unique())
    ax.set_yscale('log')

    plt.tight_layout()
    output_file = Path(__file__).parent.parent / 'results' / 'execution_time_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Guardado: {output_file}")
    plt.close()

def plot_algorithm_bars(df):
    """Gráfico de barras comparando algoritmos"""
    # Promediar sobre todos los tamaños
    summary = df.groupby('algorithm').agg({
        'max_slot_used': 'mean',
        'total_spectrum': 'mean',
        'execution_time': 'mean'
    }).reset_index()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    algorithms = ['greedy_ff', 'greedy_mw', 'sa', 'ga']
    colors = {'greedy_ff': '#FF6B6B', 'greedy_mw': '#4ECDC4', 'sa': '#45B7D1', 'ga': '#96CEB4'}
    labels = {
        'greedy_ff': 'Greedy\nFirst-Fit',
        'greedy_mw': 'Greedy\nMin-Growth',
        'sa': 'Simulated\nAnnealing',
        'ga': 'Genetic\nAlgorithm'
    }

    # Subplot 1: Max Slot Used
    x = np.arange(len(algorithms))
    values = [summary[summary['algorithm'] == alg]['max_slot_used'].values[0] for alg in algorithms]
    bars1 = ax1.bar(x, values, color=[colors[alg] for alg in algorithms], alpha=0.8, edgecolor='black', linewidth=1.5)

    ax1.set_ylabel('Max Slot Used (promedio)', fontsize=12, fontweight='bold')
    ax1.set_title('Uso de Espectro por Algoritmo', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([labels[alg] for alg in algorithms], fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')

    # Añadir valores en las barras
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontweight='bold', fontsize=10)

    # Subplot 2: Tiempo de Ejecución
    values2 = [summary[summary['algorithm'] == alg]['execution_time'].values[0] for alg in algorithms]
    bars2 = ax2.bar(x, values2, color=[colors[alg] for alg in algorithms], alpha=0.8, edgecolor='black', linewidth=1.5)

    ax2.set_ylabel('Tiempo de Ejecución (segundos)', fontsize=12, fontweight='bold')
    ax2.set_title('Tiempo por Algoritmo', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([labels[alg] for alg in algorithms], fontsize=10)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax2.set_yscale('log')

    # Añadir valores en las barras
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}s',
                ha='center', va='bottom', fontweight='bold', fontsize=9)

    plt.tight_layout()
    output_file = Path(__file__).parent.parent / 'results' / 'algorithm_comparison_bars.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Guardado: {output_file}")
    plt.close()

def plot_combined_comparison(df):
    """Gráfico combinado con múltiples subplots"""
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    algorithms = ['greedy_ff', 'greedy_mw', 'sa', 'ga']
    colors = {'greedy_ff': '#FF6B6B', 'greedy_mw': '#4ECDC4', 'sa': '#45B7D1', 'ga': '#96CEB4'}
    markers = {'greedy_ff': 'o', 'greedy_mw': 's', 'sa': '^', 'ga': 'D'}
    labels = {
        'greedy_ff': 'Greedy First-Fit',
        'greedy_mw': 'Greedy Min-Growth',
        'sa': 'Simulated Annealing',
        'ga': 'Genetic Algorithm'
    }

    # Subplot 1: Max Slot Used
    ax1 = fig.add_subplot(gs[0, 0])
    summary_slot = df.groupby(['num_demands', 'algorithm'])['max_slot_used'].agg(['mean', 'std']).reset_index()
    for alg in algorithms:
        data = summary_slot[summary_slot['algorithm'] == alg]
        ax1.errorbar(data['num_demands'], data['mean'], yerr=data['std'],
                    marker=markers[alg], markersize=7, linewidth=2,
                    capsize=4, label=labels[alg], color=colors[alg])
    ax1.set_xlabel('Número de Demandas', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Max Slot Used', fontsize=11, fontweight='bold')
    ax1.set_title('(A) Uso de Espectro', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Subplot 2: Tiempo de Ejecución
    ax2 = fig.add_subplot(gs[0, 1])
    summary_time = df.groupby(['num_demands', 'algorithm'])['execution_time'].mean().reset_index()
    for alg in algorithms:
        data = summary_time[summary_time['algorithm'] == alg]
        ax2.plot(data['num_demands'], data['execution_time'],
                marker=markers[alg], markersize=7, linewidth=2,
                label=labels[alg], color=colors[alg])
    ax2.set_xlabel('Número de Demandas', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Tiempo (segundos)', fontsize=11, fontweight='bold')
    ax2.set_title('(B) Tiempo de Ejecución', fontsize=12, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_yscale('log')

    # Subplot 3: Utilización de Espectro
    ax3 = fig.add_subplot(gs[1, 0])
    summary_util = df.groupby(['num_demands', 'algorithm'])['utilization'].mean().reset_index()
    for alg in algorithms:
        data = summary_util[summary_util['algorithm'] == alg]
        ax3.plot(data['num_demands'], data['utilization'],
                marker=markers[alg], markersize=7, linewidth=2,
                label=labels[alg], color=colors[alg])
    ax3.set_xlabel('Número de Demandas', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Utilización (%)', fontsize=11, fontweight='bold')
    ax3.set_title('(C) Utilización de Espectro', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3, linestyle='--')

    # Subplot 4: Demandas Asignadas
    ax4 = fig.add_subplot(gs[1, 1])
    summary_assigned = df.groupby(['num_demands', 'algorithm']).agg({
        'assigned': 'mean',
        'total': 'first'
    }).reset_index()
    summary_assigned['percentage'] = (summary_assigned['assigned'] / summary_assigned['total']) * 100

    for alg in algorithms:
        data = summary_assigned[summary_assigned['algorithm'] == alg]
        ax4.plot(data['num_demands'], data['percentage'],
                marker=markers[alg], markersize=7, linewidth=2,
                label=labels[alg], color=colors[alg])
    ax4.set_xlabel('Número de Demandas', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Demandas Asignadas (%)', fontsize=11, fontweight='bold')
    ax4.set_title('(D) Tasa de Asignación', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, linestyle='--')
    ax4.set_ylim([75, 102])

    fig.suptitle('Comparación Completa de Algoritmos de Optimización RMLSA',
                 fontsize=16, fontweight='bold', y=0.995)

    output_file = Path(__file__).parent.parent / 'results' / 'combined_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Guardado: {output_file}")
    plt.close()

def main():
    """Generar todos los gráficos"""
    print("=" * 80)
    print("GENERACIÓN DE GRÁFICOS - RMLSA Static Optimizer")
    print("=" * 80)

    # Cargar resultados
    print("\nCargando resultados...")
    df = load_results()
    print(f"✓ Cargados {len(df)} resultados")

    # Generar gráficos
    print("\nGenerando gráficos...")
    plot_max_slot_comparison(df)
    plot_execution_time(df)
    plot_algorithm_bars(df)
    plot_combined_comparison(df)

    print("\n" + "=" * 80)
    print("✅ GRÁFICOS GENERADOS EXITOSAMENTE")
    print("=" * 80)
    print("\nArchivos generados en results/:")
    print("  - max_slot_comparison.png")
    print("  - execution_time_comparison.png")
    print("  - algorithm_comparison_bars.png")
    print("  - combined_comparison.png")
    print("=" * 80)

if __name__ == "__main__":
    main()
