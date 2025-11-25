import numpy as np
import math

# --- MODULATION CONFIGURATION ---
# Format: (name, max_reach_km, bits_per_symbol, slots_per_100gbps)
MODULATION_FORMATS = [
    ("16-QAM", 500, 4, 2),  # High efficiency
    ("8-QAM", 1000, 3, 3),  # Mid efficiency
    ("QPSK", 2000, 2, 4),  # Standard long haul
    ("BPSK", 10000, 1, 8),  # Ultra long haul
]


def get_modulation_params(distance_km):
    """Retorna los parámetros de modulación según la distancia."""
    for name, max_reach, bps, slots_100g in MODULATION_FORMATS:
        if distance_km <= max_reach:
            return {"name": name, "slots_per_100g": slots_100g}
    return None


def calculate_slots(bandwidth_gbps, distance_km):
    """Calcula slots necesarios. Retorna (num_slots, mod_name)."""
    mod = get_modulation_params(distance_km)
    if not mod:
        return None, None

    # Capacidad por slot = 100G / slots_necesarios_para_100G
    capacity_per_slot = 100.0 / mod["slots_per_100g"]
    slots_needed = math.ceil(bandwidth_gbps / capacity_per_slot)
    return int(slots_needed), mod["name"]


# --- NETWORK STATE ---
class Network:
    """
    Representa el estado de la red óptica (Espectro).
    Integra la lógica de asignación (First Fit) para mayor eficiencia.
    """

    def __init__(self, topology, num_slots=320):
        self.topology = topology
        self.num_slots = num_slots
        # spectrum[(u, v)] es un array booleano: False=Libre, True=Ocupado
        self.spectrum = {}
        for u, v in self.topology.edges():
            self.spectrum[(u, v)] = np.zeros(num_slots, dtype=bool)
            self.spectrum[(v, u)] = np.zeros(num_slots, dtype=bool)

    def is_path_free(self, path, start_slot, num_slots):
        """Verifica si un rango de slots está libre en todos los enlaces del camino."""
        if start_slot + num_slots > self.num_slots:
            return False

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            # Usamos slicing de numpy para verificar el bloque entero rápidamente
            # Si la suma es > 0, significa que hay al menos un 'True' (ocupado)
            if self.spectrum[(u, v)][start_slot : start_slot + num_slots].any():
                return False
        return True

    def find_first_fit(self, path, num_slots):
        """
        Encuentra el primer índice de slot válido para el camino.
        Optimización: Busca huecos continuos.
        """
        # Esta es una implementación básica. Para producción masiva se usan máscaras de bits.
        for i in range(self.num_slots - num_slots + 1):
            if self.is_path_free(path, i, num_slots):
                return i
        return None

    def allocate(self, path, start_slot, num_slots):
        """Marca los slots como ocupados."""
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            self.spectrum[(u, v)][start_slot : start_slot + num_slots] = True

    def get_utilization(self):
        """Calcula el porcentaje de uso total de la red."""
        total_slots = len(self.spectrum) * self.num_slots
        used_slots = sum(np.sum(arr) for arr in self.spectrum.values())
        return (used_slots / total_slots) * 100.0 if total_slots > 0 else 0.0

    def get_max_slot_used(self):
        """Retorna el índice del slot más alto utilizado en toda la red (Max FSU Index)."""
        max_slot = -1
        for slots in self.spectrum.values():
            # np.where devuelve los índices donde es True (ocupado)
            indices = np.where(slots)[0]
            if indices.size > 0:
                current_max = indices.max()
                if current_max > max_slot:
                    max_slot = current_max
        return int(max_slot)

    def reset(self):
        """Limpia todo el espectro."""
        for key in self.spectrum:
            self.spectrum[key].fill(False)
