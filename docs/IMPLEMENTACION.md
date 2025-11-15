# Documentación de Implementación - Simulador RMLSA

## 1. Arquitectura del Sistema

### 1.1 Visión General

El simulador RMLSA está implementado en Python 3.8+ con una arquitectura modular que separa:
- **Datos**: Topología y configuración de red
- **Core**: Lógica fundamental (routing, spectrum, network state)
- **Algoritmos**: Implementaciones de SP-FF y k-SP-MW
- **Simulación**: Motor de ejecución y experimentación
- **Visualización**: Generación de gráficos y reportes

### 1.2 Diagrama de Módulos

```
RMLSA-STATIC/
│
├── data/                           # Módulo de Datos
│   ├── nsfnet.py                  # Topología NSFNET
│   ├── modulation.py              # Tabla de formatos de modulación
│   └── demand_generator.py        # Generador de demandas
│
├── src/
│   ├── core/                      # Módulo Core
│   │   ├── network.py            # Clase Network (gestión de espectro)
│   │   ├── routing.py            # Algoritmos de routing (Dijkstra, Yen)
│   │   └── spectrum.py           # Asignación de espectro (First-Fit)
│   │
│   ├── algorithms/                # Módulo de Algoritmos
│   │   ├── sp_ff.py              # Algoritmo SP-FF
│   │   └── ksp_mw.py             # Algoritmo k-SP-MW
│   │
│   └── simulator.py               # Motor de Simulación
│
├── scripts/                        # Scripts de Ejecución
│   ├── run_experiments.py         # Ejecutar experimentos
│   └── generate_plots.py          # Generar visualizaciones
│
└── results/                        # Resultados (generados)
    ├── metrics.csv
    └── *.png
```

---

## 2. Módulos Principales

### 2.1 Módulo de Datos (`data/`)

#### `nsfnet.py` - Topología NSFNET
**Responsabilidad:** Definir la topología de la red

**Funciones principales:**
```python
create_nsfnet_topology() -> nx.Graph
    # Crea grafo NetworkX con 14 nodos y 21 enlaces
    # Cada enlace tiene atributo 'distance' (km)

get_node_names() -> dict
    # Retorna mapeo {node_id: city_name}

get_path_distance(G, path) -> float
    # Calcula distancia total de una ruta
```

**Uso:**
```python
from data.nsfnet import create_nsfnet_topology

G = create_nsfnet_topology()
print(G.number_of_nodes())  # 14
print(G[0][1]['distance'])  # 1500 (Seattle-San Francisco)
```

#### `modulation.py` - Tabla de Modulación
**Responsabilidad:** Selección de formato de modulación

**Funciones principales:**
```python
get_modulation_format(distance_km) -> dict
    # Selecciona formato según distancia
    # Retorna: {name, max_reach, bits_per_symbol, slots_per_100gbps}

calculate_required_slots(bandwidth_gbps, distance_km) -> (int, str)
    # Calcula slots necesarios + nombre de formato
    # Incluye guard bands (2 slots)
```

**Tabla implementada:**
| Formato | Alcance | Slots/100Gbps |
|---------|---------|---------------|
| 16-QAM  | 500 km  | 2             |
| 8-QAM   | 1000 km | 3             |
| QPSK    | 2000 km | 4             |
| BPSK    | 4000 km | 8             |

#### `demand_generator.py` - Generador de Demandas
**Responsabilidad:** Crear conjuntos de demandas para simulación

**Clase principal:**
```python
class DemandGenerator:
    def __init__(self, num_nodes, seed=None)

    def generate_uniform_demands(num_demands, bandwidth_range=(25,100))
        # Retorna lista de diccionarios:
        # {id, source, destination, bandwidth}
```

---

### 2.2 Módulo Core (`src/core/`)

#### `network.py` - Gestión de Estado de Red
**Responsabilidad:** Representar red y estado de espectro

**Clase principal:**
```python
class Network:
    def __init__(self, topology, num_slots=320)
        # Inicializa red con espectro vacío
        # self.spectrum[link] = np.array(num_slots, dtype=bool)

    def is_spectrum_available(path, start_slot, num_slots) -> bool
        # Verifica disponibilidad en TODOS los enlaces de la ruta

    def allocate_spectrum(path, start_slot, num_slots) -> bool
        # Asigna espectro en todos los enlaces

    def get_max_watermark() -> int
        # Retorna slot más alto usado en toda la red

    def get_spectrum_utilization() -> float
        # Retorna % de slots ocupados
```

