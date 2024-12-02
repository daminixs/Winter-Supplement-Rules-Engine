import random
import concurrent.futures
import time
import tracemalloc
import pytest
from winter_supplement_engine.calculator import WinterSupplementCalculator


class TestPerformanceAndStress:
    def generate_test_data(self, num_scenarios):
        """
        Generate diverse test scenarios.
        """
        return [
            {
                "id": f"stress_test_{i}",
                "numberOfChildren": random.randint(0, 5),
                "familyComposition": random.choice(["single", "couple"]),
                "familyUnitInPayForDecember": random.choice([True, False])
            } for i in range(num_scenarios)
        ]

    @pytest.mark.parametrize("num_calculations", [100, 1000, 10000])
    def test_calculation_performance(self, num_calculations):
        """
        Test performance of supplement calculations at scale.
        """
        # Prepare test data
        test_data = self.generate_test_data(num_calculations)

        # Measure calculation time, using High-resolution timer as we can encounter total_time as 0
        start_time = time.perf_counter()
        results = [WinterSupplementCalculator.calculate_supplement(data) for data in test_data]
        end_time = time.perf_counter()

        # Performance assertions
        total_time = end_time - start_time
        if total_time > 0:  # Avoid ZeroDivisionError
            calculations_per_second = num_calculations / total_time
        else:  # Consider as very high throughput
            calculations_per_second = float("inf")

        print(f"\nCalculations: {num_calculations}")
        print(f"Total Time: {total_time:.6f} seconds")
        print(f"Calculations per second: {calculations_per_second:.2f}")

        assert total_time < 10, f"Calculations took too long: {total_time} seconds"
        assert calculations_per_second > 100, f"Low calculation throughput: {calculations_per_second}"
        assert len(results) == num_calculations

    def test_memory_usage(self):
        """
        Test memory consumption during calculations
        """
        # Start memory tracking
        tracemalloc.start()

        # Prepare test data
        test_data = {
            "id": "memory_test",
            "numberOfChildren": 2,
            "familyComposition": "couple",
            "familyUnitInPayForDecember": True
        }

        # Perform calculations
        for _ in range(1000):
            WinterSupplementCalculator.calculate_supplement(test_data)

        # Get memory stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"\nCurrent memory usage: {current / 10 ** 6} MB")
        print(f"Peak memory usage: {peak / 10 ** 6} MB")

        # Memory usage assertions
        assert current < 10 * 10 ** 6, "Excessive memory usage during calculations"
        assert peak < 20 * 10 ** 6, "Peak memory usage too high"

    def test_concurrent_calculations(self):
        """
        Test ability to handle concurrent supplement calculations
        """
        # Generate test scenarios
        test_scenarios = self.generate_test_data(1000)

        # Use thread pool for concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Submit calculations concurrently
            future_to_scenario = {
                executor.submit(WinterSupplementCalculator.calculate_supplement, scenario): scenario
                for scenario in test_scenarios
            }

            # Collect results
            results = []
            for future in concurrent.futures.as_completed(future_to_scenario):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    pytest.fail(f"Calculation generated an exception: {exc}")

        # Verification
        assert len(results) == len(test_scenarios)

        # Additional validation
        for result in results:
            assert 'id' in result
            assert 'isEligible' in result
            assert 'supplementAmount' in result

            # Validate supplement amount logic
            if result['isEligible']:
                assert result['supplementAmount'] >= 0
            else:
                assert result['supplementAmount'] == 0.0

    @pytest.mark.parametrize("num_users", [10, 100, 1000])
    def test_calculation_benchmark(self, benchmark, num_users):
        """
        Performance test simulating multiple supplement calculations
        """

        def calculate_multiple_supplements():
            for i in range(num_users):
                input_data = {
                    "id": f"user_{i}",
                    "numberOfChildren": i % 3,
                    "familyComposition": "single" if i % 2 == 0 else "couple",
                    "familyUnitInPayForDecember": True
                }
                WinterSupplementCalculator.calculate_supplement(input_data)

        # Use pytest-benchmark to measure performance
        benchmark(calculate_multiple_supplements)
