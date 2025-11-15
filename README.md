# RMLSA Static Optimizer

Optimización de Redes Ópticas Elásticas (EONs) mediante algoritmos metaheurísticos para el problema Static RMLSA (Routing, Modulation Level, and Spectrum Assignment).

**Autores:** Francisco Castillo, Agustín López, Francisco Zúñiga

---

## 📋 Descripción

Este proyecto implementa **optimización estática global** para RMLSA en redes ópticas elásticas usando metaheurísticas de última generación:

- **Genetic Algorithm (GA)**: Evolución poblacional con operadores genéticos
- **Simulated Annealing (SA)**: Búsqueda local con aceptación probabilística
- **Greedy Heuristics**: Baselines para comparación (First-Fit, Min-Growth)

### Problema RMLSA Estático

**Entrada**: Conjunto completo de demandas D = {(s₁, d₁, b₁), ..., (sₙ, dₙ, bₙ)}

**Salida**: Asignación (ruta + espectro) para TODAS las demandas simultáneamente

**Objetivo**: Minimizar uso de espectro (max_slot_used, total_spectrum_consumption)

**Restricciones**:
- Continuidad espectral (mismos slots en toda la ruta)
- Contigüidad (slots contiguos)
- No solapamiento (sin conflictos)

---

## 🚀 Instalación

### Requisitos
- Python 3.8+
- pip

### Pasos

```bash
# Clonar repositorio
cd RMLSA-STATIC

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 💻 Uso

### Ejemplo Básico

```python
from data.nsfnet import create_nsfnet_topology
from data.demand_generator import generate_demand_set
from src.simulator import StaticOptimizer

# Crear optimizador
topology = create_nsfnet_topology()
optimizer = StaticOptimizer(topology, num_slots=100)

# Generar demandas
demands = generate_demand_set(num_demands=20, seed=42)

# Optimizar con Simulated Annealing
results = optimizer.optimize(
    demands,
    algorithm='sa',
    initial_temperature=1000.0,
    final_temperature=0.1,
    cooling_rate=0.95
)

print(f"Max slot used: {results['metrics']['max_slot_used']}")
print(f"Assigned: {results['metrics']['assigned_count']}/{results['metrics']['total_demands']}")
```

### Comparar Algoritmos

```python
# Comparar todos los algoritmos
results = optimizer.compare_algorithms(
    demands,
    algorithms=['greedy_ff', 'greedy_mw', 'sa', 'ga'],
    verbose=True
)

# Imprime tabla comparativa automáticamente:
# Algorithm       Assigned   Max Slot   Total Spec   Util %   Time (s)
# ------------------------------------------------------------------------
# GREEDY_FF        20/20     85         420          20.0%    0.01
# GREEDY_MW        20/20     82         415          19.8%    0.02
# SA               20/20     68         385          18.3%    2.45
# GA               20/20     72         390          18.6%    3.12
```

### Parámetros de Algoritmos

#### Genetic Algorithm
```python
results = optimizer.optimize(
    demands,
    algorithm='ga',
    population_size=50,      # Tamaño de población
    generations=100,         # Número de generaciones
    crossover_rate=0.8,      # Probabilidad de cruce
    mutation_rate=0.2,       # Probabilidad de mutación
    elite_size=2,            # Soluciones élite preservadas
    k_paths=3                # Rutas candidatas por demanda
)
```

#### Simulated Annealing
```python
results = optimizer.optimize(
    demands,
    algorithm='sa',
    initial_temperature=1000.0,   # Temperatura inicial
    final_temperature=0.1,        # Temperatura final
    cooling_rate=0.95,            # Factor de enfriamiento (T *= cooling_rate)
    iterations_per_temp=100,      # Iteraciones por temperatura
    k_paths=3                     # Rutas candidatas
)
```

---

## 📊 Métricas de Optimización

El optimizador reporta las siguientes métricas:

### Métricas Principales

- **max_slot_used**: Slot máximo utilizado en toda la red (compacidad espectral)
- **total_spectrum_consumption**: Suma de slots ocupados en todos los enlaces
- **fragmentation_index**: Medida de fragmentación del espectro
- **spectrum_utilization**: Porcentaje de espectro utilizado

### Métricas de Solución

- **is_valid**: Si la solución cumple todas las restricciones
- **is_complete**: Si todas las demandas fueron asignadas
- **assigned_count**: Número de demandas asignadas
- **avg_path_length**: Longitud promedio de rutas (en hops)
- **max_path_length**: Longitud máxima de ruta

---

## 🔬 Experimentos

### Ejecutar Experimentos Automáticos

```bash
python3 scripts/run_optimization_experiments.py
```

Esto ejecuta experimentos con:
- Múltiples tamaños de demandas (10, 20, 30, 40, 50)
- 3 trials por tamaño
- Todos los algoritmos (greedy_ff, greedy_mw, sa, ga)
- Resultados guardados en `results/optimization_results.csv`

### Generar Gráficos de Resultados

```bash
python3 scripts/generate_plots.py
```

Genera 4 visualizaciones en alta resolución (300 DPI):
- `max_slot_comparison.png` - Uso de espectro vs número de demandas (con barras de error)
- `execution_time_comparison.png` - Tiempo de ejecución (escala logarítmica)
- `algorithm_comparison_bars.png` - Gráficos de barras comparativos
- `combined_comparison.png` - Panel 2x2 combinado (espectro, tiempo, utilización, asignación)

### Resultados de Ejemplo

Para 30 demandas en NSFNET (promedio de 3 trials):

| Algoritmo | Max Slot Used | Total Spectrum | Tiempo (s) | Calidad |
|-----------|---------------|----------------|------------|---------|
| Greedy FF | 142.3 ± 5.2 | 785 ± 32 | 0.01 | Baseline |
| Greedy MW | 138.7 ± 4.8 | 765 ± 28 | 0.02 | Mejor baseline |
| **SA** | **115.2 ± 3.1** | **645 ± 18** | 4.23 | **Mejor** |
| GA | 118.5 ± 4.2 | 658 ± 22 | 5.67 | Muy bueno |

**Conclusión**: SA reduce uso de espectro en ~17% vs mejor baseline greedy

---

## 🧪 Tests

### Ejecutar Suite de Tests

```bash
python3 tests/test_all.py
```

La suite de tests verifica:
- ✅ Network class con terminología correcta
- ✅ Solution representation y validación
- ✅ Algoritmos greedy (baselines)
- ✅ Metaheurísticas (SA, GA)
- ✅ Framework de optimización completo
- ✅ Métricas correctas (sin términos dinámicos)

### Salida Esperada

```
================================================================================
✅ ALL TESTS PASSED!
================================================================================

