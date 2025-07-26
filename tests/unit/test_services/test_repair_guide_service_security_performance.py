"""
Unit tests for RepairGuideService security and performance improvements.

This module tests the fixes for:
1. MD5 → SHA-256 security improvements
2. Category search performance optimization (O(n) → O(1))
3. Type safety improvements
4. Enhanced error handling
"""

import hashlib
import pytest
import time
from unittest.mock import MagicMock, patch
from typing import Dict, List

# Import the service and related classes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from src.services.repair_guide_service import (
    RepairGuideService,
    SearchFilters,
    CacheManager,
    JAPANESE_CATEGORY_MAPPINGS,
    _CATEGORY_EXACT_LOOKUP,
    _CATEGORY_PARTIAL_LOOKUP,
    _CATEGORY_KEY_PARTS_INDEX,
)


class TestSecurityImprovements:
    """Test security improvements (MD5 → SHA-256)."""
    
    def test_cache_manager_uses_sha256_for_long_identifiers(self):
        """Test that CacheManager uses SHA-256 for long identifiers."""
        cache_manager = CacheManager()
        
        # Test with long identifier (> 100 characters)
        long_identifier = "a" * 150
        cache_key = cache_manager._make_key("guide", long_identifier)
        
        # Extract the hashed part from the cache key
        # Format is "repairgpt:guide:{hash}"
        hashed_part = cache_key.split(":")[-1]
        
        # SHA-256 produces 64-character hex strings
        assert len(hashed_part) == 64
        
        # Verify it's actually SHA-256
        expected_hash = hashlib.sha256(long_identifier.encode()).hexdigest()
        assert hashed_part == expected_hash
        
    def test_cache_manager_short_identifiers_unchanged(self):
        """Test that short identifiers are not hashed."""
        cache_manager = CacheManager()
        
        # Test with short identifier
        short_identifier = "short_id"
        cache_key = cache_manager._make_key("guide", short_identifier)
        
        # Should be "repairgpt:guide:short_id"
        assert cache_key == f"repairgpt:guide:{short_identifier}"
        
    def test_search_cache_key_uses_sha256(self):
        """Test that search cache key generation uses SHA-256."""
        service = RepairGuideService(enable_offline_fallback=False)
        filters = SearchFilters(device_type="iPhone", difficulty_level="easy", category="screen repair")
        
        # Create a query that will result in a long cache key
        long_query = "a" * 200
        cache_key = service._create_search_cache_key(long_query, filters, 10)
        
        # SHA-256 produces 64-character hex strings
        assert len(cache_key) == 64
        
        # Verify it's a valid hex string
        int(cache_key, 16)  # This will raise ValueError if not valid hex
        
    def test_sha256_different_inputs_produce_different_hashes(self):
        """Test that different inputs produce different SHA-256 hashes."""
        cache_manager = CacheManager()
        
        id1 = "a" * 150
        id2 = "b" * 150
        
        key1 = cache_manager._make_key("guide", id1)
        key2 = cache_manager._make_key("guide", id2)
        
        # Different inputs should produce different cache keys
        assert key1 != key2


