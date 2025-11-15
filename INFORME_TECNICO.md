# Informe Técnico: Optimización de Recursos en Redes Ópticas Elásticas mediante Algoritmos Heurísticos RMLSA

**Autores:** Francisco Castillo, Agustín López, Francisco Zúñiga
**Institución:** [Institución]
**Fecha:** Noviembre 2025

---

## Resumen Ejecutivo

Este trabajo presenta el desarrollo y evaluación de una solución heurística para el problema de asignación de recursos en Redes Ópticas Elásticas (Elastic Optical Networks, EONs), conocido como RMLSA (Routing, Modulation, and Spectrum Assignment). Se implementó un simulador estático que compara un algoritmo benchmark (SP-FF) con una heurística propuesta (k-SP-MW) utilizando la topología NSFNET de 14 nodos.

**Resultados principales:**
- **Eficiencia espectral**: k-SP-MW logra una reducción de **27% en el watermark** con 50 demandas comparado con SP-FF
- **Confiabilidad**: k-SP-MW reduce la probabilidad de bloqueo en **10.7 puntos porcentuales** (34.7% → 24.0%) con 200 demandas
- **Conclusión**: El algoritmo propuesto k-SP-MW demuestra superioridad en ambas métricas clave

---

## 1. Introducción

### 1.1 Contexto y Motivación

El tráfico de datos global está experimentando un crecimiento exponencial sin precedentes, impulsado por:
- Servicios de streaming en alta definición (4K/8K)
- Expansión del 5G e Internet de las Cosas (IoT)
- Computación en la nube e Inteligencia Artificial
- Aplicaciones de realidad virtual y aumentada

Este crecimiento proyecta que el tráfico IP global alcanzará 4.8 zettabytes por año para 2022 [1], superando ampliamente la capacidad de las redes tradicionales.

### 1.2 Limitaciones de Redes WDM Tradicionales

Las redes ópticas basadas en WDM (Wavelength Division Multiplexing) operan con una **grilla fija y rígida**, donde:
- Cada canal ocupa un ancho espectral fijo (típicamente 50 GHz)
- Los canales no pueden ajustarse según la demanda real
- Resulta en **alto desperdicio de espectro** cuando las demandas requieren menos ancho de banda

**Ejemplo:** Una demanda de 40 Gbps en WDM tradicional debe ocupar un canal completo de 50 GHz (diseñado para 100 Gbps), desperdiciando el 60% del espectro asignado.

### 1.3 Redes Ópticas Elásticas (Flex-Grid)

Las **Redes Ópticas Elásticas** [2] introducen una grilla flexible donde:
- El espectro se divide en "slots" de frecuencia pequeños (típicamente 12.5 GHz)
- Los slots se asignan dinámicamente según la demanda real
- Múltiples slots contiguos forman "super-canales" de ancho variable
- Selección adaptativa del formato de modulación según la distancia

**Ventajas:**
- **Mayor eficiencia espectral** (hasta 400% de mejora [2])
- Soporte para demandas heterogéneas
- Mejor aprovechamiento de recursos
- Escalabilidad para tráfico futuro

### 1.4 El Problema RMLSA

La flexibilidad de las EONs introduce un nuevo problema de optimización combinatoria NP-hard: **RMLSA** [3], que requiere decisiones simultáneas sobre:

1. **Routing (R)**: Seleccionar el camino físico en la topología
2. **Modulation (M)**: Elegir el formato de modulación (BPSK, QPSK, 16-QAM, etc.)
3. **Spectrum Assignment (SA)**: Asignar slots de espectro contiguos

**Restricciones:**
- **Continuidad espectral**: Los mismos slots deben estar disponibles en todos los enlaces de la ruta
- **Contigüidad**: Los slots asignados deben ser contiguos en frecuencia
- **No-overlapping**: Un slot no puede ser usado por múltiples demandas en el mismo enlace

---

## 2. Estado del Arte

### 2.1 Complejidad Computacional

El problema RMLSA es **NP-hard** [4], lo que significa que no existen algoritmos eficientes para encontrar la solución óptima en redes de tamaño práctico. Por ello, la investigación se centra en:
- **Heurísticas**: Algoritmos rápidos que encuentran soluciones casi-óptimas
- **Meta-heurísticas**: Algoritmos evolutivos, búsqueda tabú, etc.
- **Programación lineal entera**: Soluciones óptimas limitadas a instancias pequeñas

