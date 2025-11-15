Claro, aquí tienes un desglose razonado del proyecto, incorporando la información de la presentación y el feedback recibido, en el formato Markdown solicitado.

---

# Optimización de Recursos en Redes Ópticas Elásticas (EONs)

[cite_start]**Autores:** Francisco Castillo, Agustín López, Francisco Zúñiga [cite: 5, 6, 7]

**Resumen del Proyecto:** Este trabajo desarrolla y evalúa una solución heurística para el problema de asignación de recursos en Redes Ópticas Elásticas (EONs), conocido como RMLSA (Routing, Modulation, and Spectrum Assignment). [cite_start]El objetivo es optimizar el uso de los recursos de la red [cite: 39] comparando un algoritmo *benchmark* (SP-FF) con una heurística ad-hoc propuesta (k-SP-MW). [cite_start]La simulación mide la eficiencia del espectro (Watermark Máximo) y la Tasa de Bloqueo bajo diferentes cargas de tráfico en la topología NSFNET[cite: 41, 42].

---

## 1. Contexto y Problema

[cite_start]Vivimos una explosión sin precedentes en el tráfico de datos global [cite: 18, 19][cite_start], impulsada por servicios como *streaming 4K/8K*, la expansión del 5G e IoT, y el auge de la Computación en la Nube e Inteligencia Artificial[cite: 21, 22, 23].

[cite_start]La columna vertebral que soporta esta demanda son las redes ópticas[cite: 24]. [cite_start]Sin embargo, las redes WDM (Wavelength Division Multiplexing) tradicionales operan en una **grilla fija y rígida**, lo que genera un **alto desperdicio de espectro** al asignar "carriles" de tamaño fijo sin importar la demanda real[cite: 26, 27].

[cite_start]La evolución natural son las **Redes Ópticas Elásticas (Flex-Grid)**, que permiten una grilla flexible con "slots" a medida [cite: 28, 30, 31][cite_start], ofreciendo una eficiencia y optimización muy superiores[cite: 32, 33].

[cite_start]Esta flexibilidad introduce un nuevo y complejo desafío de optimización: el problema **RMLSA (Routing, Modulation, and Spectrum Assignment)**[cite: 34, 35, 47, 48]. [cite_start]Para cada solicitud de conexión, se debe decidir de forma óptima[cite: 35]:
1.  **Ruta (Routing):** El camino físico que tomará la luz.
2.  **Modulación (Modulation):** El formato de modulación (ej. QPSK, 16-QAM) que define cuántos datos se transmiten, lo cual depende de la distancia de la ruta.
3.  [cite_start]**Asignación de Espectro (Spectrum Assignment):** Qué bloque de frecuencias específico (slots) se asignará a esa conexión en esa ruta[cite: 36, 49, 52, 53].

---

## 2. Estado del Arte y Justificación

El problema RMLSA es un problema de optimización combinatoria **NP-hard**, lo que significa que no existen soluciones exactas eficientes para redes de gran tamaño. [cite_start]Por ello, la investigación se centra en desarrollar **heurísticas y algoritmos** para encontrar soluciones casi-óptimas de forma rápida[cite: 54].

* [cite_start]**Justificación de Métricas (Watermark):** Para el escenario **estático** (donde se asigna un conjunto fijo de demandas), la métrica estándar de la industria y la academia para medir la eficiencia del espectro es el **Watermark Máximo**[cite: 112].
    * [cite_start]**Definición:** Es el slot de frecuencia más alto utilizado en *toda* la red después de asignar todas las demandas[cite: 112].
    * **Objetivo:** Minimizarlo. [cite_start]Un watermark bajo significa que la red está usando el espectro de manera más compacta y eficiente[cite: 113], dejando más capacidad libre para futuras demandas.
* [cite_start]**Algoritmo *Benchmark*:** Como punto de referencia, se implementa el algoritmo **SP-FF (Shortest Path - First Fit)**[cite: 41], una heurística común que selecciona la ruta más corta y le asigna el primer bloque de espectro disponible.