**Restricciones implementadas:**
1. **Continuidad espectral**: Mismos slots en todos los enlaces
2. **Contigüidad**: Slots contiguos en frecuencia
3. **No-overlapping**: Sin conflictos en mismo enlace

#### `routing.py` - Algoritmos de Routing
**Responsabilidad:** Cálculo de rutas

**Funciones principales:**
```python
get_shortest_path(graph, source, target, weight='distance') -> list
    # Dijkstra: 1 ruta más corta
    # Complejidad: O(V²)

get_k_shortest_paths(graph, source, target, k=3, weight='distance') -> list
    # Algoritmo de Yen: k rutas más cortas
    # Complejidad: O(k × V³)

get_path_info(graph, path) -> dict
    # Retorna: {distance, num_hops, nodes}
```

**Algoritmo de Yen:** Encuentra k rutas disjuntas más cortas sin ciclos.

#### `spectrum.py` - Asignación de Espectro
**Responsabilidad:** Políticas de asignación espectral

**Funciones principales:**
```python
first_fit(network, path, num_slots) -> int or None
    # Busca desde slot 0: primer bloque contiguo disponible
    # Retorna start_slot o None si no hay

calculate_watermark_increment(network, path, num_slots) -> int or None
    # Calcula watermark resultante si se asigna
    # Usado por k-SP-MW para selección de ruta
```

---

### 2.3 Módulo de Algoritmos (`src/algorithms/`)

#### `sp_ff.py` - Shortest Path First-Fit
**Responsabilidad:** Algoritmo benchmark

**Función principal:**
```python
def sp_ff_assign(network, demand) -> dict or None:
    # 1. path = get_shortest_path(source, dest)
    # 2. (slots, mod) = calculate_required_slots(bandwidth, distance)
    # 3. start = first_fit(network, path, slots)
    # 4. allocate_spectrum(path, start, slots)
    # Retorna: {path, start_slot, num_slots, modulation, distance}
```

**Complejidad:** O(V²) por demanda

#### `ksp_mw.py` - k-Shortest Paths Minimum Watermark
**Responsabilidad:** Algoritmo propuesto

**Función principal:**
```python
def ksp_mw_assign(network, demand, k=3) -> dict or None:
    # 1. paths = get_k_shortest_paths(source, dest, k=3)
    # 2. Para cada path:
    #      - Calcular watermark_incremental
    # 3. Elegir path con mínimo watermark
    # 4. Asignar con first_fit
    # Retorna: {path, start_slot, num_slots, modulation, watermark}
```

**Complejidad:** O(k × V³) por demanda

---

### 2.4 Motor de Simulación (`src/simulator.py`)

#### Clase `StaticSimulator`
**Responsabilidad:** Ejecutar simulación estática completa

**Método principal:**
```python
def run_simulation(demands, algorithm='sp_ff', k=3, verbose=False) -> dict:
    # 1. Ordenar demandas por bandwidth (descendente)
    # 2. Crear network fresh
    # 3. Para cada demanda:
    #      - Aplicar algoritmo (sp_ff o ksp_mw)
    #      - Registrar si assigned o blocked
    # 4. Calcular métricas finales
    # Retorna: {assigned, blocked, blocking_probability, max_watermark, ...}
```

**Flujo de ejecución:**
```
┌─────────────────────────┐
│ Cargar Topología        │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Generar Demandas        │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Ordenar por Bandwidth   │ ← Heurística clave
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Procesar Demandas       │ ← Loop principal
│   - Routing             │
│   - Modulación          │
│   - Spectrum Assignment │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Calcular Métricas       │
│   - Watermark           │
│   - Bloqueo             │
│   - Utilización         │
└─────────────────────────┘
```

---

## 3. Flujo de Datos

### 3.1 Procesamiento de una Demanda (SP-FF)