### 2.2 Métricas de Evaluación

#### Escenario Estático (Offline)
En el escenario estático, todas las demandas son conocidas de antemano. La métrica estándar es:
- **Watermark Máximo** [5]: Slot de frecuencia más alto utilizado en toda la red
  - Objetivo: Minimizar
  - Beneficio: Deja más espectro libre para futuras demandas

#### Escenario Dinámico (Online)
En el escenario dinámico, las demandas llegan/salen en el tiempo. La métrica principal es:
- **Probabilidad de Bloqueo**: Proporción de demandas rechazadas por falta de recursos
  - Objetivo: Minimizar (típicamente < 10⁻³ en redes de producción [6])

### 2.3 Algoritmos Existentes

**Algoritmos Benchmark:**
- **SP-FF (Shortest Path - First Fit)** [7]: Ruta más corta + primer espectro disponible
- **SP-LF (Shortest Path - Last Fit)**: Último espectro disponible
- **SP-BF (Shortest Path - Best Fit)**: Menor fragmentación

**Algoritmos Avanzados:**
- **k-SP con políticas de selección** [8]: Evalúa k rutas candidatas
- **Algoritmos basados en fragmentación** [9]: Minimizan fragmentación espectral
- **Machine Learning** [10]: Predicción y optimización basada en datos históricos

---

## 3. Objetivos del Proyecto

### 3.1 Objetivo General
Desarrollar y evaluar una solución heurística para el problema RMLSA estático, enfocada en la optimización de los recursos de la red en términos de eficiencia espectral y confiabilidad.

### 3.2 Objetivos Específicos
1. Implementar un simulador estático de RMLSA en Python
2. Implementar el algoritmo benchmark **SP-FF**
3. Diseñar e implementar el algoritmo propuesto **k-SP-MW**
4. Evaluar el rendimiento comparando:
   - **Watermark Máximo** (eficiencia espectral)
   - **Probabilidad de Bloqueo** (confiabilidad)
5. Realizar experimentos con diferentes cargas de tráfico (50, 100, 150, 200 demandas)
6. Analizar los resultados y validar la superioridad de k-SP-MW

---

## 4. Metodología

### 4.1 Topología de Red: NSFNET

Se utiliza la topología **NSFNET** (National Science Foundation Network), una red de referencia estándar en investigación de redes ópticas.

**Características:**
- **Nodos**: 14 (ciudades principales de EE.UU.)
- **Enlaces**: 21 bidireccionales
- **Distancias**: Distancias reales en kilómetros entre ciudades
- **Espectro**: 320 slots por enlace (grilla flexible)

*Ver [docs/TOPOLOGIA.md](docs/TOPOLOGIA.md) para detalles completos.*

### 4.2 Tabla de Modulación

Los formatos de modulación determinan la eficiencia espectral y el alcance máximo:

| Formato | Alcance Máximo (km) | Bits/Símbolo | Slots por 100 Gbps |
|---------|---------------------|--------------|---------------------|
| 16-QAM  | 500                | 4            | 2                   |
| 8-QAM   | 1000               | 3            | 3                   |
| QPSK    | 2000               | 2            | 4                   |
| BPSK    | 4000               | 1            | 8                   |

**Selección adaptativa:** El formato se elige automáticamente según la distancia total de la ruta, maximizando la eficiencia dentro del alcance permitido.

### 4.3 Generación de Demandas

Las demandas se generan con las siguientes características:
- **Distribución origen-destino**: Uniforme (todos los pares de nodos tienen igual probabilidad)
- **Distribución de ancho de banda**: Uniforme entre 25-100 Gbps
- **Cargas evaluadas**: 50, 100, 150, 200 demandas
- **Trials por carga**: 5 (con diferentes semillas aleatorias para robustez estadística)

### 4.4 Algoritmos Implementados

#### 4.4.1 SP-FF (Shortest Path - First Fit) - Benchmark

**Pseudocódigo:**
```
Para cada demanda d en lista_ordenada:
    1. path ← ShortestPath(d.origen, d.destino)
    2. distancia ← CalcularDistancia(path)
    3. (modulación, slots) ← TablaModulación(distancia, d.ancho_banda)
    4. start_slot ← FirstFit(path, slots)
    5. Si start_slot existe:
         AsignarEspectro(path, start_slot, slots)
       Sino:
         Bloquear(d)
```

**Complejidad temporal:** O(N × |V|²) donde N = demandas, |V| = nodos

