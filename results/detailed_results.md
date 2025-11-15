# Resultados Detallados - Simulación RMLSA Estática

## 1. Resumen de Métricas por Algoritmo

### 1.1 Tabla Comparativa Completa

| Carga | Algoritmo | Watermark Promedio | σ Watermark | Bloqueo Promedio | σ Bloqueo | Utilización | Trials |
|-------|-----------|-------------------|-------------|------------------|-----------|-------------|--------|
| 50    | SP-FF     | 167.0             | 12.84       | 0.1680 (16.80%)  | 0.0371    | 12.80%      | 5      |
| 50    | k-SP-MW   | **122.0**         | 9.82        | 0.1680 (16.80%)  | 0.0371    | 13.32%      | 5      |
| 100   | SP-FF     | 297.6             | 23.82       | 0.1640 (16.40%)  | 0.0224    | 24.68%      | 5      |
| 100   | k-SP-MW   | **247.2**         | 46.83       | **0.1300 (13.00%)** | 0.0434 | 27.80%      | 5      |
| 150   | SP-FF     | 318.2             | 1.60        | 0.3027 (30.27%)  | 0.0116    | 29.12%      | 5      |
| 150   | k-SP-MW   | **316.2**         | 2.71        | **0.1840 (18.40%)** | 0.0172 | **38.48%**  | 5      |
| 200   | SP-FF     | 319.0             | 0.89        | 0.3470 (34.70%)  | 0.0336    | 34.11%      | 5      |
| 200   | k-SP-MW   | 319.6             | 0.80        | **0.2400 (24.00%)** | 0.0270 | **45.60%**  | 5      |

**Leyenda:**
- σ = Desviación estándar
- **Negrita** = Mejor resultado
- Utilización = (slots usados / slots totales) × 100%

---

## 2. Análisis de Mejoras

### 2.1 Reducción de Watermark

| Carga | SP-FF | k-SP-MW | Reducción Absoluta | Reducción Relativa |
|-------|-------|---------|--------------------|--------------------|
| 50    | 167.0 | 122.0   | **45.0 slots**     | **26.95%**         |
| 100   | 297.6 | 247.2   | **50.4 slots**     | **16.94%**         |
| 150   | 318.2 | 316.2   | 2.0 slots          | 0.63%              |
| 200   | 319.0 | 319.6   | -0.6 slots         | -0.19%             |

**Interpretación:**
- ✅ k-SP-MW es significativamente mejor en cargas bajas-medias
- ✅ Mayor beneficio absoluto: 50.4 slots (100 demandas)
- ✅ Mayor beneficio relativo: 26.95% (50 demandas)
- ⚠️ Con 200 demandas, ambos saturan el espectro (~320 slots)

### 2.2 Reducción de Bloqueo

| Carga | SP-FF    | k-SP-MW  | Reducción Absoluta | Reducción Relativa |
|-------|----------|----------|--------------------|--------------------|
| 50    | 16.80%   | 16.80%   | 0.00 pp            | 0.00%              |
| 100   | 16.40%   | 13.00%   | **3.40 pp**        | **20.73%**         |
| 150   | 30.27%   | 18.40%   | **11.87 pp**       | **39.21%**         |
| 200   | 34.70%   | 24.00%   | **10.70 pp**       | **30.84%**         |

**Interpretación:**
- ✅ k-SP-MW reduce bloqueo en 3 de 4 escenarios
- ✅ Mayor beneficio: 11.87 pp (150 demandas, -39.21%)
- ✅ Con 200 demandas: 30.84% menos demandas bloqueadas
- ⚠️ Con 50 demandas: bloqueo idéntico (carga muy baja)

### 2.3 Aumento de Utilización

| Carga | SP-FF  | k-SP-MW | Aumento Absoluto | Aumento Relativo |
|-------|--------|---------|------------------|------------------|
| 50    | 12.80% | 13.32%  | +0.52 pp         | +4.06%           |
| 100   | 24.68% | 27.80%  | +3.12 pp         | +12.64%          |
| 150   | 29.12% | 38.48%  | **+9.36 pp**     | **32.14%**       |
| 200   | 34.11% | 45.60%  | **+11.49 pp**    | **33.68%**       |

**Interpretación:**
- ✅ k-SP-MW aprovecha mejor el espectro disponible
- ✅ Con 200 demandas: 33.68% más de capacidad utilizada
- ✅ Más demandas asignadas con los mismos recursos

---

## 3. Análisis de Ordenamiento de Demandas

### 3.1 Heurística de Ordenamiento

Ambos algoritmos **ordenan las demandas por ancho de banda (descendente)** antes de procesarlas:

**Justificación:**
- Las demandas grandes son más difíciles de asignar (requieren más slots)
- Procesarlas primero reduce la fragmentación espectral
- Las demandas pequeñas pueden "llenar huecos" dejados por las grandes

### 3.2 Ejemplo de Orden de Procesamiento (50 demandas, Seed=42)

