# RMLSA Static Simulator

Simulador de optimización de recursos en Redes Ópticas Elásticas (EONs) para el problema RMLSA (Routing, Modulation, and Spectrum Assignment) en escenario estático.

**Autores:** Francisco Castillo, Agustín López, Francisco Zúñiga

## Descripción del Proyecto

Este proyecto implementa y compara dos algoritmos heurísticos para resolver el problema RMLSA en redes ópticas elásticas:

1. **SP-FF (Shortest Path - First Fit)**: Algoritmo benchmark que selecciona la ruta más corta y asigna el primer bloque de espectro disponible.

2. **k-SP-MW (k-Shortest Paths - Minimum Watermark)**: Algoritmo propuesto que evalúa k=3 rutas candidatas y selecciona la que minimiza el crecimiento del watermark (uso de espectro).

### Métricas Evaluadas

- **Watermark Máximo**: Slot de frecuencia más alto utilizado en toda la red (métrica principal de eficiencia espectral)
- **Probabilidad de Bloqueo**: Porcentaje de demandas que no pudieron ser asignadas por falta de recursos

### Topología y Configuración

- **Red**: NSFNET (14 nodos, 21 enlaces bidireccionales)
- **Espectro**: 320 slots por enlace
- **Formatos de Modulación**: BPSK, QPSK, 8-QAM, 16-QAM (selección automática según distancia)
- **Cargas de Tráfico**: 50, 100, 150, 200 demandas

## Estructura del Proyecto

```
RMLSA-STATIC/
├── data/
│   ├── nsfnet.py              # Topología NSFNET
│   ├── modulation.py          # Tabla de formatos de modulación
│   └── demand_generator.py    # Generador de demandas
├── src/
│   ├── core/
│   │   ├── network.py         # Clase Network (gestión de espectro)
│   │   ├── routing.py         # Algoritmo de Yen (k-shortest paths)
│   │   └── spectrum.py        # Asignación de espectro First-Fit
│   ├── algorithms/
│   │   ├── sp_ff.py          # Algoritmo SP-FF
│   │   └── ksp_mw.py         # Algoritmo k-SP-MW
│   └── simulator.py           # Motor de simulación
├── scripts/
│   ├── run_experiments.py     # Ejecutar experimentos
│   └── generate_plots.py      # Generar gráficos
├── results/                   # Resultados y gráficos (generados)
├── requirements.txt           # Dependencias Python
├── Proyect.md                # Documentación detallada del proyecto
└── README.md                 # Este archivo
```

## Instalación

### Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio** (o descargar los archivos)

```bash
cd RMLSA-STATIC
```