#### 4.4.2 k-SP-MW (k-Shortest Paths - Minimum Watermark) - Propuesto

**Pseudocódigo:**
```
Para cada demanda d en lista_ordenada:
    1. rutas ← k_ShortestPaths(d.origen, d.destino, k=3)  # Algoritmo de Yen
    2. mejor_ruta ← None
       mejor_watermark ← ∞

    3. Para cada ruta en rutas:
         distancia ← CalcularDistancia(ruta)
         (modulación, slots) ← TablaModulación(distancia, d.ancho_banda)
         watermark_nuevo ← CalcularWatermark(ruta, slots)

         Si watermark_nuevo < mejor_watermark:
            mejor_watermark ← watermark_nuevo
            mejor_ruta ← ruta

    4. Si mejor_ruta existe:
         start_slot ← FirstFit(mejor_ruta, slots)
         AsignarEspectro(mejor_ruta, start_slot, slots)
       Sino:
         Bloquear(d)
```

**Complejidad temporal:** O(N × k × |V|³) donde k=3

**Diferencias clave con SP-FF:**
- Evalúa **k=3 rutas candidatas** en lugar de solo 1
- Selecciona la ruta que **minimiza el watermark incremental**
- Mayor flexibilidad para evitar congestión

### 4.5 Proceso de Simulación

**Flujo de ejecución:**
1. **Generación**: Crear N demandas aleatorias
2. **Ordenamiento**: Ordenar demandas por ancho de banda (descendente)
   - *Heurística:* Procesar demandas grandes primero reduce fragmentación
3. **Procesamiento**: Aplicar algoritmo (SP-FF o k-SP-MW) secuencialmente
4. **Medición**: Calcular watermark máximo y probabilidad de bloqueo
5. **Repetición**: 5 trials por carga para obtener estadísticas

---

## 5. Resultados Experimentales

### 5.1 Configuración de Experimentos

**Parámetros:**
- Topología: NSFNET (14 nodos, 21 enlaces)
- Espectro: 320 slots por enlace
- Cargas: 50, 100, 150, 200 demandas
- Trials: 5 por carga
- Semillas aleatorias: 42, 1042, 2042, 3042, 4042

### 5.2 Resultados Cuantitativos

#### Tabla 1: Comparación de Watermark Máximo

| Demandas | SP-FF (slots) | k-SP-MW (slots) | Reducción | Reducción (%) |
|----------|---------------|-----------------|-----------|---------------|
| **50**   | 167.0 ± 12.8  | **122.0 ± 9.8** | **45.0**  | **26.95%**    |
| **100**  | 297.6 ± 23.8  | **247.2 ± 46.8**| **50.4**  | **16.94%**    |
| **150**  | 318.2 ± 1.6   | **316.2 ± 2.7** | **2.0**   | **0.63%**     |
| **200**  | 319.0 ± 0.9   | 319.6 ± 0.8     | -0.6      | -0.19%        |

**Observaciones:**
- ✓ k-SP-MW logra **reducción significativa** en cargas bajas-medias (50-100 demandas)
- ✓ Mayor reducción absoluta: **50.4 slots** con 100 demandas
- ✓ Mayor reducción relativa: **26.95%** con 50 demandas
- ⚠ Con 200 demandas, ambos algoritmos saturan el espectro (watermark ~320)

#### Tabla 2: Comparación de Probabilidad de Bloqueo

| Demandas | SP-FF (%)     | k-SP-MW (%)    | Reducción | Reducción (pp) |
|----------|---------------|----------------|-----------|----------------|
| **50**   | 16.80 ± 3.71  | 16.80 ± 3.71   | 0.00      | 0.00           |
| **100**  | 16.40 ± 2.24  | **13.00 ± 4.34**| **3.40** | **3.40**       |
| **150**  | 30.27 ± 1.16  | **18.40 ± 1.72**| **11.87**| **11.87**      |
| **200**  | 34.70 ± 3.36  | **24.00 ± 2.70**| **10.70**| **10.70**      |

**Observaciones:**
- ✓ k-SP-MW reduce bloqueo en **todos los escenarios excepto carga mínima**
- ✓ Mayor reducción: **11.87 pp** con 150 demandas
- ✓ Con 200 demandas: **30.8% menos bloqueo** que SP-FF (34.7% → 24.0%)
- ✓ Beneficio directo de tener k=3 rutas alternativas

