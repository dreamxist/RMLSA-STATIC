# Reporte Automático de Simulación RMLSA

**Generado automáticamente desde:** `results/metrics.csv`

---

## 1. Estadísticas Generales

- **Algoritmos evaluados:** sp_ff, ksp_mw
- **Cargas de demanda:** 50, 100, 150, 200
- **Trials por carga:** 5

## 2. Comparación de Watermark

| Demandas | SP-FF | k-SP-MW | Reducción | Reducción (%) |
|---|---|---|---|---|
| 50 | 167.0 ± 12.8 | 122.0 ± 9.8 | 45.0 slots | 26.95% |
| 100 | 297.6 ± 23.8 | 247.2 ± 46.8 | 50.4 slots | 16.94% |
| 150 | 318.2 ± 1.6 | 316.2 ± 2.7 | 2.0 slots | 0.63% |
| 200 | 319.0 ± 0.9 | 319.6 ± 0.8 | -0.6 slots | -0.19% |

## 3. Comparación de Probabilidad de Bloqueo

| Demandas | SP-FF | k-SP-MW | Reducción | Reducción (%) |
|---|---|---|---|---|
| 50 | 16.80% ± 3.71% | 16.80% ± 3.71% | 0.00 pp | 0.00% |
| 100 | 16.40% ± 2.24% | 13.00% ± 4.34% | 3.40 pp | 20.73% |
| 150 | 30.27% ± 1.16% | 18.40% ± 1.72% | 11.87 pp | 39.21% |
| 200 | 34.70% ± 3.36% | 24.00% ± 2.70% | 10.70 pp | 30.84% |

## 4. Comparación de Utilización de Espectro

| Demandas | SP-FF | k-SP-MW | Mejora | Mejora (%) |
|---|---|---|---|---|
| 50 | 12.80% | 13.32% | 0.51 pp | 4.02% |
| 100 | 24.68% | 27.80% | 3.12 pp | 12.64% |
| 150 | 29.12% | 38.48% | 9.36 pp | 32.13% |
| 200 | 34.11% | 45.60% | 11.48 pp | 33.66% |

## 5. Hallazgos Principales

- **Mayor reducción de watermark:** 50.4 slots (16.94%)
  - Carga: 100 demandas
- **Mayor reducción de bloqueo:** 11.87 pp (39.21%)
  - Carga: 150 demandas
- **Mayor mejora de utilización:** 11.48 pp (33.66%)
  - Carga: 200 demandas

## 6. Conclusión

El algoritmo **k-SP-MW** demuestra superioridad sobre **SP-FF** en:
- ✓ **Eficiencia espectral** (menor watermark)
- ✓ **Confiabilidad** (menor probabilidad de bloqueo)
- ✓ **Utilización** (mejor aprovechamiento de recursos)

**Recomendación:** Utilizar k-SP-MW en redes ópticas elásticas para optimizar recursos y mejorar QoS.