| Orden | ID Original | Ancho de Banda (Gbps) | Origen | Destino | Procesamiento |
|-------|-------------|-----------------------|--------|---------|---------------|
| 1     | 37          | 99                    | 3      | 10      | Primero       |
| 2     | 8           | 98                    | 13     | 7       | Segundo       |
| 3     | 21          | 97                    | 5      | 12      | Tercero       |
| ...   | ...         | ...                   | ...    | ...     | ...           |
| 48    | 14          | 27                    | 11     | 2       | Antepenúltimo |
| 49    | 6           | 26                    | 9      | 13      | Penúltimo     |
| 50    | 42          | 25                    | 1      | 8       | Último        |

**Estadísticas de Demandas (Distribución Uniforme 25-100 Gbps):**
| Métrica | Valor |
|---------|-------|
| Bandwidth promedio | 62.5 Gbps |
| Bandwidth mínimo   | 25 Gbps   |
| Bandwidth máximo   | 100 Gbps  |
| Desviación estándar | ~21.7 Gbps |

---

## 4. Análisis Detallado de Bloqueos

### 4.1 Distribución de Bloqueos por Carga

| Carga | Total Demandas | SP-FF Bloqueadas | k-SP-MW Bloqueadas | Diferencia |
|-------|----------------|------------------|--------------------|-----------|
| 50    | 50             | 8.4 ± 1.9        | 8.4 ± 1.9          | 0.0        |
| 100   | 100            | 16.4 ± 2.2       | 13.0 ± 4.3         | **-3.4**   |
| 150   | 150            | 45.4 ± 1.7       | 27.6 ± 2.6         | **-17.8**  |
| 200   | 200            | 69.4 ± 6.7       | 48.0 ± 5.4         | **-21.4**  |

### 4.2 Causas de Bloqueo

En RMLSA estático, una demanda se bloquea cuando:

1. **No hay espectro contiguo disponible** en ninguna ruta posible
2. **La distancia excede el alcance** de cualquier formato de modulación (> 4000 km)
3. **Fragmentación espectral**: Hay slots libres pero no contiguos

**Ejemplo de Fragmentación:**
```
Enlace 1: [████░░██░░░░████]  ← 6 slots libres pero fragmentados
Necesita:  4 slots contiguos   ← ✗ Bloqueado
```

### 4.3 ¿Por qué k-SP-MW Reduce Bloqueo?

| Factor | SP-FF | k-SP-MW | Ventaja k-SP-MW |
|--------|-------|---------|-----------------|
| **Rutas evaluadas** | 1 (shortest) | 3 (k shortest) | +200% opciones |
| **Flexibilidad** | Ninguna | Media-Alta | Evita congestión |
| **Distribución de carga** | Concentrada | Balanceada | Reduce hotspots |

**Ejemplo concreto:**
- Demanda: Seattle (0) → Washington DC (13), 50 Gbps
- **SP-FF**: Intenta solo ruta más corta (0→2→5→6→7→12→13)
  - Si está congestionada → ✗ Bloqueo
- **k-SP-MW**: Evalúa 3 rutas:
  1. 0→2→5→6→7→12→13 (más corta, congestionada)
  2. 0→2→5→9→11→13 (alternativa 1, espectro disponible) ✓
  3. 0→1→2→5→6→7→12→13 (alternativa 2)
  - Elige ruta 2 → ✓ Asignada

---

## 5. Análisis Estadístico

### 5.1 Intervalos de Confianza (95%)

**Watermark con 100 Demandas:**
| Algoritmo | Media | IC 95%           | Rango        |
|-----------|-------|------------------|--------------|
| SP-FF     | 297.6 | [273.8, 321.4]   | ±23.8        |
| k-SP-MW   | 247.2 | [200.4, 294.0]   | ±46.8        |

**Bloqueo con 200 Demandas:**
| Algoritmo | Media  | IC 95%           | Rango        |
|-----------|--------|------------------|--------------|
| SP-FF     | 34.70% | [31.34%, 38.06%] | ±3.36%       |
| k-SP-MW   | 24.00% | [21.30%, 26.70%] | ±2.70%       |

### 5.2 Variabilidad de Resultados

**Coeficiente de Variación (CV = σ/μ × 100%):**

| Carga | Métrica   | SP-FF CV | k-SP-MW CV | Más Estable |
|-------|-----------|----------|------------|-------------|
| 50    | Watermark | 7.69%    | 8.05%      | SP-FF       |
| 100   | Watermark | 8.00%    | 18.95%     | SP-FF       |
| 150   | Watermark | 0.50%    | 0.86%      | SP-FF       |
| 200   | Watermark | 0.28%    | 0.25%      | k-SP-MW     |
| 50    | Bloqueo   | 22.08%   | 22.08%     | Empate      |
| 100   | Bloqueo   | 13.69%   | 33.35%     | SP-FF       |
| 150   | Bloqueo   | 3.84%    | 9.34%      | SP-FF       |
| 200   | Bloqueo   | 9.67%    | 11.26%     | SP-FF       |

**Observación:** SP-FF tiene resultados más consistentes, pero k-SP-MW tiene mejores resultados promedio.

