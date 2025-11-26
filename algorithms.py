import random
import numpy as np
from topology import get_k_shortest_paths, get_path_distance, get_node_names
from core import calculate_slots, Network


# --- BASELINE: SP-FF ---
def run_sp_ff(topology, demands, k=3, num_slots=640, export_file=None):
    """
    Ejecuta SP-FF secuencialmente.
    """
    net = Network(topology, num_slots)
    node_names = get_node_names()
    assigned_count = 0

    if export_file:
        export_file.write(
            f"{'ID':<5} {'Source':<15} {'Dest':<15} {'GBPS':<6} {'Status':<10} {'Slots':<10} {'Modulation':<10} {'Path'}\n"
        )
        export_file.write("-" * 100 + "\n")

    for demand in demands:
        src_id, dst_id = demand["source"], demand["destination"]
        bw = demand["bandwidth"]
        paths = get_k_shortest_paths(topology, src_id, dst_id, k)
        allocated = False
        row_str = ""

        for path in paths:
            dist = get_path_distance(topology, path)
            slots_needed, mod_name = calculate_slots(bw, dist)

            if not slots_needed:
                continue

            start_slot = net.find_first_fit(path, slots_needed)

            if start_slot is not None:
                net.allocate(path, start_slot, slots_needed)
                assigned_count += 1
                allocated = True

                s_name = node_names.get(src_id, str(src_id))
                d_name = node_names.get(dst_id, str(dst_id))
                slot_range = f"{start_slot}-{start_slot + slots_needed - 1}"
                path_str = "->".join(map(str, path))

                row_str = f"{demand['id']:<5} {s_name:<15} {d_name:<15} {bw:<6} {'ASSIGNED':<10} {slot_range:<10} {mod_name:<10} {path_str}\n"
                break

        if not allocated:
            s_name = node_names.get(src_id, str(src_id))
            d_name = node_names.get(dst_id, str(dst_id))
            row_str = f"{demand['id']:<5} {s_name:<15} {d_name:<15} {bw:<6} {'BLOCKED':<10} {'-':<10} {'-':<10} {'-'}\n"

        if export_file:
            export_file.write(row_str)

    return {
        "assigned": assigned_count,
        "total": len(demands),
        "utilization": net.get_utilization(),
        "max_slot": net.get_max_slot_used(),
    }


