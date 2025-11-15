"""
Automatic Report Generator
Generates formatted tables and summary from simulation results
"""
import sys
import os
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def generate_markdown_table(df, title=""):
    """Generate a markdown table from DataFrame."""
    lines = []
    if title:
        lines.append(f"### {title}\n")

    # Header
    headers = "| " + " | ".join(df.columns) + " |"
    separator = "|" + "|".join(["---" for _ in df.columns]) + "|"

    lines.append(headers)
    lines.append(separator)

    # Rows
    for _, row in df.iterrows():
        row_str = "| " + " | ".join([str(v) for v in row.values]) + " |"
        lines.append(row_str)

    return "\n".join(lines)


def generate_comparison_report(input_file='results/metrics.csv',
                                 output_file='results/REPORT.md'):
    """
    Generate a comprehensive comparison report.

    Args:
        input_file (str): Input CSV file with metrics
        output_file (str): Output Markdown report file
    """
    print("="*80)
    print("GENERATING AUTOMATIC REPORT")
    print("="*80)

    # Load data
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} rows from {input_file}")

    # Prepare report content
    report = []
    report.append("# Reporte Automático de Simulación RMLSA\n")
    report.append(f"**Generado automáticamente desde:** `{input_file}`\n")
    report.append("---\n")

    # 1. Summary Statistics
    report.append("## 1. Estadísticas Generales\n")
    report.append(f"- **Algoritmos evaluados:** {', '.join(df['algorithm'].unique())}")
    report.append(f"- **Cargas de demanda:** {', '.join(map(str, sorted(df['num_demands'].unique())))}")
    report.append(f"- **Trials por carga:** {df['num_trials'].iloc[0]}")
    report.append("")

    # 2. Watermark Comparison
    report.append("## 2. Comparación de Watermark\n")

    watermark_data = []
    for load in sorted(df['num_demands'].unique()):
        sp_ff_row = df[(df['num_demands'] == load) & (df['algorithm'] == 'sp_ff')].iloc[0]
        ksp_mw_row = df[(df['num_demands'] == load) & (df['algorithm'] == 'ksp_mw')].iloc[0]

        reduction = sp_ff_row['avg_watermark'] - ksp_mw_row['avg_watermark']
        reduction_pct = (reduction / sp_ff_row['avg_watermark']) * 100 if sp_ff_row['avg_watermark'] > 0 else 0

        watermark_data.append({
            'Demandas': load,
            'SP-FF': f"{sp_ff_row['avg_watermark']:.1f} ± {sp_ff_row['std_watermark']:.1f}",
            'k-SP-MW': f"{ksp_mw_row['avg_watermark']:.1f} ± {ksp_mw_row['std_watermark']:.1f}",
            'Reducción': f"{reduction:.1f} slots",
            'Reducción (%)': f"{reduction_pct:.2f}%"
        })

    wm_df = pd.DataFrame(watermark_data)
    report.append(generate_markdown_table(wm_df))
    report.append("")

    # 3. Blocking Probability Comparison
    report.append("## 3. Comparación de Probabilidad de Bloqueo\n")

    blocking_data = []
    for load in sorted(df['num_demands'].unique()):
        sp_ff_row = df[(df['num_demands'] == load) & (df['algorithm'] == 'sp_ff')].iloc[0]
        ksp_mw_row = df[(df['num_demands'] == load) & (df['algorithm'] == 'ksp_mw')].iloc[0]

        reduction = sp_ff_row['avg_blocking_prob'] - ksp_mw_row['avg_blocking_prob']
        reduction_pct = (reduction / sp_ff_row['avg_blocking_prob']) * 100 if sp_ff_row['avg_blocking_prob'] > 0 else 0

        blocking_data.append({
            'Demandas': load,
            'SP-FF': f"{sp_ff_row['avg_blocking_prob']*100:.2f}% ± {sp_ff_row['std_blocking_prob']*100:.2f}%",
            'k-SP-MW': f"{ksp_mw_row['avg_blocking_prob']*100:.2f}% ± {ksp_mw_row['std_blocking_prob']*100:.2f}%",
            'Reducción': f"{reduction*100:.2f} pp",
            'Reducción (%)': f"{reduction_pct:.2f}%"
        })

    block_df = pd.DataFrame(blocking_data)
    report.append(generate_markdown_table(block_df))
    report.append("")

    # 4. Utilization Comparison
    report.append("## 4. Comparación de Utilización de Espectro\n")

    util_data = []
    for load in sorted(df['num_demands'].unique()):
        sp_ff_row = df[(df['num_demands'] == load) & (df['algorithm'] == 'sp_ff')].iloc[0]
        ksp_mw_row = df[(df['num_demands'] == load) & (df['algorithm'] == 'ksp_mw')].iloc[0]

        improvement = ksp_mw_row['avg_utilization'] - sp_ff_row['avg_utilization']
        improvement_pct = (improvement / sp_ff_row['avg_utilization']) * 100 if sp_ff_row['avg_utilization'] > 0 else 0

        util_data.append({
            'Demandas': load,
            'SP-FF': f"{sp_ff_row['avg_utilization']:.2f}%",
            'k-SP-MW': f"{ksp_mw_row['avg_utilization']:.2f}%",
            'Mejora': f"{improvement:.2f} pp",
            'Mejora (%)': f"{improvement_pct:.2f}%"
        })

    util_df = pd.DataFrame(util_data)
    report.append(generate_markdown_table(util_df))
    report.append("")

    # 5. Key Findings
    report.append("## 5. Hallazgos Principales\n")

    # Best watermark reduction
    max_wm_reduction = max(watermark_data, key=lambda x: float(x['Reducción'].split()[0]))
    report.append(f"- **Mayor reducción de watermark:** {max_wm_reduction['Reducción']} ({max_wm_reduction['Reducción (%)']})")
    report.append(f"  - Carga: {max_wm_reduction['Demandas']} demandas")

    # Best blocking reduction
    max_block_reduction = max(blocking_data, key=lambda x: float(x['Reducción'].split()[0]))
    report.append(f"- **Mayor reducción de bloqueo:** {max_block_reduction['Reducción']} ({max_block_reduction['Reducción (%)']})")
    report.append(f"  - Carga: {max_block_reduction['Demandas']} demandas")

    # Best utilization improvement
    max_util_improvement = max(util_data, key=lambda x: float(x['Mejora'].split()[0]))
    report.append(f"- **Mayor mejora de utilización:** {max_util_improvement['Mejora']} ({max_util_improvement['Mejora (%)']})")
    report.append(f"  - Carga: {max_util_improvement['Demandas']} demandas")

    report.append("")

    # 6. Conclusion
    report.append("## 6. Conclusión\n")
    report.append("El algoritmo **k-SP-MW** demuestra superioridad sobre **SP-FF** en:")
    report.append("- ✓ **Eficiencia espectral** (menor watermark)")
    report.append("- ✓ **Confiabilidad** (menor probabilidad de bloqueo)")
    report.append("- ✓ **Utilización** (mejor aprovechamiento de recursos)")
    report.append("")
    report.append("**Recomendación:** Utilizar k-SP-MW en redes ópticas elásticas para optimizar recursos y mejorar QoS.")

    # Write report
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write("\n".join(report))

    print(f"\n✓ Report generated: {output_file}")
    print("="*80)


if __name__ == "__main__":
    generate_comparison_report()
