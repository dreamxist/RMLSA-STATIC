import time
import matplotlib.pyplot as plt
import numpy as np
from topology import create_nsfnet
from traffic import DemandGenerator
from algorithms import run_sp_ff, GeneticOptimizer


def print_summary(alg_name, result, time_taken):
    print(f"\n{'=' * 35}")
    print(f"RESUMEN FINAL: {alg_name}")
    print(f"{'=' * 35}")
    print(f"Tiempo ejecución:   {time_taken:.4f} s")
    print(f"Asignadas:          {result['assigned']} / {result['total']}")
    print(f"Max FSU Index:      {result['max_slot']}")
    print(f"Uso Espectro Global:{result['utilization']:.2f}%")
    print(f"{'=' * 35}\n")

    return {
        "Algorithm": alg_name,
        "Assigned": result["assigned"],
        "Max_Slot": result["max_slot"],
        "Utilization": result["utilization"],
    }


def plot_results(data):
    """Genera gráficos de barras comparando los dos algoritmos."""
    if not data:
        return

    names = [d["Algorithm"] for d in data]
    max_slots = [d["Max_Slot"] for d in data]
    assigned = [d["Assigned"] for d in data]

    x = np.arange(len(names))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(8, 6))

    # --- Eje Izquierdo: Max Slot Index (Barras Azules) ---
    color1 = "#1f77b4"
    bars1 = ax1.bar(
        x - width / 2,
        max_slots,
        width,
        label="Max Slot Index (Menor es mejor)",
        color=color1,
        alpha=0.8,
    )
    ax1.set_ylabel("Max Slot Index", color=color1, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(0, 320)

    # --- Eje Derecho: Asignaciones (Barras Verdes) ---
    ax2 = ax1.twinx()
    color2 = "#2ca02c"
    bars2 = ax2.bar(
        x + width / 2,
        assigned,
        width,
        label="Demandas Asignadas",
        color=color2,
        alpha=0.8,
    )
    ax2.set_ylabel("Demandas Asignadas", color=color2, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=color2)

    if assigned:
        ax2.set_ylim(0, max(assigned) * 1.15)

    ax1.set_title(
        "Comparativa RMLSA: Baseline vs Genetic Algorithm", fontsize=14, pad=15
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    ax1.bar_label(bars1, padding=3, fmt="%d")
    ax2.bar_label(bars2, padding=3, fmt="%d")

    # Leyenda unificada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncol=2,
    )

    fig.tight_layout()
    output_filename = "resultado_comparativa.png"
    plt.savefig(output_filename)
    print(f"\n[GRÁFICO] Guardado exitosamente en: '{output_filename}'")

    try:
        plt.show()
    except Exception:
        pass


def main():
    print("=== SIMULADOR RMLSA: OPTIMIZACIÓN DE ESPECTRO ===")
    NUM_SLOTS = 320
    AVG_BW = 100.0

    topo = create_nsfnet()
    # Generamos demandas con semilla fija para consistencia
    gen = DemandGenerator(len(topo.nodes()), seed=42)
    demands_original = gen.generate_full_mesh(topo, avg_bw=AVG_BW)
    print(
        f"Escenario: {len(topo.nodes())} nodos | {len(demands_original)} demandas de tráfico.\n"
    )

    filename = "assignments_details.txt"
    results_summary = []

    with open(filename, "w") as f:
        f.write("=== REPORTE DETALLADO DE ASIGNACIONES ===\n\n")

        # ---------------------------------------------------------
        # 1. Baseline: SP-FF (Orden Original)
        # ---------------------------------------------------------
        print("Ejecutando 1: SP-FF (Baseline - Orden Original)...")
        f.write(">>> 1. SP-FF (Baseline)\n")
        start = time.time()
        res_base = run_sp_ff(topo, demands_original, num_slots=NUM_SLOTS, export_file=f)
        end = time.time()
        results_summary.append(print_summary("SP-FF (Baseline)", res_base, end - start))
        f.write("\n")

        # ---------------------------------------------------------
        # 2. Genetic Algorithm
        # ---------------------------------------------------------
        print("Ejecutando 2: Algoritmo Genético (Optimización)...")
        f.write(">>> 2. Genetic Algorithm (Optimized)\n")
        start = time.time()
        ga = GeneticOptimizer(
            topo, demands_original, pop_size=50, generations=100, num_slots=NUM_SLOTS
        )
        res_ga = ga.optimize(export_file_handle=f)

        end = time.time()
        results_summary.append(print_summary("Algoritmo Genético", res_ga, end - start))

    print(f"Detalle de asignaciones guardado en: {filename}")

    plot_results(results_summary)


if __name__ == "__main__":
    main()
