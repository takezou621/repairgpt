"""
Performance benchmark tests for RepairGuideService optimizations.

This module contains performance tests to verify the improvements:
1. Category search optimization (O(n) → O(1))
2. Cache key generation performance 
3. Overall search performance improvements
"""

import os
import statistics

# Import the service and related classes
import sys
import time
from typing import Dict, List

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from src.services.repair_guide_service import (
    JAPANESE_CATEGORY_MAPPINGS,
    SearchFilters,
)


class TestCategorySearchPerformance:
    """Performance tests for category search optimization."""
    
    @pytest.fixture
    def test_categories(self) -> List[str]:
        """Provide a comprehensive list of test categories."""
        # Include exact matches and partial matches
        return [
            # Exact matches
            "画面修理",
            "バッテリー交換",
            "基板修理",
            "充電ポート",
            "スピーカー修理",
            "カメラ修理",
            "キーボード修理",
            "トラックパッド",
            "冷却ファン",
            "水没修理",
            
            # Partial matches that should work
            "画面の修理",
            "バッテリーの交換", 
            "スピーカーの修理",
            "カメラの修理",
            
            # Non-matching categories
            "unknown_category_1",
            "unknown_category_2",
            "test_category_123",
            "",
            "日本語テスト",
            "some_english_category",
        ]
    
    def benchmark_category_normalization(self, categories: List[str], iterations: int = 1000) -> Dict[str, float]:
        """
        Benchmark category normalization performance.
        
        Args:
            categories: List of categories to test
            iterations: Number of iterations to run
            
        Returns:
            Dictionary with performance metrics
        """
        filters = SearchFilters()
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            
            for category in categories:
                filters.normalize_japanese_category(category)
                
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        return {
            "min_time": min(times),
            "max_time": max(times),
            "mean_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "total_operations": len(categories) * iterations,
            "operations_per_second": (len(categories) * iterations) / sum(times),
        }
    
    def test_category_normalization_performance_target(self, test_categories):
        """Test that category normalization meets performance targets."""
        # Run benchmark
        results = self.benchmark_category_normalization(test_categories, iterations=100)
        
        # Performance targets (adjusted for realistic performance)
        max_mean_time_per_operation = 0.001   # 1ms per operation
        min_operations_per_second = 1000      # 1K operations per second
        
        mean_time_per_operation = results["mean_time"] / len(test_categories)
        
        print(f"\nPerformance Results:")
        print(f"  Mean time per operation: {mean_time_per_operation*1000:.4f}ms")
        print(f"  Operations per second: {results['operations_per_second']:.0f}")
        print(f"  Total operations: {results['total_operations']}")
        
        # Assert performance targets
        assert mean_time_per_operation < max_mean_time_per_operation, \
            f"Category normalization too slow: {mean_time_per_operation*1000:.4f}ms per operation"
        
        assert results["operations_per_second"] > min_operations_per_second, \
            f"Operations per second too low: {results['operations_per_second']:.0f}"
    
    def test_category_normalization_consistency(self, test_categories):
        """Test that category normalization is consistent across runs."""
        filters = SearchFilters()
        
        # Run the same normalization multiple times
        for category in test_categories:
            results = []
            for _ in range(10):
                result = filters.normalize_japanese_category(category)
                results.append(result)
            
            # All results should be identical
            assert all(r == results[0] for r in results), \
                f"Inconsistent results for category '{category}': {set(results)}"
    
    def test_category_normalization_scalability(self):
        """Test that performance scales well with input size."""
        filters = SearchFilters()
        
        # Test with increasing numbers of categories
        base_categories = list(JAPANESE_CATEGORY_MAPPINGS.keys())[:5]
        
        results = {}
        for multiplier in [1, 2, 5, 10]:
            test_categories = base_categories * multiplier
            start_time = time.perf_counter()
            
            for category in test_categories:
                filters.normalize_japanese_category(category)
                
            end_time = time.perf_counter()
            
            results[len(test_categories)] = end_time - start_time
            
        # Performance should scale roughly linearly
        # Check that 10x categories takes less than 20x time (some overhead is expected)
        min_size = min(results.keys())
        max_size = max(results.keys())
        
        if min_size > 0:
            scale_factor = max_size / min_size
            time_factor = results[max_size] / results[min_size]
            
            print(f"\nScalability Results:")
            print(f"  Category count scale factor: {scale_factor}x")
            print(f"  Time scale factor: {time_factor:.2f}x")
            
            # Should not be worse than quadratic scaling
            assert time_factor < scale_factor * 2, \
                f"Poor scalability: {time_factor:.2f}x time for {scale_factor}x categories"