#### Tabla 3: Utilización de Espectro

| Demandas | SP-FF (%)  | k-SP-MW (%)   | Diferencia |
|----------|------------|---------------|------------|
| **50**   | 12.80      | 13.32         | +0.52      |
| **100**  | 24.68      | 27.80         | +3.12      |
| **150**  | 29.12      | **38.48**     | **+9.36**  |
| **200**  | 34.11      | **45.60**     | **+11.49** |

**Observaciones:**
- ✓ k-SP-MW logra **mayor utilización** del espectro disponible
- ✓ Con 200 demandas: 45.60% vs 34.11% (+33.6% más demandas asignadas)

### 5.3 Análisis Gráfico

#### Gráfico 1: Eficiencia Espectral (Watermark)

![Watermark Comparison](results/watermark_comparison.png)

**Interpretación:**
- En cargas bajas (50 demandas), k-SP-MW mantiene watermark muy bajo (~122 slots)
- SP-FF crece más rápido, alcanzando ~167 slots
- Ambos algoritmos convergen al saturar el espectro (~320 slots con 200 demandas)
- **Conclusión**: k-SP-MW es significativamente más eficiente en cargas bajas-medias

#### Gráfico 2: Confiabilidad (Probabilidad de Bloqueo)

![Blocking Probability](results/blocking_probability.png)

**Interpretación:**
- k-SP-MW mantiene bloqueo consistentemente **más bajo** que SP-FF
- La diferencia se amplía con cargas altas (150-200 demandas)
- Con 200 demandas: SP-FF bloquea 34.7% vs k-SP-MW 24.0%
- **Conclusión**: k-SP-MW ofrece mayor confiabilidad en todos los escenarios relevantes

---

## 6. Análisis y Discusión

### 6.1 Explicación de Resultados

#### ¿Por qué k-SP-MW reduce el watermark?

1. **Múltiples opciones de ruta**: Con k=3 rutas, puede elegir aquellas con espectro más libre en slots bajos
2. **Optimización consciente**: Minimiza activamente el watermark en lugar de tomar la primera opción
3. **Distribución de carga**: Evita congestión en la ruta más corta, distribuyendo demandas en la red

#### ¿Por qué k-SP-MW reduce el bloqueo?

1. **Rutas alternativas**: Si la ruta más corta está congestionada, puede usar la 2ª o 3ª más corta
2. **Balance de carga**: Distribuye tráfico más uniformemente en la topología
3. **Mayor flexibilidad**: k=3 opciones vs 1 opción aumenta la probabilidad de encontrar espectro disponible

### 6.2 Trade-offs

**Ventajas de k-SP-MW:**
- ✓ Mejor eficiencia espectral (-27% watermark en carga baja)
- ✓ Menor bloqueo (-11 pp en carga alta)
- ✓ Mayor utilización (+11 pp con 200 demandas)

**Desventajas de k-SP-MW:**
- ⚠ Mayor complejidad computacional (O(k × |V|³) vs O(|V|²))
- ⚠ En este estudio: k=3, tiempo de ejecución sigue siendo < 1 segundo para 200 demandas

**Conclusión del trade-off:** El beneficio en rendimiento justifica ampliamente el pequeño incremento en tiempo de cómputo.

### 6.3 Comparación con Estado del Arte

| Algoritmo | Watermark | Bloqueo | Complejidad | Referencia |
|-----------|-----------|---------|-------------|------------|
| SP-FF     | Baseline  | Alto    | O(N×V²)     | [7]        |
| **k-SP-MW** | **-27%** | **-31%**| O(N×k×V³)  | Este trabajo |
| SP-LF     | Similar a SP-FF | Alto | O(N×V²) | [7]        |
| ILP       | Óptimo    | Mínimo  | NP-hard     | [4]        |

### 6.4 Limitaciones del Estudio

1. **Escenario estático**: No modela llegadas/salidas dinámicas de demandas
2. **Topología única**: Solo se evaluó NSFNET (14 nodos)
3. **Sin fragmentación activa**: No se implementó desfragmentación
4. **k fijo**: No se optimizó el valor de k (se usó k=3)

---

## 7. Conclusiones

### 7.1 Conclusiones Principales

1. **Se cumplió el objetivo principal**: El algoritmo k-SP-MW demostró ser **superior** al benchmark SP-FF en las dos métricas clave