2. **Crear entorno virtual** (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

## Uso

### 1. Ejecutar Experimentos

El script principal ejecuta simulaciones con diferentes cargas de tráfico y compara ambos algoritmos:

```bash
python scripts/run_experiments.py
```

Este script:
- Genera conjuntos de demandas con diferentes tamaños (50, 100, 150, 200)
- Ejecuta 5 trials por cada carga (para promediar resultados)
- Compara SP-FF vs k-SP-MW
- Guarda resultados en `results/metrics.csv`

**Salida esperada:**
```
================================================================================
RMLSA STATIC SIMULATION EXPERIMENTS
================================================================================
Configuration:
  Demand loads: [50, 100, 150, 200]
  Trials per load: 5
  Spectrum slots: 320
  k-paths: 3
================================================================================

Testing with 50 demands...
  Trial 1/5...
    SP-FF:   Watermark=45, Pb=0.0200
    k-SP-MW: Watermark=38, Pb=0.0000
  ...
```

### 2. Generar Gráficos

Una vez ejecutados los experimentos, generar visualizaciones:

```bash
python scripts/generate_plots.py
```

Genera tres gráficos en `results/`:
- `watermark_comparison.png`: Comparación de watermark
- `blocking_probability.png`: Comparación de probabilidad de bloqueo
- `combined_comparison.png`: Ambas métricas lado a lado

### 3. Pruebas Individuales de Módulos

Cada módulo puede ejecutarse de forma independiente para pruebas:

```bash
# Probar topología NSFNET
python data/nsfnet.py

# Probar tabla de modulación
python data/modulation.py

# Probar generador de demandas
python data/demand_generator.py

# Probar clase Network
python src/core/network.py

# Probar algoritmo de routing
python src/core/routing.py

# Probar asignación de espectro
python src/core/spectrum.py

# Probar algoritmo SP-FF
python src/algorithms/sp_ff.py

# Probar algoritmo k-SP-MW
python src/algorithms/ksp_mw.py

# Probar simulador
python src/simulator.py
```

## Metodología

### Escenario Estático

El simulador implementa el escenario **estático (offline)** del problema RMLSA:
- Todas las demandas son conocidas de antemano
- Las demandas se ordenan por ancho de banda (descendente) antes de procesarse
- Cada demanda se asigna permanentemente (no hay liberación de recursos)
- Se mide el estado final de la red tras procesar todas las demandas

### Proceso de Simulación

1. **Generación de Demandas**: Se generan N demandas con:
   - Pares origen-destino aleatorios (distribución uniforme)
   - Ancho de banda entre 25-100 Gbps (distribución uniforme)

2. **Ordenamiento**: Las demandas se ordenan de mayor a menor ancho de banda (heurística: procesar las más difíciles primero)

3. **Asignación Secuencial**: Para cada demanda:
   - **SP-FF**: Calcula 1 ruta (shortest path) → First-Fit
   - **k-SP-MW**: Calcula k=3 rutas → Elige la de menor watermark → First-Fit

4. **Cálculo de Métricas**:
   - Watermark Máximo = slot más alto usado en cualquier enlace
   - Probabilidad de Bloqueo = (demandas bloqueadas) / (demandas totales)

### Algoritmos Implementados

#### SP-FF (Benchmark)
```
Para cada demanda:
  1. Encontrar shortest path (Dijkstra)
  2. Calcular slots necesarios (según distancia y bandwidth)
  3. Asignar con First-Fit en esa ruta
  4. Si falla → bloquear demanda
```

#### k-SP-MW (Propuesto)
```
Para cada demanda:
  1. Encontrar k=3 shortest paths (Algoritmo de Yen)
  2. Para cada ruta:
       Calcular watermark resultante si se asigna
  3. Elegir ruta con mínimo watermark
  4. Asignar con First-Fit en ruta elegida
  5. Si todas fallan → bloquear demanda
```

## Resultados Esperados

Según el documento del proyecto (Proyect.md), se espera que:

1. **Watermark**: k-SP-MW logra watermark significativamente más bajo que SP-FF en cargas bajas-medias
2. **Probabilidad de Bloqueo**: k-SP-MW tiene menor bloqueo en todos los escenarios (beneficio de tener k=3 rutas alternativas)

### Interpretación

- **Watermark bajo** → Mayor eficiencia espectral, más capacidad libre para futuras demandas
- **Bloqueo bajo** → Mayor confiabilidad, más demandas atendidas con los mismos recursos

## Personalización

### Modificar Parámetros de Experimentación

Editar `scripts/run_experiments.py`:

```python
DEMAND_LOADS = [50, 100, 150, 200]  # Cargas a probar
NUM_TRIALS = 5                       # Repeticiones por carga
NUM_SLOTS = 320                      # Slots de espectro
K_PATHS = 3                          # Rutas candidatas
```

### Cambiar Distribución de Bandwidth

Editar `data/demand_generator.py` para usar distribución exponencial:

```python
demands = generator.generate_exponential_bandwidth(
    num_demands=100,
    mean_bandwidth=50
)
```

### Ajustar Formatos de Modulación

Editar `data/modulation.py` para cambiar alcances o eficiencias:

```python
MODULATION_FORMATS = [
    ("16-QAM", 500, 4, 2),
    ("8-QAM", 1000, 3, 3),
    ("QPSK", 2000, 2, 4),
    ("BPSK", 4000, 1, 8),
]
```

## Contribución y Desarrollo

### Agregar Nuevos Algoritmos

1. Crear archivo en `src/algorithms/nuevo_algoritmo.py`
2. Implementar función `nuevo_algoritmo_assign(network, demand)` que retorne assignment dict o None
3. Agregar opción en `src/simulator.py` método `run_simulation()`

### Ejecutar Tests Unitarios

Cada módulo incluye una sección `if __name__ == "__main__"` con tests básicos.

## Referencias

- **Problema RMLSA**: Routing, Modulation, and Spectrum Assignment en EONs
- **Topología**: NSFNET (National Science Foundation Network)
- **Algoritmo de Yen**: k-shortest paths
- **Grilla Flexible**: Flex-Grid para redes ópticas elásticas

## Licencia

Proyecto académico para optimización de redes ópticas.

---

## Documentación Adicional

### 📚 Reportes y Análisis

- **[INFORME_TECNICO.md](INFORME_TECNICO.md)** - Informe técnico completo con:
  - Marco teórico sobre EONs y RMLSA
  - Metodología detallada
  - Resultados experimentales con gráficos
  - Análisis estadístico
  - Referencias bibliográficas académicas

- **[results/detailed_results.md](results/detailed_results.md)** - Análisis profundo de resultados:
  - Tablas comparativas completas
  - Análisis de ordenamiento de demandas
  - Distribución de bloqueos
  - Sensibilidad de parámetros
  - Casos de uso representativos

### 🔧 Documentación Técnica

- **[docs/TOPOLOGIA.md](docs/TOPOLOGIA.md)** - Especificación completa de NSFNET:
  - Características de la red
  - Mapa de nodos y ciudades
  - Tabla de enlaces y distancias
  - Estadísticas de conectividad
  - Ejemplos de rutas

- **[docs/IMPLEMENTACION.md](docs/IMPLEMENTACION.md)** - Arquitectura del simulador:
  - Diagrama de módulos
  - Documentación de funciones
  - Flujo de datos
  - Estructuras de datos
  - Guía de extensibilidad
  - Casos de prueba

### 📊 Herramientas

- **[scripts/generate_report.py](scripts/generate_report.py)** - Generador automático de reportes:
  - Lee `results/metrics.csv`
  - Genera tablas en Markdown
  - Calcula estadísticas comparativas
  - Crea resumen ejecutivo

### 🎨 Resultados Visuales

Todos los gráficos se encuentran en `results/`:
- `watermark_comparison.png` - Eficiencia espectral
- `blocking_probability.png` - Confiabilidad de red
- `combined_comparison.png` - Comparación combinada

---

## Resultados Destacados

### 🏆 Logros Principales

| Métrica | Carga | SP-FF | k-SP-MW | Mejora |
|---------|-------|-------|---------|--------|
| **Watermark** | 50 demandas | 167.0 slots | **122.0 slots** | **-26.95%** ✓ |
| **Watermark** | 100 demandas | 297.6 slots | **247.2 slots** | **-16.94%** ✓ |
| **Bloqueo** | 150 demandas | 30.27% | **18.40%** | **-39.21%** ✓ |
| **Bloqueo** | 200 demandas | 34.70% | **24.00%** | **-30.84%** ✓ |
| **Utilización** | 200 demandas | 34.11% | **45.60%** | **+33.68%** ✓ |

### 📈 Conclusión

El algoritmo propuesto **k-SP-MW demuestra superioridad** sobre el benchmark SP-FF en:
- ✅ Eficiencia espectral (menor watermark en cargas bajas-medias)
- ✅ Confiabilidad (menor probabilidad de bloqueo en cargas medias-altas)
- ✅ Utilización de recursos (mejor aprovechamiento del espectro disponible)

---

**Contacto**: Francisco Castillo, Agustín López, Francisco Zúñiga
# RMLSA-STATIC