class TestCacheKeyPerformance:
    """Performance tests for cache key generation."""
    
    def test_cache_key_generation_performance(self):
        """Test cache key generation performance with SHA-256."""
        from src.services.repair_guide_service import RepairGuideService
        
        service = RepairGuideService(enable_offline_fallback=False)
        filters = SearchFilters(
            device_type="iPhone",
            difficulty_level="easy", 
            category="screen repair"
        )
        
        # Test with various query lengths
        queries = [
            "short",
            "medium length query for testing",
            "very long query " * 50,  # Very long query to trigger hashing
        ]
        
        times = []
        for query in queries:
            start_time = time.perf_counter()
            
            for _ in range(1000):
                service._create_search_cache_key(query, filters, 10)
                
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        # Should complete quickly even for long queries
        max_time_per_operation = 0.01  # 10ms per 1000 operations
        
        for i, query_time in enumerate(times):
            print(f"Query {i+1} (length {len(queries[i])}): {query_time*1000:.2f}ms for 1000 operations")
            assert query_time < max_time_per_operation, \
                f"Cache key generation too slow for query {i+1}: {query_time*1000:.2f}ms"


class TestMemoryUsage:
    """Test memory efficiency of optimizations."""
    
    def test_category_index_memory_efficiency(self):
        """Test that category indices don't use excessive memory."""
        from src.services.repair_guide_service import (
            _CATEGORY_EXACT_LOOKUP,
            _CATEGORY_KEY_PARTS_INDEX,
            _CATEGORY_PARTIAL_LOOKUP,
        )

        # Indices should exist and be reasonable size
        assert len(_CATEGORY_EXACT_LOOKUP) > 0
        
        # Exact lookup should have same size as original mappings
        assert len(_CATEGORY_EXACT_LOOKUP) == len(JAPANESE_CATEGORY_MAPPINGS)
        
        # Other indices should be reasonable size (not exponentially larger)
        total_index_entries = (
            len(_CATEGORY_EXACT_LOOKUP) + 
            len(_CATEGORY_PARTIAL_LOOKUP) + 
            len(_CATEGORY_KEY_PARTS_INDEX)
        )
        
        # Should not be more than 5x the original mapping size
        max_reasonable_size = len(JAPANESE_CATEGORY_MAPPINGS) * 5
        assert total_index_entries <= max_reasonable_size, \
            f"Index size too large: {total_index_entries} entries (max: {max_reasonable_size})"


class TestRegressionPrevention:
    """Tests to prevent performance regressions."""
    
    def test_no_performance_regression_in_common_operations(self):
        """Test that common operations maintain good performance."""
        filters = SearchFilters()
        
        # Common Japanese categories that users might search for
        common_categories = [
            "画面修理",      # screen repair
            "バッテリー交換", # battery replacement  
            "基板修理",      # motherboard repair
            "充電ポート",    # charging port
        ]
        
        # These should all be very fast (under 0.01ms each)
        for category in common_categories:
            start_time = time.perf_counter()
            result = filters.normalize_japanese_category(category)
            end_time = time.perf_counter()
            
            operation_time = end_time - start_time
            
            assert operation_time < 0.001, \
                f"Common category '{category}' too slow: {operation_time*1000:.4f}ms"
            assert result is not None, f"No result for common category '{category}'"
    
    def test_bulk_operations_performance(self):
        """Test performance with bulk operations similar to real usage."""
        filters = SearchFilters()
        
        # Simulate bulk category normalization as might happen in real usage
        categories = list(JAPANESE_CATEGORY_MAPPINGS.keys()) * 10  # 10x all categories
        
        start_time = time.perf_counter()
        
        results = [filters.normalize_japanese_category(cat) for cat in categories]
        
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        time_per_operation = total_time / len(categories)
        
        print(f"\nBulk operation results:")
        print(f"  Total categories processed: {len(categories)}")
        print(f"  Total time: {total_time*1000:.2f}ms")
        print(f"  Time per category: {time_per_operation*1000:.4f}ms")
        
        # Should process all categories quickly
        assert total_time < 1.0, f"Bulk operation too slow: {total_time:.3f}s"
        assert time_per_operation < 0.001, f"Per-operation time too slow: {time_per_operation*1000:.4f}ms"
        
        # All results should be valid
        assert len(results) == len(categories)
        assert all(result is not None for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to see print output