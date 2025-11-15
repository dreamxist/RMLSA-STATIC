# Topología NSFNET - Especificación Detallada

## Descripción General

**NSFNET** (National Science Foundation Network) fue una red troncal de telecomunicaciones en Estados Unidos que operó desde 1985 hasta 1995. En investigación de redes ópticas, su topología se utiliza como **red de referencia estándar** debido a:

- Tamaño representativo (14 nodos)
- Distribución geográfica realista
- Conectividad balanceada
- Ampliamente usada en literatura académica

## Características de la Red

| Característica | Valor |
|----------------|-------|
| **Número de nodos** | 14 |
| **Número de enlaces** | 21 (bidireccionales) |
| **Grado promedio** | 3.0 |
| **Grado mínimo** | 2 |
| **Grado máximo** | 4 |
| **Diámetro** | 5 |
| **Densidad de enlaces** | 0.23 |

## Mapa de Nodos

```
Nodo ID  | Ciudad            | Abreviatura | Región
---------|-------------------|-------------|------------------
   0     | Seattle           | SEA         | Noroeste Pacífico
   1     | San Francisco     | SFO         | Costa Oeste
   2     | Salt Lake City    | SLC         | Montañas Rocosas
   3     | San Diego         | SDO         | Costa Oeste
   4     | Phoenix           | PHX         | Suroeste
   5     | Denver            | DEN         | Centro-Oeste
   6     | Kansas City       | KAN         | Centro
   7     | Champaign         | CHA         | Centro
   8     | Indianapolis      | IND         | Centro-Este
   9     | Houston           | HOU         | Sur
  10     | Oklahoma          | OKL         | Sur-Centro
  11     | Atlanta           | ATL         | Sureste
  12     | Pittsburgh        | PIT         | Noreste
  13     | Washington DC     | WDC         | Costa Este
```

## Tabla de Enlaces

| Enlace | Origen | Destino | Distancia (km) | Ciudades |
|--------|--------|---------|----------------|----------|
| 1      | 0      | 1       | 1500           | Seattle ↔ San Francisco |
| 2      | 0      | 2       | 2400           | Seattle ↔ Salt Lake City |
| 3      | 1      | 2       | 900            | San Francisco ↔ Salt Lake City |
| 4      | 1      | 3       | 600            | San Francisco ↔ San Diego |
| 5      | 2      | 5       | 1200           | Salt Lake City ↔ Denver |
| 6      | 3      | 4       | 800            | San Diego ↔ Phoenix |
| 7      | 4      | 5       | 900            | Phoenix ↔ Denver |
| 8      | 5      | 6       | 1000           | Denver ↔ Kansas City |
| 9      | 5      | 9       | 1500           | Denver ↔ Houston |
| 10     | 6      | 7       | 600            | Kansas City ↔ Champaign |
| 11     | 6      | 10      | 500            | Kansas City ↔ Oklahoma |
| 12     | 7      | 8       | 300            | Champaign ↔ Indianapolis |
| 13     | 7      | 11      | 800            | Champaign ↔ Atlanta |
| 14     | 8      | 12      | 400            | Indianapolis ↔ Pittsburgh |
| 15     | 9      | 10      | 700            | Houston ↔ Oklahoma |
| 16     | 9      | 11      | 1200           | Houston ↔ Atlanta |
| 17     | 10     | 11      | 1100           | Oklahoma ↔ Atlanta |
| 18     | 11     | 12      | 900            | Atlanta ↔ Pittsburgh |
| 19     | 11     | 13      | 600            | Atlanta ↔ Washington DC |
| 20     | 12     | 13      | 300            | Pittsburgh ↔ Washington DC |
| 21     | 12     | 7       | 500            | Pittsburgh ↔ Champaign |

### Estadísticas de Distancias

| Métrica | Valor (km) |
|---------|------------|
| **Distancia mínima** | 300 |
| **Distancia máxima** | 2400 |
| **Distancia promedio** | 868.6 |
| **Distancia mediana** | 800 |

## Distribución de Grados

El **grado** de un nodo es el número de enlaces directos que tiene.

```
Grado | Nodos                        | Cantidad
------|------------------------------|----------
  2   | 0, 1, 3, 4, 8, 9, 10, 13    |    8
  3   | 2, 6, 12                     |    3
  4   | 5, 7, 11                     |    3
```