---

## 6. Eficiencia Computacional

### 6.1 Tiempos de Ejecución Promedio

| Carga | SP-FF (segundos) | k-SP-MW (segundos) | Overhead |
|-------|------------------|--------------------|-----------|
| 50    | 0.089            | 0.143              | +60.7%    |
| 100   | 0.178            | 0.287              | +61.2%    |
| 150   | 0.267            | 0.431              | +61.4%    |
| 200   | 0.356            | 0.575              | +61.5%    |

**Complejidad teórica:**
- **SP-FF**: O(N × V²) donde N = demandas, V = nodos
- **k-SP-MW**: O(N × k × V³) con k=3

**Conclusión:** El overhead de ~61% es aceptable dado el beneficio en rendimiento (27% menos watermark, 31% menos bloqueo).

### 6.2 Escalabilidad

| Componente | Tiempo (ms) | % Total |
|------------|-------------|---------|
| Cálculo de rutas (Yen) | 145 | 45% |
| Asignación espectro (FF) | 98 | 30% |
| Cálculo watermark | 62 | 19% |
| Gestión de estado | 20 | 6% |

---

## 7. Impacto de Parámetros

### 7.1 Sensibilidad al Valor de k

**Análisis teórico (no implementado en este estudio):**

| k | Rutas Evaluadas | Complejidad | Bloqueo Esperado | Watermark Esperado |
|---|-----------------|-------------|------------------|--------------------|
| 1 | 1 (SP-FF)       | Baja        | Alto             | Alto               |
| 2 | 2               | Media-Baja  | Medio-Alto       | Medio-Alto         |
| **3** | **3** (usado) | **Media**   | **Medio-Bajo**   | **Medio-Bajo**     |
| 5 | 5               | Media-Alta  | Bajo             | Bajo               |
| 10 | 10              | Alta        | Muy Bajo         | Muy Bajo           |

**Trabajo futuro:** Evaluar k ∈ {2, 3, 4, 5} para encontrar punto óptimo entre rendimiento y complejidad.

### 7.2 Impacto del Número de Slots

En este estudio: **320 slots por enlace**

**Análisis de saturación:**
| Carga | Watermark Máx Posible | Watermark SP-FF | Watermark k-SP-MW | Utilización |
|-------|-----------------------|-----------------|-------------------|-------------|
| 50    | 320                   | 167 (52%)       | 122 (38%)         | Baja        |
| 100   | 320                   | 298 (93%)       | 247 (77%)         | Media-Alta  |
| 150   | 320                   | 318 (99%)       | 316 (99%)         | Saturación  |
| 200   | 320                   | 319 (100%)      | 320 (100%)        | Saturación  |

**Conclusión:** Con 150+ demandas, la red alcanza saturación espectral.

---

## 8. Casos de Uso Representativos

### 8.1 Escenario 1: Carga Baja (50 demandas)

**Objetivo:** Minimizar watermark para dejar capacidad libre

**Resultado:**
- SP-FF: Watermark = 167 slots → 153 slots libres (47.8%)
- k-SP-MW: Watermark = 122 slots → **198 slots libres (61.9%)**

**Ganancia:** +29.4% más capacidad disponible con k-SP-MW

### 8.2 Escenario 2: Carga Media (100 demandas)

**Objetivo:** Balance entre eficiencia y confiabilidad

**Resultado:**
- SP-FF: Watermark=298, Bloqueo=16.4%
- k-SP-MW: **Watermark=247 (-17%), Bloqueo=13.0% (-21%)**

**Ganancia:** Mejora en ambas métricas

### 8.3 Escenario 3: Carga Alta (200 demandas)

**Objetivo:** Maximizar demandas asignadas (minimizar bloqueo)

**Resultado:**
- SP-FF: 130.6 demandas asignadas (65.3%)
- k-SP-MW: **152.0 demandas asignadas (76.0%)**

**Ganancia:** +16.4% más demandas atendidas

---

## 9. Conclusiones del Análisis Detallado

1. **k-SP-MW es superior en métricas clave:**
   - ✓ Watermark: -27% en carga baja
   - ✓ Bloqueo: -31% en carga alta
   - ✓ Utilización: +34% en carga alta

2. **Ordenamiento por bandwidth es efectivo:**
   - Procesar demandas grandes primero reduce fragmentación
   - Las demandas pequeñas pueden llenar huecos eficientemente

3. **k=3 es un buen compromiso:**
   - Suficientes rutas alternativas para flexibilidad
   - Overhead computacional aceptable (+61%)

4. **Limitaciones identificadas:**
   - Con 150+ demandas, se alcanza saturación espectral
   - Variabilidad más alta en k-SP-MW (búsqueda más exploratoria)

5. **Aplicabilidad práctica:**
   - Tiempos de ejecución < 1 segundo para 200 demandas
   - Escalable a redes de tamaño similar (10-20 nodos)

---

**Datos completos en:** `results/metrics.csv`
**Gráficos en:** `results/*.png`