```
Demanda: {source: 0, destination: 13, bandwidth: 100}
    ↓
[routing.py] get_shortest_path(0, 13)
    → Ruta: [0, 2, 5, 6, 7, 12, 13]
    → Distancia: 6000 km
    ↓
[modulation.py] calculate_required_slots(100 Gbps, 6000 km)
    → Formato: BPSK (única opción para 6000 km)
    → Slots: 8 × 1 + 2 (guard) = 10 slots
    ↓
[spectrum.py] first_fit(network, path, 10)
    → Buscar primer bloque de 10 slots contiguos
    → Encontrado en start_slot = 45
    ↓
[network.py] allocate_spectrum(path, 45, 10)
    → Marcar slots 45-54 como ocupados en enlaces:
       (0,2), (2,5), (5,6), (6,7), (7,12), (12,13)
    ↓
Retorno: {path: [0,2,5,6,7,12,13], start_slot: 45, num_slots: 10,
          modulation: "BPSK", distance: 6000}
```

### 3.2 Procesamiento de una Demanda (k-SP-MW)

```
Demanda: {source: 0, destination: 13, bandwidth: 100}
    ↓
[routing.py] get_k_shortest_paths(0, 13, k=3)
    → Ruta 1: [0, 2, 5, 6, 7, 12, 13] (6000 km)
    → Ruta 2: [0, 2, 5, 9, 11, 13] (6700 km)
    → Ruta 3: [0, 1, 2, 5, 6, 7, 12, 13] (7500 km)
    ↓
[Para cada ruta] calculate_watermark_increment()
    → Ruta 1: watermark = 180 (congestionada)
    → Ruta 2: watermark = 165 (mejor opción)  ← Elegida
    → Ruta 3: watermark = 190 (peor opción)
    ↓
[spectrum.py] first_fit(network, ruta_2, 10)
    → start_slot = 155
    ↓
[network.py] allocate_spectrum(ruta_2, 155, 10)
    → Slots 155-164 ocupados en enlaces de ruta 2
    ↓
Retorno: {path: [0,2,5,9,11,13], start_slot: 155, num_slots: 10,
          modulation: "BPSK", watermark: 165}
```

---

## 4. Estructuras de Datos

### 4.1 Representación de Demanda

```python
demand = {
    'id': int,              # Identificador único
    'source': int,          # Nodo origen (0-13)
    'destination': int,     # Nodo destino (0-13)
    'bandwidth': int        # Ancho de banda en Gbps (25-100)
}
```

### 4.2 Representación de Espectro

```python
# Por enlace: Array booleano NumPy
self.spectrum[(u, v)] = np.array([False, False, ..., False])
                        # Índices: 0 a num_slots-1
                        # True = ocupado, False = libre

# Ejemplo con 20 slots:
# [F, F, T, T, T, F, F, T, T, F, F, F, F, T, T, T, T, F, F, F]
#  ↑  ↑  ↑--------↑  ↑  ↑-----↑  ↑        ↑-----------↑
#  0  1  2  3  4  5  6  7  8  9  10       13 14 15 16 17
#     ↑  └─ocupado─┘     └─ocupado─┘      └───ocupado───┘
#   libre                libre                    libre
```

### 4.3 Resultado de Simulación

```python
result = {
    'assigned': int,                # Demandas asignadas
    'blocked': int,                 # Demandas bloqueadas
    'total': int,                   # Total demandas
    'blocking_probability': float,  # Pb = blocked / total
    'max_watermark': int,           # Watermark máximo
    'utilization': float,           # % espectro usado
    'assignments': [                # Detalle de cada demanda
        {
            'demand_id': int,
            'assigned': bool,
            'path': list,           # Si assigned=True
            'start_slot': int,
            'num_slots': int,
            'modulation': str
        },
        ...
    ],
    'execution_time': float,        # Segundos
    'algorithm': str                # 'sp_ff' o 'ksp_mw'
}
```

---

## 5. Dependencias

### 5.1 Librerías Externas

```python
networkx>=3.0      # Grafos y algoritmos de routing
numpy>=1.24.0      # Arrays numéricos para espectro
matplotlib>=3.7.0  # Visualización de resultados
pandas>=2.0.0      # Manejo de datos y CSV
scipy>=1.10.0      # Funciones estadísticas
```

### 5.2 Módulos Estándar

```python
import time        # Medición de tiempo de ejecución
import math        # Operaciones matemáticas (ceil)
import sys, os     # Gestión de paths
```

---

## 6. Casos de Prueba

### 6.1 Test Unitario - Network

