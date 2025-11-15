"""
Modulation Formats Table
Defines relationship between distance, modulation format, and spectrum efficiency
"""
import math


# Modulation formats table
# Format: (name, max_reach_km, bits_per_symbol, slots_per_100Gbps)
MODULATION_FORMATS = [
    ("16-QAM", 500, 4, 2),      # Highest efficiency, shortest reach
    ("8-QAM", 1000, 3, 3),      # Medium-high efficiency
    ("QPSK", 2000, 2, 4),       # Medium efficiency
    ("BPSK", 4000, 1, 8),       # Lowest efficiency, longest reach
]


def get_modulation_format(distance_km):
    """
    Select appropriate modulation format based on path distance.

    The format is selected based on maximum reach. Longer distances
    require more robust (but less efficient) modulation formats.

    Args:
        distance_km (float): Total path distance in kilometers

    Returns:
        dict: Modulation format info with keys:
              - name: Format name (e.g., "QPSK")
              - max_reach: Maximum reach in km
              - bits_per_symbol: Spectral efficiency
              - slots_per_100gbps: Slots needed for 100 Gbps
    """
    for name, max_reach, bits_per_symbol, slots_per_100gbps in MODULATION_FORMATS:
        if distance_km <= max_reach:
            return {
                "name": name,
                "max_reach": max_reach,
                "bits_per_symbol": bits_per_symbol,
                "slots_per_100gbps": slots_per_100gbps
            }

    # If distance exceeds all formats, return None (unreachable)
    return None


def calculate_required_slots(bandwidth_gbps, distance_km):
    """
    Calculate number of spectrum slots required for a demand.

    Args:
        bandwidth_gbps (float): Requested bandwidth in Gbps
        distance_km (float): Total path distance in km

    Returns:
        tuple: (num_slots, modulation_format_name) or (None, None) if unreachable
    """
    modulation = get_modulation_format(distance_km)

    if modulation is None:
        # Distance too long for any modulation format
        return None, None

    # Calculate slots needed based on bandwidth and format efficiency
    # Formula: slots = ceil(bandwidth / 100) * slots_per_100gbps
    slots_needed = math.ceil(bandwidth_gbps / 100.0) * modulation["slots_per_100gbps"]

    # Add guard band (1 slot on each side)
    slots_with_guard = slots_needed + 2

    return slots_with_guard, modulation["name"]


def get_modulation_table():
    """
    Returns the complete modulation formats table.

    Returns:
        list: List of tuples (name, max_reach, bits_per_symbol, slots_per_100gbps)
    """
    return MODULATION_FORMATS


if __name__ == "__main__":
    # Test modulation selection
    print("Modulation Formats Table:")
    print("-" * 70)
    print(f"{'Format':<10} {'Max Reach (km)':<15} {'Bits/Symbol':<15} {'Slots/100Gbps':<15}")
    print("-" * 70)
    for name, reach, bits, slots in MODULATION_FORMATS:
        print(f"{name:<10} {reach:<15} {bits:<15} {slots:<15}")

    print("\n" + "=" * 70)
    print("Test Cases:")
    print("=" * 70)

    test_cases = [
        (100, 400),   # 100 Gbps, 400 km
        (50, 1500),   # 50 Gbps, 1500 km
        (200, 2500),  # 200 Gbps, 2500 km
        (100, 5000),  # 100 Gbps, 5000 km (unreachable)
    ]

    for bandwidth, distance in test_cases:
        slots, format_name = calculate_required_slots(bandwidth, distance)
        if slots:
            print(f"{bandwidth} Gbps over {distance} km: {slots} slots ({format_name})")
        else:
            print(f"{bandwidth} Gbps over {distance} km: UNREACHABLE")