---

## 3. Objetivos del Proyecto

### Objetivo General
[cite_start]Desarrollar y evaluar una solución heurística para el problema RMLSA estático, enfocada en la optimización de los recursos de la red[cite: 39].

### Objetivos Específicos
* [cite_start]Implementar el algoritmo *benchmark* **SP-FF** y una heurística ad-hoc propuesta (denominada en los resultados como **k-SP-MW**)[cite: 41, 115].
* [cite_start]Comparar el rendimiento de ambas soluciones midiendo el **Watermark Máximo** del espectro[cite: 42].
* [cite_start]Evaluar el impacto en la **Tasa de Bloqueo**[cite: 58].
* [cite_start]Realizar las simulaciones bajo diferentes cargas de tráfico en la topología **NSFNET**[cite: 42].

---

## 4. Arquitectura y Metodología del Simulador

[cite_start]El proyecto se basa en un simulador [cite: 55] cuyo flujo de proceso y metodología se describen a continuación:

### Entradas del Simulador
1.  [cite_start]**Topología de Red:** Se utiliza la topología NSFNET, que define los nodos y las distancias de los enlaces [cite: 59, 76-110].
2.  [cite_start]**Set de Demandas:** Un conjunto de solicitudes de conexión, cada una con un (Origen, Destino, Ancho de Banda)[cite: 62].
3.  **Parámetros de Simulación:**
    * [cite_start]Tabla de Modulación (define la relación entre distancia y formato de modulación/slots necesarios)[cite: 63].
    * [cite_start]Parámetro $k=3$ para el algoritmo de k-rutas[cite: 64].
4.  **Distribución de Carga (Feedback):** Para simular el aumento de tráfico, las demandas se generan siguiendo un **proceso de Poisson**, lo que resulta en tiempos entre llegadas con **distribución exponencial** (relacionado con el factor $\mu$ del feedback). Esto es un estándar para modelar tráfico en telecomunicaciones.

### Proceso del Algoritmo (Paso a Paso)

[cite_start]El simulador procesa las demandas secuencialmente[cite: 65, 67]:

1.  [cite_start]**Ordenar Demandas:** Las demandas se ordenan de mayor a menor ancho de banda solicitado[cite: 66]. Esto es una heurística clave, ya que prioriza las demandas más "difíciles" de asignar.
2.  [cite_start]**Bucle por Demanda:** Para cada demanda en la lista ordenada[cite: 67, 68]:
3.  **Cálculo de Rutas (Routing):**
    * [cite_start]Se utiliza el **Algoritmo de Yen** para encontrar las $k$ rutas más cortas (Shortest Paths) entre el origen y el destino de la demanda[cite: 70].
    * [cite_start]Se utiliza $k=3$[cite: 64], un valor que ofrece un buen equilibrio entre tener múltiples opciones de ruta (para evitar congestión) y mantener una complejidad computacional manejable.
4.  [cite_start]**Evaluación de Rutas:** Se evalúa el "Costo-Watermark" para cada una de las $k=3$ rutas[cite: 71, 72].
5.  [cite_start]**Selección de Mejor Ruta:** Se selecciona la mejor ruta según la heurística k-SP-MW (que busca minimizar el *watermark* incremental)[cite: 73].
6.  **Asignación de Recursos (Modulación y Espectro):**
    * [cite_start]**Modulación (M):** Basado en la distancia total de la ruta seleccionada, se consulta la Tabla de Modulación [cite: 63] para determinar el formato de modulación y, por ende, cuántos *slots* de espectro contiguos se necesitan.
    * **Asignación de Espectro (SA):** Se utiliza una política **First-Fit (FF)**. El algoritmo barre el espectro desde el *slot* 0 hacia arriba y asigna el **primer bloque contiguo de *slots* disponible** que cumpla con el ancho de banda requerido.
7.  [cite_start]**Actualizar Estado:** El estado de la red se actualiza, marcando los *slots* asignados como "ocupados" en todos los enlaces de la ruta seleccionada[cite: 74, 75].