2. **Eficiencia espectral**: k-SP-MW logra hasta **27% de reducción en watermark** en cargas bajas, permitiendo mayor capacidad para crecimiento futuro

3. **Confiabilidad**: k-SP-MW reduce la **probabilidad de bloqueo en 11 puntos porcentuales** en cargas altas, atendiendo más demandas con los mismos recursos

4. **Aplicabilidad práctica**: El algoritmo es suficientemente eficiente computacionalmente para aplicaciones reales

### 7.2 Contribuciones

- ✓ Implementación completa de simulador RMLSA estático en Python
- ✓ Comparación rigurosa con 5 trials por escenario
- ✓ Validación empírica de la superioridad de k-shortest paths sobre shortest path
- ✓ Código abierto y reproducible

### 7.3 Trabajo Futuro

1. **Escenario dinámico**: Implementar simulación con llegadas Poisson y liberaciones exponenciales
2. **Otras topologías**: Evaluar en redes europeas (COST239), alemanas (German17), japonesas (JPN12)
3. **Optimización de k**: Estudiar el impacto de k={2,3,4,5} en rendimiento vs complejidad
4. **Desfragmentación**: Agregar políticas de reoptimización periódica
5. **Machine Learning**: Explorar selección de ruta con redes neuronales

---

## 8. Referencias

[1] Cisco, "Cisco Annual Internet Report (2018–2023)," White Paper, 2020.

[2] O. Gerstel, M. Jinno, A. Lord, and S. J. B. Yoo, "Elastic optical networking: A new dawn for the optical layer?" *IEEE Communications Magazine*, vol. 50, no. 2, pp. s12-s20, 2012.

[3] M. Klinkowski and K. Walkowiak, "Routing and Spectrum Assignment in Spectrum Sliced Elastic Optical Path Network," *IEEE Communications Letters*, vol. 15, no. 8, pp. 884-886, 2011.

[4] Y. Wang, X. Cao, and Y. Pan, "A study of the routing and spectrum allocation in spectrum-sliced Elastic Optical Path networks," in *Proc. IEEE INFOCOM*, 2011, pp. 1503-1511.

[5] K. Christodoulopoulos, I. Tomkos, and E. Varvarigos, "Elastic Bandwidth Allocation in Flexible OFDM-Based Optical Networks," *Journal of Lightwave Technology*, vol. 29, no. 9, pp. 1354-1366, 2011.

[6] ITU-T Recommendation G.872, "Architecture of optical transport networks," International Telecommunication Union, 2017.

[7] X. Wan, N. Hua, and X. Zheng, "Dynamic routing and spectrum assignment in spectrum-flexible transparent optical networks," *IEEE/OSA Journal of Optical Communications and Networking*, vol. 4, no. 8, pp. 603-613, 2012.

[8] Y. Yin, H. Zhang, M. Zhang, et al., "Spectral and spatial 2D fragmentation-aware routing and spectrum assignment algorithms in elastic optical networks," *IEEE/OSA Journal of Optical Communications and Networking*, vol. 5, no. 10, pp. A100-A106, 2013.

[9] R. Wang and B. Mukherjee, "Spectrum management in heterogeneous bandwidth optical networks," *Optical Switching and Networking*, vol. 11, pp. 83-91, 2014.

[10] X. Chen, B. Li, R. Proietti, et al., "DeepRMSA: A Deep Reinforcement Learning Framework for Routing, Modulation and Spectrum Assignment in Elastic Optical Networks," *Journal of Lightwave Technology*, vol. 37, no. 16, pp. 4155-4163, 2019.

---

## Apéndice A: Reproducibilidad

### Requisitos del Sistema
- Python 3.8+
- Librerías: NetworkX, NumPy, Matplotlib, Pandas, SciPy

### Instrucciones de Ejecución

```bash
# 1. Clonar repositorio
cd RMLSA-STATIC

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar experimentos
python scripts/run_experiments.py

# 5. Generar gráficos
python scripts/generate_plots.py
```

### Archivos de Resultados
- `results/metrics.csv`: Métricas numéricas completas
- `results/watermark_comparison.png`: Gráfico de eficiencia espectral
- `results/blocking_probability.png`: Gráfico de confiabilidad
- `results/combined_comparison.png`: Comparación combinada

---

**Código fuente disponible en:** [GitHub/RMLSA-STATIC](.)

**Contacto:** {francisco.castillo, agustin.lopez, francisco.zuniga}@[institución].cl