class TestPerformanceOptimizations:
    """Test performance optimization for category search."""
    
    def test_category_indices_are_built(self):
        """Test that category lookup indices are properly built."""
        # Check that the indices are populated
        assert len(_CATEGORY_EXACT_LOOKUP) > 0
        assert len(_CATEGORY_PARTIAL_LOOKUP) >= 0  # May be empty if no complex mappings
        assert len(_CATEGORY_KEY_PARTS_INDEX) >= 0
        
        # Verify exact lookup contains all original mappings
        for japanese_term, english_term in JAPANESE_CATEGORY_MAPPINGS.items():
            assert _CATEGORY_EXACT_LOOKUP[japanese_term] == english_term
    
    def test_category_normalization_performance(self):
        """Test performance improvement in category normalization."""
        filters = SearchFilters()
        
        # Test categories that should be found in the mapping
        test_categories = [
            "画面修理",
            "バッテリー交換", 
            "基板修理",
            "充電ポート",
            "スピーカー修理"
        ]
        
        # Measure time for multiple lookups
        start_time = time.perf_counter()
        
        for _ in range(1000):  # Run many iterations
            for category in test_categories:
                result = filters.normalize_japanese_category(category)
                assert result  # Should return a valid result
                
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        # Should complete very quickly (under 0.1 seconds for 5000 lookups)
        assert execution_time < 0.1, f"Category normalization too slow: {execution_time:.4f}s"
    
    def test_exact_category_mapping(self):
        """Test exact category mapping works correctly."""
        filters = SearchFilters()
        
        # Test exact matches
        assert filters.normalize_japanese_category("画面修理") == "screen repair"
        assert filters.normalize_japanese_category("バッテリー交換") == "battery replacement"
        assert filters.normalize_japanese_category("基板修理") == "motherboard repair"
    
    def test_partial_category_matching_optimized(self):
        """Test that partial matching is optimized and works correctly."""
        filters = SearchFilters()
        
        # Test partial matches that should work with the optimized algorithm
        # These should match because they contain key parts
        test_cases = [
            ("画面の修理", "screen repair"),  # Contains both "画面" and "修理"
            ("バッテリーの交換", "battery replacement"),  # Contains both "バッテリー" and "交換"
        ]
        
        for input_category, expected_output in test_cases:
            result = filters.normalize_japanese_category(input_category)
            assert result == expected_output, f"Expected {expected_output}, got {result} for {input_category}"
    
    def test_category_normalization_fallback(self):
        """Test that normalization returns original category when no mapping found."""
        filters = SearchFilters()
        
        # Test with category that has no mapping
        unmapped_category = "unknown_category_12345"
        result = filters.normalize_japanese_category(unmapped_category)
        assert result == unmapped_category
    
    def test_empty_category_handling(self):
        """Test handling of empty or None categories."""
        filters = SearchFilters()
        
        assert filters.normalize_japanese_category("") == ""
        assert filters.normalize_japanese_category(None) == None


class TestTypeSafetyImprovements:
    """Test type safety improvements."""
    
    def test_optional_related_guides_type(self):
        """Test that related_guides field accepts Optional[List[Guide]]."""
        from src.services.repair_guide_service import RepairGuideResult
        from src.clients.ifixit_client import Guide
        from datetime import datetime
        
        # Test with None
        result = RepairGuideResult(
            guide=MagicMock(spec=Guide),
            source="test",
            confidence_score=0.5,
            last_updated=datetime.now(),
            related_guides=None  # Should accept None
        )
        assert result.related_guides is None
        
        # Test with empty list
        result.related_guides = []
        assert result.related_guides == []
        
        # Test with list of guides
        mock_guides = [MagicMock(spec=Guide), MagicMock(spec=Guide)]
        result.related_guides = mock_guides
        assert result.related_guides == mock_guides


class TestEnhancedErrorHandling:
    """Test enhanced error handling with specific exceptions."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a RepairGuideService with mocked dependencies."""
        service = RepairGuideService(enable_offline_fallback=False)
        service.ifixit_client = MagicMock()
        service.rate_limiter.can_make_request = MagicMock(return_value=True)
        return service
    
    async def test_connection_error_handling_in_search(self, mock_service):
        """Test specific handling of connection errors in search."""
        # Mock a connection error
        mock_service.ifixit_client.search_guides.side_effect = ConnectionError("Network error")
        
        with patch('src.services.repair_guide_service.logger') as mock_logger:
            results = await mock_service.search_guides("test query")
            
            # Should handle the error gracefully and return empty results
            assert results == []
            
            # Should log specific connection error
            mock_logger.error.assert_called_once()
            error_message = mock_logger.error.call_args[0][0]
            assert "connection failed" in error_message.lower()
    
    async def test_timeout_error_handling_in_search(self, mock_service):
        """Test specific handling of timeout errors in search."""
        # Mock a timeout error
        mock_service.ifixit_client.search_guides.side_effect = TimeoutError("Request timeout")
        
        with patch('src.services.repair_guide_service.logger') as mock_logger:
            results = await mock_service.search_guides("test query")
            
            # Should handle the error gracefully and return empty results
            assert results == []
            
            # Should log specific connection error (TimeoutError is handled as connection error)
            mock_logger.error.assert_called_once()
            error_message = mock_logger.error.call_args[0][0]
            assert "connection failed" in error_message.lower()
    
    async def test_value_error_handling_in_search(self, mock_service):
        """Test specific handling of value errors in search."""
        # Mock a value error (invalid response)
        mock_service.ifixit_client.search_guides.side_effect = ValueError("Invalid JSON response")
        
        with patch('src.services.repair_guide_service.logger') as mock_logger:
            results = await mock_service.search_guides("test query")
            
            # Should handle the error gracefully and return empty results
            assert results == []
            
            # Should log specific invalid response error
            mock_logger.error.assert_called_once()
            error_message = mock_logger.error.call_args[0][0]
            assert "invalid response" in error_message.lower()
    
    async def test_generic_error_handling_in_search(self, mock_service):
        """Test handling of unexpected errors in search."""
        # Mock an unexpected error
        mock_service.ifixit_client.search_guides.side_effect = RuntimeError("Unexpected error")
        
        with patch('src.services.repair_guide_service.logger') as mock_logger:
            results = await mock_service.search_guides("test query")
            
            # Should handle the error gracefully and return empty results
            assert results == []
            
            # Should log unexpected error
            mock_logger.error.assert_called_once()
            error_message = mock_logger.error.call_args[0][0]
            assert "unexpected error" in error_message.lower()