### Salidas (Métricas de Rendimiento)
* [cite_start]**Métrica Principal:** Watermark Máximo Final[cite: 57].
* [cite_start]**Métrica Secundaria:** Tasa de Bloqueo (el porcentaje de demandas que no pudieron ser asignadas por falta de recursos)[cite: 58].

---

## 5. Resultados y Conclusiones

Los gráficos de resultados comparan el algoritmo *benchmark* (SPFF) con la heurística propuesta (k-SP-MW).

### Comparación de Watermark (Métrica Principal)

**Resultados Experimentales:**

| Carga (Demandas) | SP-FF (slots) | k-SP-MW (slots) | Reducción | Reducción (%) |
|------------------|---------------|-----------------|-----------|---------------|
| 50               | 167.0 ± 12.8  | **122.0 ± 9.8** | **45.0**  | **26.95%**    |
| 100              | 297.6 ± 23.8  | **247.2 ± 46.8**| **50.4**  | **16.94%**    |
| 150              | 318.2 ± 1.6   | **316.2 ± 2.7** | 2.0       | 0.63%         |
| 200              | 319.0 ± 0.9   | 319.6 ± 0.8     | -0.6      | -0.19%        |

* **Observación:** En cargas de demanda bajas (50 demandas), el algoritmo **k-SP-MW logra un watermark significativamente más bajo** (122 vs 167 slots, **-26.95%**). La mayor reducción absoluta se observa con 100 demandas (**50.4 slots**). En cargas altas (150-200), ambos algoritmos convergen cerca del límite máximo (320 slots), ya que la red se satura.
* **Conclusión:** La heurística propuesta **cumple el objetivo** de optimizar y compactar el espectro de manera más eficiente en escenarios de carga baja-media, logrando reducciones de hasta **27%** en el uso de espectro.

### Comparación de Probabilidad de Bloqueo (Métrica Secundaria)

**Resultados Experimentales:**

| Carga (Demandas) | SP-FF (%)     | k-SP-MW (%)    | Reducción | Reducción (%) |
|------------------|---------------|----------------|-----------|---------------|
| 50               | 16.80 ± 3.71  | 16.80 ± 3.71   | 0.00 pp   | 0.00%         |
| 100              | 16.40 ± 2.24  | **13.00 ± 4.34**| **3.40 pp**| **20.73%**   |
| 150              | 30.27 ± 1.16  | **18.40 ± 1.72**| **11.87 pp**| **39.21%**  |
| 200              | 34.70 ± 3.36  | **24.00 ± 2.70**| **10.70 pp**| **30.84%**  |

* **Observación:** El algoritmo **k-SP-MW tiene una probabilidad de bloqueo consistentemente más baja** que el SP-FF en los escenarios de carga media-alta (100 a 200 demandas). La mayor reducción se observa con 150 demandas (**11.87 puntos porcentuales**, equivalente a **-39.21%**).
* **Conclusión:** Este es un beneficio adicional clave. Al tener $k=3$ rutas para elegir, la heurística k-SP-MW puede "esquivar" enlaces congestionados que el SP-FF (que solo prueba la ruta más corta) no puede.

### Contextualización (Respuesta al Feedback)
El feedback indicaba que los resultados de bloqueo en la industria buscan valores de $P_b \approx 10^{-3}$. Los gráficos muestran valores de bloqueo más altos, lo cual es esperado ya que las simulaciones se corren bajo cargas de demanda crecientes hasta saturar la red.

Los resultados **son válidos** porque demuestran la **superioridad relativa** de k-SP-MW sobre SP-FF. Para observar valores de $P_b \approx 10^{-3}$, la red debería operarse en un régimen de carga mucho más bajo que los puntos de 150 o 200 mostrados en la simulación.

### Conclusión General
El algoritmo propuesto **k-SP-MW es superior** a la heurística *benchmark* SP-FF en ambas métricas clave:

1. **Eficiencia Espectral (Watermark):** Reducción de hasta **26.95%** (50 demandas) y **16.94%** (100 demandas)
2. **Confiabilidad (Bloqueo):** Reducción de hasta **39.21%** (150 demandas) y **30.84%** (200 demandas)

No solo cumple el objetivo principal de reducir el watermark en cargas bajas, sino que, como beneficio adicional, reduce significativamente la probabilidad de bloqueo en todos los escenarios de carga media-alta.

---

## 7. Implementación y Reproducibilidad

### 7.1 Arquitectura del Simulador

El simulador se implementó en **Python 3.8+** con arquitectura modular:

**Módulos Principales:**
- `data/`: Topología NSFNET, tabla de modulación, generador de demandas
- `src/core/`: Clase Network, algoritmos de routing (Yen), asignación de espectro (First-Fit)
- `src/algorithms/`: Implementación de SP-FF y k-SP-MW
- `src/simulator.py`: Motor de simulación estático
- `scripts/`: Scripts de experimentación y visualización

**Dependencias:**
- NetworkX (grafos y routing)
- NumPy (gestión de espectro)
- Matplotlib (visualización)
- Pandas (análisis de datos)

### 7.2 Instrucciones de Ejecución

```bash
# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar experimentos
python scripts/run_experiments.py

# 4. Generar gráficos
python scripts/generate_plots.py
```

**Resultados generados:**
- `results/metrics.csv`: Métricas numéricas completas
- `results/watermark_comparison.png`: Gráfico de eficiencia espectral
- `results/blocking_probability.png`: Gráfico de confiabilidad

**Documentación completa:**
- `INFORME_TECNICO.md`: Informe académico detallado
- `docs/TOPOLOGIA.md`: Especificación de NSFNET
- `docs/IMPLEMENTACION.md`: Arquitectura del código
- `results/detailed_results.md`: Análisis estadístico profundo

---

## 8. Referencias Bibliográficas

[1] O. Gerstel, M. Jinno, A. Lord, and S. J. B. Yoo, "Elastic optical networking: A new dawn for the optical layer?" *IEEE Communications Magazine*, vol. 50, no. 2, pp. s12-s20, February 2012.

[2] M. Jinno et al., "Spectrum-efficient and scalable elastic optical path network: architecture, benefits, and enabling technologies," *IEEE Communications Magazine*, vol. 47, no. 11, pp. 66-73, November 2009.

[3] M. Klinkowski and K. Walkowiak, "Routing and Spectrum Assignment in Spectrum Sliced Elastic Optical Path Network," *IEEE Communications Letters*, vol. 15, no. 8, pp. 884-886, August 2011.

[4] Y. Wang, X. Cao, and Y. Pan, "A study of the routing and spectrum allocation in spectrum-sliced Elastic Optical Path networks," in *Proc. IEEE INFOCOM*, Shanghai, China, 2011, pp. 1503-1511.

[5] K. Christodoulopoulos, I. Tomkos, and E. Varvarigos, "Elastic Bandwidth Allocation in Flexible OFDM-Based Optical Networks," *Journal of Lightwave Technology*, vol. 29, no. 9, pp. 1354-1366, May 2011.

[6] X. Wan, N. Hua, and X. Zheng, "Dynamic routing and spectrum assignment in spectrum-flexible transparent optical networks," *IEEE/OSA Journal of Optical Communications and Networking*, vol. 4, no. 8, pp. 603-613, August 2012.

[7] Y. Yin, H. Zhang, M. Zhang, et al., "Spectral and spatial 2D fragmentation-aware routing and spectrum assignment algorithms in elastic optical networks," *IEEE/OSA Journal of Optical Communications and Networking*, vol. 5, no. 10, pp. A100-A106, October 2013.

[8] Cisco, "Cisco Annual Internet Report (2018–2023)," White Paper, March 2020.

---

**Código fuente y datos:** [GitHub Repository](https://github.com/franciscozunigap/RMLSA-STATIC)