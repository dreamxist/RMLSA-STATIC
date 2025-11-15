#!/usr/bin/env python3
"""
Comprehensive test suite for Static RMLSA Optimizer

Tests all components:
- Network class
- Solution representation
- Greedy algorithms
- Metaheuristics
- Full optimizer framework
"""

from data.nsfnet import create_nsfnet_topology
from data.demand_generator import generate_demand_set
from src.core.network import Network
from src.core.solution import Solution, Assignment, create_empty_solution
from src.simulator import StaticOptimizer

def test_network_class():
    """Test Network class with correct terminology"""
    print("="*80)
    print("TEST 1: Network Class")
    print("="*80)

    topology = create_nsfnet_topology()
    network = Network(topology, num_slots=100)

    # Test initial state
    assert network.get_max_slot_used() == 0, "Initial max slot should be 0"
    assert network.get_total_spectrum_consumption() == 0, "Initial consumption should be 0"
    assert network.get_spectrum_utilization() == 0.0, "Initial utilization should be 0"

    # Test allocation
    test_path = [0, 2, 5, 6]
    success = network.allocate_spectrum(test_path, start_slot=10, num_slots=5)
    assert success, "Allocation should succeed"
    assert network.get_max_slot_used() == 15, "Max slot should be 15"
    assert network.get_total_spectrum_consumption() > 0, "Should have consumption"

    print("✓ Network class tests PASSED")
    print()

def test_solution_representation():
    """Test Solution and Assignment classes"""
    print("="*80)
    print("TEST 2: Solution Representation")
    print("="*80)

    topology = create_nsfnet_topology()
    network = Network(topology, num_slots=100)
    demands = generate_demand_set(num_demands=5, seed=42)

    # Create solution
    solution = create_empty_solution(network, demands)
    assert len(solution.assignments) == 5, "Should have 5 assignment slots"
    assert not solution.is_complete(), "Empty solution should not be complete"

    # Add assignment
    assignment = Assignment(0, [0, 1, 2], 0, 10)
    solution.set_assignment(0, assignment)
    assert solution.get_assigned_count() == 1, "Should have 1 assignment"

    print("✓ Solution representation tests PASSED")
    print()

def test_greedy_algorithms():
    """Test greedy baseline algorithms"""
    print("="*80)
    print("TEST 3: Greedy Algorithms")
    print("="*80)

    topology = create_nsfnet_topology()
    optimizer = StaticOptimizer(topology, num_slots=100)
    demands = generate_demand_set(num_demands=10, seed=42)

    # Test Greedy First-Fit
    results_ff = optimizer.optimize(demands, algorithm='greedy_ff', verbose=False)
    assert results_ff['metrics']['is_valid'], "Solution should be valid"
    assert results_ff['metrics']['assigned_count'] > 0, "Should assign some demands"
    print(f"  Greedy FF: {results_ff['metrics']['assigned_count']}/{results_ff['metrics']['total_demands']} assigned, "
          f"max_slot={results_ff['metrics']['max_slot_used']}")

    # Test Greedy Min-Watermark
    results_mw = optimizer.optimize(demands, algorithm='greedy_mw', verbose=False)
    assert results_mw['metrics']['is_valid'], "Solution should be valid"
    assert results_mw['metrics']['assigned_count'] > 0, "Should assign some demands"
    print(f"  Greedy MW: {results_mw['metrics']['assigned_count']}/{results_mw['metrics']['total_demands']} assigned, "
          f"max_slot={results_mw['metrics']['max_slot_used']}")

    print("✓ Greedy algorithms tests PASSED")
    print()