# --- GENETIC ALGORITHM OPTIMIZADO ---
class GeneticOptimizer:
    def __init__(
        self, topology, demands, pop_size=100, generations=200, num_slots=320, k_paths=5
    ):
        self.topology = topology
        self.demands = demands
        self.pop_size = pop_size
        self.generations = generations
        self.num_slots = num_slots
        self.k_paths = k_paths
        self.rng = random.Random(42)
        self.path_cache = {}
        self._precompute_paths(k=self.k_paths)

    def _precompute_paths(self, k):
        for d in self.demands:
            key = (d["source"], d["destination"])
            if key not in self.path_cache:
                self.path_cache[key] = get_k_shortest_paths(
                    self.topology, key[0], key[1], k
                )

    def _evaluate_fitness(self, chromosome):
        net = Network(self.topology, self.num_slots)
        assigned = 0
        sum_start_indices = 0

        ordered_demands = [self.demands[i] for i in chromosome]

        for demand in ordered_demands:
            src, dst = demand["source"], demand["destination"]
            paths = self.path_cache.get((src, dst), [])

            for path in paths:
                dist = get_path_distance(self.topology, path)
                slots, _ = calculate_slots(demand["bandwidth"], dist)
                if slots:
                    start = net.find_first_fit(path, slots)
                    if start is not None:
                        net.allocate(path, start, slots)
                        assigned += 1
                        sum_start_indices += start
                        break

        max_slot = net.get_max_slot_used()

        score = (
            (assigned * 1_000_000_000)
            + ((self.num_slots - max_slot) * 1_000_000)
            - (sum_start_indices)
        )

        return score, max_slot, assigned, sum_start_indices

    def optimize(self, export_file_handle=None):
        indices = list(range(len(self.demands)))
        population = []

        # 1. Semilla Maestra LPF
        dists = []
        for i in indices:
            d = self.demands[i]
            paths = self.path_cache.get((d["source"], d["destination"]), [])
            dist = get_path_distance(self.topology, paths[0]) if paths else 0
            dists.append(dist)

        lpf_chrome = [x for _, x in sorted(zip(dists, indices), reverse=True)]
        population.append(lpf_chrome[:])

        # 2. Inicialización por Vecindad
        print("[GA] Inicializando población con variaciones de LPF...")
        while len(population) < self.pop_size:
            clone = lpf_chrome[:]
            r = self.rng.random()
            if r < 0.4:
                self._mutate_swap(clone)
            elif r < 0.7:
                self._mutate_scramble(clone)
            else:
                self._mutate_shift_priority(clone)
            population.append(clone)

        best_chrome = None
        best_fitness = -float("inf")

        global_best_assigned = 0
        global_best_msi = self.num_slots
        stagnation_counter = 0

        print(f"{'Gen':<5} | {'MSI':<5} | {'Asignadas':<10} | {'Compactación':<30}")
        print("-" * 60)

        for gen in range(self.generations):
            fitness_data = []

            for chrom in population:
                fit_val, msi, asg, compactness = self._evaluate_fitness(chrom)
                fitness_data.append((chrom, fit_val, msi, asg, compactness))

            fitness_data.sort(key=lambda x: x[1], reverse=True)

            current_top = fitness_data[0]
            current_fit = current_top[1]
            current_msi = current_top[2]
            current_asg = current_top[3]
            current_compact = current_top[4]

            real_improvement = False
            if current_msi < global_best_msi:
                global_best_msi = current_msi
                real_improvement = True

            if current_asg > global_best_assigned:
                global_best_assigned = current_asg
                real_improvement = True

            if current_fit > best_fitness:
                best_fitness = current_fit
                best_chrome = current_top[0][:]

            if real_improvement:
                stagnation_counter = 0
                print(
                    f"{gen:<5} | {current_msi:<5} | {current_asg:<10} | {current_compact:<30} <--- MEJORA MSI!"
                )
            else:
                stagnation_counter += 1

            if gen % 10 == 0 and not real_improvement:
                print(
                    f"{gen:<5} | {global_best_msi:<5} | {global_best_assigned:<10} | {current_compact:<30} (Estancado: {stagnation_counter})"
                )

            # --- CATACLISMO RÁPIDO ---
            if stagnation_counter >= 12:
                print("   >>> CATACLISMO (Rápido): Reiniciando vecindad...")
                next_pop = [best_chrome[:]]

                while len(next_pop) < self.pop_size:
                    c = best_chrome[:]
                    self._mutate_scramble(c)
                    self._mutate_shift_priority(c)
                    if self.rng.random() < 0.5:
                        self._mutate_swap(c)
                    next_pop.append(c)

                population = next_pop
                stagnation_counter = 0
                continue

            # Selección y Cruce
            elite_count = max(2, int(self.pop_size * 0.1))
            next_pop = [x[0] for x in fitness_data[:elite_count]]

            while len(next_pop) < self.pop_size:
                p1 = self._tournament(fitness_data)
                p2 = self._tournament(fitness_data)
                child = self._crossover_ox1(p1, p2)

                if self.rng.random() < 0.3:
                    r_mut = self.rng.random()
                    if r_mut < 0.33:
                        self._mutate_swap(child)
                    elif r_mut < 0.66:
                        self._mutate_scramble(child)
                    else:
                        self._mutate_shift_priority(child)

                next_pop.append(child)

            population = next_pop

        print(
            f"\n[GA] FINAL -> Asignadas: {global_best_assigned}, Max Slot: {global_best_msi}"
        )

        final_demands = [self.demands[i] for i in best_chrome]
        return run_sp_ff(
            self.topology,
            final_demands,
            k=self.k_paths,
            num_slots=self.num_slots,
            export_file=export_file_handle,
        )

    def _tournament(self, scored_pop):
        sample = self.rng.sample(scored_pop, 4)
        return max(sample, key=lambda x: x[1])[0]

    def _crossover_ox1(self, p1, p2):
        size = len(p1)
        a, b = sorted(self.rng.sample(range(size), 2))
        child = [-1] * size
        child[a:b] = p1[a:b]
        current_p2 = 0
        for i in range(size):
            if i >= a and i < b:
                continue
            while p2[current_p2] in child:
                current_p2 += 1
            child[i] = p2[current_p2]
        return child

    def _mutate_swap(self, chrome):
        i1, i2 = self.rng.sample(range(len(chrome)), 2)
        chrome[i1], chrome[i2] = chrome[i2], chrome[i1]

    def _mutate_scramble(self, chrome):
        a, b = sorted(self.rng.sample(range(len(chrome)), 2))
        sub = chrome[a:b]
        self.rng.shuffle(sub)
        chrome[a:b] = sub

    def _mutate_shift_priority(self, chrome):
        size = len(chrome)
        idx = self.rng.randint(size // 2, size - 1)
        val = chrome.pop(idx)
        chrome.insert(0, val)