```python
# Crear red de prueba
topology = create_nsfnet_topology()
network = Network(topology, num_slots=100)

# Test 1: Asignación exitosa
path = [0, 2, 5]
assert network.is_spectrum_available(path, 10, 5) == True
assert network.allocate_spectrum(path, 10, 5) == True
assert network.get_max_watermark() == 15

# Test 2: Conflicto (overlapping)
assert network.is_spectrum_available(path, 12, 5) == False

# Test 3: Asignación no-overlapping
assert network.allocate_spectrum(path, 20, 3) == True
assert network.get_max_watermark() == 23
```

### 6.2 Test Unitario - Routing

```python
topology = create_nsfnet_topology()

# Test: k-shortest paths
paths = get_k_shortest_paths(topology, source=0, target=13, k=3)
assert len(paths) == 3
assert len(paths[0]) <= len(paths[1]) <= len(paths[2])

# Test: distancias crecientes
d1 = get_path_distance(topology, paths[0])
d2 = get_path_distance(topology, paths[1])
d3 = get_path_distance(topology, paths[2])
assert d1 <= d2 <= d3
```

---

## 7. Extensibilidad

### 7.1 Agregar Nuevo Algoritmo

**Paso 1:** Crear archivo `src/algorithms/nuevo_algoritmo.py`

```python
def nuevo_algoritmo_assign(network, demand):
    # Tu lógica aquí
    return assignment or None
```

**Paso 2:** Modificar `src/simulator.py`

```python
def run_simulation(self, demands, algorithm='sp_ff', ...):
    if algorithm == 'sp_ff':
        result = sp_ff_assign(network, demand)
    elif algorithm == 'ksp_mw':
        result = ksp_mw_assign(network, demand)
    elif algorithm == 'nuevo_algoritmo':  # ← Agregar
        result = nuevo_algoritmo_assign(network, demand)
```

### 7.2 Agregar Nueva Topología

**Paso 1:** Crear archivo `data/mi_topologia.py`

```python
def create_mi_topologia():
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, ...])
    G.add_edge(0, 1, distance=500)
    # ...
    return G
```

**Paso 2:** Usar en experimentos

```python
from data.mi_topologia import create_mi_topologia

topology = create_mi_topologia()
simulator = StaticSimulator(topology)
```

---

## 8. Debugging y Logging

### 8.1 Modo Verbose

```python
# Habilitar logs detallados
results = simulator.run_simulation(demands, algorithm='ksp_mw', verbose=True)

# Salida:
# Processing demand 1/50: 3 -> 10, 99 Gbps
#   ✓ Assigned (watermark: 122)
# Processing demand 2/50: 13 -> 7, 98 Gbps
#   ✗ Blocked
# ...
```

### 8.2 Tests Individuales de Módulos

```bash
# Test topología
python data/nsfnet.py

# Test modulación
python data/modulation.py

# Test generador de demandas
python data/demand_generator.py

# Test network
python src/core/network.py

# Test routing
python src/core/routing.py

# Test spectrum
python src/core/spectrum.py

# Test SP-FF
python src/algorithms/sp_ff.py

# Test k-SP-MW
python src/algorithms/ksp_mw.py

# Test simulador
python src/simulator.py
```

---

## 9. Optimizaciones Implementadas

### 9.1 Eficiencia de Espectro

1. **Arrays NumPy**: Operaciones vectorizadas para verificación de disponibilidad
2. **Caching de grafos**: NetworkX cachea shortest paths
3. **Early termination**: First-Fit detiene búsqueda en primera coincidencia

### 9.2 Eficiencia de Memoria

1. **Representación booleana**: 1 byte por slot en lugar de integer
2. **Sin copia de grafos**: Referencia compartida a topología
3. **Generación lazy de demandas**: Solo cuando se necesitan

---

## 10. Limitaciones Conocidas

1. **Sin regeneración**: Rutas > 4000 km se bloquean
2. **Sin desfragmentación**: Fragmentación puede degradar rendimiento
3. **Sin multipath**: Una demanda usa exactamente 1 ruta
4. **Sin grooming**: No se combinan demandas en mismo super-canal
5. **Estático puro**: No hay llegadas/salidas dinámicas

---

**Ver también:**
- [INFORME_TECNICO.md](../INFORME_TECNICO.md) - Resultados y análisis
- [TOPOLOGIA.md](TOPOLOGIA.md) - Detalles de NSFNET
- [README.md](../README.md) - Guía de uso