def test_metaheuristics():
    """Test metaheuristic algorithms"""
    print("="*80)
    print("TEST 4: Metaheuristics")
    print("="*80)

    topology = create_nsfnet_topology()
    optimizer = StaticOptimizer(topology, num_slots=100)
    demands = generate_demand_set(num_demands=8, seed=42)  # Small for fast testing

    # Test Simulated Annealing
    results_sa = optimizer.optimize(
        demands,
        algorithm='sa',
        initial_temperature=100.0,
        final_temperature=0.1,
        cooling_rate=0.9,
        iterations_per_temp=10,
        verbose=False
    )
    assert results_sa['metrics']['is_valid'], "SA solution should be valid"
    print(f"  SA: {results_sa['metrics']['assigned_count']}/{results_sa['metrics']['total_demands']} assigned, "
          f"max_slot={results_sa['metrics']['max_slot_used']}, "
          f"time={results_sa['execution_time']:.2f}s")

    # Test Genetic Algorithm
    results_ga = optimizer.optimize(
        demands,
        algorithm='ga',
        population_size=10,
        generations=10,
        verbose=False
    )
    assert results_ga['metrics']['is_valid'], "GA solution should be valid"
    print(f"  GA: {results_ga['metrics']['assigned_count']}/{results_ga['metrics']['total_demands']} assigned, "
          f"max_slot={results_ga['metrics']['max_slot_used']}, "
          f"time={results_ga['execution_time']:.2f}s")

    print("✓ Metaheuristics tests PASSED")
    print()

def test_full_comparison():
    """Test full algorithm comparison"""
    print("="*80)
    print("TEST 5: Full Algorithm Comparison")
    print("="*80)

    topology = create_nsfnet_topology()
    optimizer = StaticOptimizer(topology, num_slots=100)
    demands = generate_demand_set(num_demands=8, seed=42)

    results = optimizer.compare_algorithms(
        demands,
        algorithms=['greedy_ff', 'greedy_mw', 'sa'],  # Skip GA for speed
        verbose=False
    )

    assert len(results) == 3, "Should have 3 algorithm results"

    for alg_name, result in results.items():
        assert result['metrics']['is_valid'], f"{alg_name} should produce valid solution"
        print(f"  {alg_name.upper():12s}: max_slot={result['metrics']['max_slot_used']:3d}, "
              f"assigned={result['metrics']['assigned_count']:2d}/{result['metrics']['total_demands']:2d}")

    print("✓ Full comparison tests PASSED")
    print()

def test_correct_metrics():
    """Verify correct metrics are used (no watermark, no blocking probability)"""
    print("="*80)
    print("TEST 6: Correct Metrics")
    print("="*80)

    topology = create_nsfnet_topology()
    optimizer = StaticOptimizer(topology, num_slots=100)
    demands = generate_demand_set(num_demands=5, seed=42)

    results = optimizer.optimize(demands, algorithm='greedy_ff', verbose=False)

    # Check correct metrics exist
    assert 'max_slot_used' in results['metrics'], "Should have max_slot_used"
    assert 'total_spectrum_consumption' in results['metrics'], "Should have total_spectrum_consumption"
    assert 'fragmentation_index' in results['metrics'], "Should have fragmentation_index"

    # Check incorrect metrics don't exist
    assert 'watermark' not in results['metrics'], "Should NOT have watermark"
    assert 'blocking_probability' not in results['metrics'], "Should NOT have blocking_probability"

    print("  ✓ Correct metrics present: max_slot_used, total_spectrum_consumption, fragmentation_index")
    print("  ✓ Incorrect metrics absent: watermark, blocking_probability")
    print("✓ Metrics tests PASSED")
    print()

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("#"*80)
    print("# COMPREHENSIVE TEST SUITE FOR STATIC RMLSA OPTIMIZER")
    print("#"*80)
    print()

    try:
        test_network_class()
        test_solution_representation()
        test_greedy_algorithms()
        test_metaheuristics()
        test_full_comparison()
        test_correct_metrics()

        print("="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print()
        print("Summary:")
        print("  ✓ Network class with correct terminology")
        print("  ✓ Solution representation and validation")
        print("  ✓ Greedy baseline algorithms")
        print("  ✓ Metaheuristics (SA, GA)")
        print("  ✓ Full optimizer framework")
        print("  ✓ Correct metrics (no watermark/blocking)")
        print()
        print("The Static RMLSA optimizer is working correctly!")
        print("="*80)

        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