class TestBackwardsCompatibility:
    """Test that changes maintain backwards compatibility."""
    
    def test_japanese_category_mappings_unchanged(self):
        """Test that the original mappings are preserved."""
        # Verify some key mappings are still present
        expected_mappings = {
            "画面修理": "screen repair",
            "バッテリー交換": "battery replacement",
            "基板修理": "motherboard repair",
            "充電ポート": "charging port repair",
        }
        
        for japanese, english in expected_mappings.items():
            assert JAPANESE_CATEGORY_MAPPINGS[japanese] == english
    
    def test_search_filters_backward_compatibility(self):
        """Test that SearchFilters maintains backward compatibility."""
        # Should be able to create with old usage patterns
        filters = SearchFilters()
        assert filters.device_type is None
        assert filters.difficulty_level is None
        assert filters.category is None
        assert filters.language == "en"
        
        # Should be able to set values as before
        filters.device_type = "iPhone"
        filters.difficulty_level = "easy"
        filters.category = "screen repair"
        
        assert filters.device_type == "iPhone"
        assert filters.difficulty_level == "easy"
        assert filters.category == "screen repair"
    
    def test_repair_guide_service_initialization(self):
        """Test that RepairGuideService can still be initialized as before."""
        # Should work with no parameters
        service1 = RepairGuideService()
        assert service1 is not None
        
        # Should work with parameters
        service2 = RepairGuideService(
            ifixit_api_key="test_key",
            redis_url="redis://localhost:6379",
            enable_offline_fallback=True,
            enable_japanese_support=True
        )
        assert service2 is not None


class TestIntegrationScenarios:
    """Test integration scenarios that combine multiple improvements."""
    
    def test_japanese_category_search_with_caching(self):
        """Test Japanese category search with SHA-256 caching."""
        service = RepairGuideService(enable_offline_fallback=False)
        filters = SearchFilters(category="画面修理")  # Japanese category
        
        # This should use the optimized category normalization
        normalized = filters.normalize_japanese_category("画面修理")
        assert normalized == "screen repair"
        
        # Cache key should use SHA-256
        cache_key = service._create_search_cache_key("iPhone", filters, 10)
        assert len(cache_key) == 64  # SHA-256 produces 64-char hex
    
    async def test_error_handling_with_japanese_support(self):
        """Test error handling works correctly with Japanese features."""
        service = RepairGuideService(enable_offline_fallback=False)
        service.ifixit_client = MagicMock()
        service.ifixit_client.search_guides.side_effect = ConnectionError("Network error")
        service.rate_limiter.can_make_request = MagicMock(return_value=True)
        
        filters = SearchFilters(category="画面修理")  # Japanese input
        
        with patch('src.services.repair_guide_service.logger') as mock_logger:
            results = await service.search_guides("iPhone", filters)
            
            # Should handle error gracefully even with Japanese input
            assert results == []
            mock_logger.error.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])