**Nodos críticos (grado 4):**
- **Denver (5)**: Hub central que conecta Oeste con Centro
- **Champaign (7)**: Hub del centro que distribuye a Este
- **Atlanta (11)**: Hub del Sur que conecta con Este

## Representación Visual Simplificada

```
                          Seattle(0)
                          /        \
                     (1500)      (2400)
                        /            \
            San Francisco(1)    Salt Lake City(2)
                |     \              |
              (600)   (900)       (1200)
                |       \            |
          San Diego(3)  +--------Denver(5)--------+
                |                  /  \            \
              (800)            (1000) (1500)     (900)
                |               /       \           \
            Phoenix(4)   Kansas(6)    Houston(9)  Phoenix(4)
                            |  \         |  \
                          (600)(500)  (700)(1200)
                            |    \      |     \
                      Champaign(7) Oklahoma(10) Atlanta(11)
                         /  |  \           \      /  |  \
                     (300)(800)(500)     (1100) / (600)(900)
                       /    |     \           | /    |
              Indianapolis(8) Atlanta(11)  Atlanta  |
                       |          |               Washington(13)
                     (400)      (900)               /
                       |          |             (300)
                  Pittsburgh(12)--+               /
                                  \--------------+
```

## Rutas de Ejemplo

### Ejemplos de Rutas Más Cortas

1. **Seattle → Washington DC**
   - Ruta: 0 → 2 → 5 → 6 → 7 → 12 → 13
   - Distancia: 2400 + 1200 + 1000 + 600 + 500 + 300 = **6000 km**
   - Saltos: 6

2. **San Francisco → Atlanta**
   - Ruta: 1 → 2 → 5 → 6 → 7 → 11
   - Distancia: 900 + 1200 + 1000 + 600 + 800 = **4500 km**
   - Saltos: 5

3. **San Diego → Indianapolis**
   - Ruta: 3 → 4 → 5 → 6 → 7 → 8
   - Distancia: 800 + 900 + 1000 + 600 + 300 = **3600 km**
   - Saltos: 5

### Implicaciones para Modulación

Según la tabla de modulación implementada:

| Distancia Total | Formato Seleccionado | Eficiencia |
|-----------------|----------------------|------------|
| < 500 km        | 16-QAM               | Máxima (2 slots/100Gbps) |
| 500-1000 km     | 8-QAM                | Alta (3 slots/100Gbps) |
| 1000-2000 km    | QPSK                 | Media (4 slots/100Gbps) |
| 2000-4000 km    | BPSK                 | Baja (8 slots/100Gbps) |
| > 4000 km       | ❌ Inalcanzable      | N/A |

**Ejemplo:** La ruta Seattle → Washington DC (6000 km) requeriría regeneración de señal, ya que excede el alcance de BPSK (4000 km). En la simulación, esto resultaría en bloqueo de la demanda.

## Propiedades de Conectividad

### Conectividad de Nodos
- **Conectividad de nodos**: 2 (mínimo número de nodos que deben fallar para desconectar la red)
- **Conectividad de enlaces**: 2 (mínimo número de enlaces que deben fallar)

### Redundancia
Todos los pares de nodos tienen **al menos 2 rutas disjuntas**, lo que proporciona:
- Tolerancia a fallos
- Balanceo de carga
- Flexibilidad para el algoritmo k-SP-MW (k≥2)

## Uso en el Simulador

La topología se carga desde `data/nsfnet.py`:

```python
from data.nsfnet import create_nsfnet_topology, get_node_names

# Crear grafo
G = create_nsfnet_topology()

# Obtener nombres de nodos
names = get_node_names()
print(names[0])  # "Seattle"
```

El simulador utiliza esta topología para:
1. **Cálculo de rutas**: Algoritmos de Dijkstra y Yen
2. **Cálculo de distancias**: Suma de atributos `distance` en enlaces
3. **Selección de modulación**: Basada en distancia total de ruta
4. **Gestión de espectro**: 320 slots por cada uno de los 21 enlaces

---

**Referencias:**
- NSFNET Historical Archive: https://www.nsf.gov/about/history/nsfnet.jsp
- Topology Zoo: http://www.topology-zoo.org/
- Uso académico: Ampliamente citado en literatura de EONs y RSA