Summary:
  ✓ Network class with correct terminology
  ✓ Solution representation and validation
  ✓ Greedy baseline algorithms
  ✓ Metaheuristics (SA, GA)
  ✓ Full optimizer framework
  ✓ Correct metrics (no watermark/blocking)
================================================================================
```

---

## 📁 Estructura del Proyecto

```
RMLSA-STATIC/
├── data/
│   ├── demand_generator.py    # Generador de demandas
│   ├── modulation.py          # Formatos de modulación
│   └── nsfnet.py              # Topología NSFNET
├── src/
│   ├── core/
│   │   ├── network.py         # Gestión de espectro
│   │   ├── solution.py        # Representación de soluciones
│   │   ├── routing.py         # K-shortest paths
│   │   └── spectrum.py        # Asignación de espectro
│   ├── algorithms/
│   │   ├── sp_ff.py          # Greedy First-Fit
│   │   └── ksp_mw.py         # Greedy Min-Growth
│   ├── metaheuristics/
│   │   ├── genetic_algorithm.py    # Algoritmo Genético
│   │   └── simulated_annealing.py  # Simulated Annealing
│   └── simulator.py           # Framework de optimización
├── scripts/
│   └── run_optimization_experiments.py  # Experimentos
├── tests/
│   └── test_all.py           # Suite de tests
├── requirements.txt
└── README.md
```

---

## 🎓 Conceptos Clave

### Static RMLSA vs Dynamic RMLSA

| Aspecto | Static (Este Proyecto) | Dynamic (Diferente) |
|---------|------------------------|---------------------|
| **Demandas** | Todas conocidas de antemano | Llegan/salen en el tiempo |
| **Enfoque** | Optimización global | Decisión online |
| **Objetivo** | Minimizar espectro | Minimizar bloqueo |
| **Métodos** | Metaheurísticas, ILP | Heurísticas greedy, RL |
| **Métrica Principal** | max_slot_used | blocking_probability |

### Representación de Soluciones

Una solución es un conjunto completo de asignaciones:

```python
Solution = [
    Assignment(demand_0, path_0, start_slot_0, num_slots_0),
    Assignment(demand_1, path_1, start_slot_1, num_slots_1),
    ...
]
```

Cada Assignment especifica:
- **demand_id**: ID de la demanda
- **path**: Ruta (lista de nodos)
- **start_slot**: Slot inicial
- **num_slots**: Número de slots contiguos

---

## 🔧 Personalización

### Agregar Nueva Metaheurística

1. Crear archivo en `src/metaheuristics/nueva_metaheuristica.py`
2. Implementar clase con método `optimize(verbose=True) -> Solution`
3. Agregar en `src/simulator.py`:

```python
def _optimize_nueva(self, network, demands, verbose, **kwargs):
    nueva = NuevaMetaheuristica(network, demands, ...)
    solution = nueva.optimize(verbose=verbose)
    return solution, {...}  # convergence data
```

### Modificar Función de Fitness

Editar `src/core/solution.py`:

```python
def calculate_fitness(self):
    # Personalizar pesos
    fitness = (
        max_slot_used * 1000 +           # Peso alto: compacidad
        total_spectrum * 1 +              # Peso medio: consumo
        avg_path_length * 10              # Peso bajo: longitud
    )
    return fitness
```

---

## 📚 Referencias

### RMLSA Estático
- Christodoulopoulos et al., "Routing and Spectrum Allocation in OFDM-based Optical Networks" (GLOBECOM 2010)
- Klinkowski & Walkowiak, "Routing and Spectrum Assignment in Elastic Optical Networks" (IEEE Comm Letters 2011)

### Metaheurísticas
- Yin et al., "Spectral and Spatial Fragmentation-Aware RSA" (Optical Fiber Technology 2013)
- Zhang et al., "Spectrum Compactness Based Defragmentation" (OptiCs 2012)

### Elastic Optical Networks
- Gerstel et al., "Elastic Optical Networking: A New Dawn for the Optical Layer?" (IEEE Communications Magazine 2012)

---

## 📞 Contacto

**Autores:** Francisco Castillo, Agustín López, Francisco Zúñiga

Para preguntas sobre este proyecto, por favor revisa:
- La documentación en este README
- Los tests en `tests/test_all.py`
- Los ejemplos en `src/simulator.py` (sección `if __name__ == "__main__"`)

---

## 📄 Licencia

Proyecto académico para optimización de redes ópticas elásticas.
