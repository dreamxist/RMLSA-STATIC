# RMLSA-STATIC

Simulador de **Routing, Modulation Level Selection, and Spectrum Allocation (RMLSA)** para redes opticas elasticas. Compara dos algoritmos de asignacion de espectro sobre la topologia NSFNet.

## Descripcion

Este proyecto implementa y compara dos enfoques para resolver el problema RMLSA:

- **SP-FF (Shortest Path - First Fit)**: Algoritmo heuristico baseline que usa el camino mas corto y asigna el primer bloque de espectro disponible.
- **Algoritmo Genetico**: Metaheuristica que optimiza el orden de procesamiento de demandas para minimizar el uso del espectro.

### Topologia NSFNet

La simulacion utiliza la red NSFNet (National Science Foundation Network) con:

- 14 nodos
- 21 enlaces bidireccionales
- 320 slots de frecuencia por enlace

### Formatos de Modulacion

| Formato | Alcance Maximo | Bits/Simbolo | Slots por 100 Gbps |
| ------- | -------------- | ------------ | ------------------ |
| 16-QAM  | 500 km         | 4            | 2                  |
| 8-QAM   | 1000 km        | 3            | 3                  |
| QPSK    | 2000 km        | 2            | 4                  |
| BPSK    | 10000 km       | 1            | 8                  |

## Requisitos

- Python 3.10 o superior
- Sistema operativo: Windows, macOS o Linux

## Instalacion Rapida

### macOS / Linux

```bash
# Dar permisos de ejecucion (solo la primera vez)
chmod +x install_and_run.sh

# Ejecutar
./install_and_run.sh
```

### Windows

Doble clic en `install_and_run.bat` o ejecutar desde CMD:

```cmd
install_and_run.bat
```

## Instalacion Manual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar simulador
python simulator.py
```

## Uso

Al ejecutar el simulador, se realizan las siguientes acciones:

1. Se crea la topologia NSFNet
2. Se generan 182 demandas de trafico (full-mesh entre 14 nodos)
3. Se ejecuta el algoritmo SP-FF (baseline)
4. Se ejecuta el algoritmo genetico (optimizacion)
5. Se genera un grafico comparativo
6. Se guarda un reporte detallado

## Arquitectura del Proyecto

```
RMLSA-STATIC/
├── simulator.py          # Punto de entrada principal
├── algorithms.py         # Implementacion SP-FF y Algoritmo Genetico
├── core.py               # Formatos de modulacion y gestion de red
├── topology.py           # Creacion de topologia NSFNet y rutas
├── traffic.py            # Generacion de demandas de trafico
├── requirements.txt      # Dependencias Python
├── install_and_run.sh    # Script de instalacion (Mac/Linux)
├── install_and_run.bat   # Script de instalacion (Windows)
└── README.md             # Este archivo
```

### Descripcion de Modulos

| Modulo          | Descripcion                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| `simulator.py`  | Orquesta la simulacion, mide tiempos y genera visualizaciones               |
| `algorithms.py` | Contiene `run_sp_ff()` y la clase `GeneticOptimizer`                        |
| `core.py`       | Define formatos de modulacion y la clase `Network` para gestion de espectro |
| `topology.py`   | Crea la topologia NSFNet e implementa K-shortest paths                      |
| `traffic.py`    | Clase `DemandGenerator` para crear demandas sinteticas                      |

## Parametros Configurables

Los siguientes parametros pueden modificarse en `simulator.py`:

| Parametro     | Valor por Defecto | Descripcion                                   |
| ------------- | ----------------- | --------------------------------------------- |
| `NUM_SLOTS`   | 320               | Numero de slots de frecuencia por enlace      |
| `AVG_BW`      | 100.0             | Ancho de banda promedio por demanda (Gbps)    |
| `seed`        | 42                | Semilla para reproducibilidad                 |
| `pop_size`    | 50                | Tamano de poblacion del algoritmo genetico    |
| `generations` | 100               | Numero de generaciones del algoritmo genetico |

## Salidas del Simulador

### Consola

Muestra un resumen comparativo de ambos algoritmos:

- Tiempo de ejecucion
- Demandas asignadas
- Indice maximo de slot utilizado
- Porcentaje de uso del espectro

### Archivos Generados

| Archivo                     | Descripcion                                     |
| --------------------------- | ----------------------------------------------- |
| `resultado_comparativa.png` | Grafico de barras comparando ambos algoritmos   |
| `assignments_details.txt`   | Reporte detallado de cada asignacion de demanda |

## Dependencias

```
networkx>=3.0      # Estructuras de grafos y algoritmos de rutas
numpy>=1.20        # Operaciones numericas y gestion de espectro
matplotlib>=3.5.0  # Visualizacion de resultados
```

## Licencia

Este proyecto es de uso academico y educativo.
