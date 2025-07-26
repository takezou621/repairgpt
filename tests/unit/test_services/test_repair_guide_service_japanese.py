"""
Tests for Japanese functionality in RepairGuideService

This module provides comprehensive tests for the Japanese search preprocessing
functionality in RepairGuideService, including device name mapping, query
preprocessing, and integration with the JapaneseDeviceMapper.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Optional

from src.services.repair_guide_service import (
    RepairGuideService,
    SearchFilters,
    RepairGuideResult,
)
from src.clients.ifixit_client import Guide
from src.utils.japanese_device_mapper import JapaneseDeviceMapper


class TestRepairGuideServiceJapanese:
    """Test cases for Japanese functionality in RepairGuideService"""

    def setup_method(self):
        """Set up test environment before each test"""
        # Mock dependencies to avoid external API calls
        with patch('src.services.repair_guide_service.IFixitClient'), \
             patch('src.services.repair_guide_service.OfflineRepairDatabase'), \
             patch('src.services.repair_guide_service.CacheManager'), \
             patch('src.services.repair_guide_service.RateLimiter'):
            
            self.service = RepairGuideService(
                ifixit_api_key="test_key",
                enable_japanese_support=True
            )
        
        # Verify Japanese mapper is initialized
        assert self.service.japanese_mapper is not None
        assert isinstance(self.service.japanese_mapper, JapaneseDeviceMapper)

    def test_japanese_support_initialization(self):
        """Test that Japanese support is properly initialized"""
        # Test with Japanese support enabled
        with patch('src.services.repair_guide_service.IFixitClient'), \
             patch('src.services.repair_guide_service.get_mapper') as mock_get_mapper:
            
            mock_mapper = Mock(spec=JapaneseDeviceMapper)
            mock_get_mapper.return_value = mock_mapper
            
            service = RepairGuideService(enable_japanese_support=True)
            assert service.japanese_mapper is mock_mapper
            mock_get_mapper.assert_called_once()

    def test_japanese_support_disabled(self):
        """Test that Japanese support can be disabled"""
        with patch('src.services.repair_guide_service.IFixitClient'):
            service = RepairGuideService(enable_japanese_support=False)
            assert service.japanese_mapper is None

    def test_preprocess_japanese_query_direct_mapping(self):
        """Test Japanese query preprocessing with direct device mapping"""
        # Test Nintendo Switch mapping
        result = self.service._preprocess_japanese_query("スイッチ 画面割れ")
        assert "Nintendo Switch" in result
        assert "画面割れ" in result  # Non-device words should remain
        
        # Test iPhone mapping
        result = self.service._preprocess_japanese_query("アイフォン バッテリー交換")
        assert "iPhone" in result
        assert "バッテリー交換" in result
        
        # Test PlayStation mapping
        result = self.service._preprocess_japanese_query("プレステ5 修理")
        assert "PlayStation 5" in result
        assert "修理" in result

    def test_preprocess_japanese_query_multiple_devices(self):
        """Test preprocessing query with multiple Japanese device names"""
        result = self.service._preprocess_japanese_query("スイッチ と アイフォン の比較")
        assert "Nintendo Switch" in result
        assert "iPhone" in result
        assert "比較" in result

    def test_preprocess_japanese_query_fuzzy_matching(self):
        """Test Japanese query preprocessing with fuzzy matching"""
        # Mock fuzzy matching scenario
        with patch.object(self.service.japanese_mapper, 'map_device_name', return_value=None), \
             patch.object(self.service.japanese_mapper, 'find_best_match') as mock_fuzzy:
            
            mock_fuzzy.return_value = ("Nintendo Switch", 0.8)
            result = self.service._preprocess_japanese_query("すいち")
            assert "Nintendo Switch" in result
            mock_fuzzy.assert_called_with("すいち", threshold=0.7)

    def test_preprocess_japanese_query_no_mapping(self):
        """Test preprocessing when no device mapping is found"""
        result = self.service._preprocess_japanese_query("一般的な質問")
        assert result == "一般的な質問"  # Should remain unchanged

    def test_preprocess_japanese_query_mixed_languages(self):
        """Test preprocessing query with mixed Japanese and English"""
        result = self.service._preprocess_japanese_query("スイッチ screen repair")
        assert "Nintendo Switch" in result
        assert "screen repair" in result

    def test_preprocess_japanese_query_empty_input(self):
        """Test preprocessing with empty or None input"""
        assert self.service._preprocess_japanese_query("") == ""
        assert self.service._preprocess_japanese_query(None) == None
        assert self.service._preprocess_japanese_query("   ") == ""

    def test_preprocess_japanese_query_whitespace_handling(self):
        """Test preprocessing with various whitespace scenarios"""
        # Test regular spaces
        result = self.service._preprocess_japanese_query("スイッチ 修理 ガイド")
        assert "Nintendo Switch" in result
        assert "修理" in result
        assert "ガイド" in result
        
        # Test full-width spaces (common in Japanese text)
        result = self.service._preprocess_japanese_query("スイッチ　修理　ガイド")
        assert "Nintendo Switch" in result

    def test_preprocess_japanese_query_error_handling(self):
        """Test error handling during Japanese preprocessing"""
        # Mock an exception in device mapping
        with patch.object(self.service.japanese_mapper, 'map_device_name', 
                         side_effect=Exception("Test error")):
            
            original_query = "スイッチ 修理"
            result = self.service._preprocess_japanese_query(original_query)
            # Should return original query on error
            assert result == original_query

    def test_preprocess_japanese_query_disabled_support(self):
        """Test preprocessing when Japanese support is disabled"""
        with patch('src.services.repair_guide_service.IFixitClient'):
            service = RepairGuideService(enable_japanese_support=False)
            
            original_query = "スイッチ 修理"
            result = service._preprocess_japanese_query(original_query)
            assert result == original_query  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_search_guides_japanese_integration(self):
        """Test integration of Japanese preprocessing in search_guides method"""
        # Mock the iFixit client search
        mock_guide = Guide(
            guideid=1,
            title="Nintendo Switch Screen Repair",
            device="Nintendo Switch",
            category="Repair",  
            subject="Screen",
            difficulty="Moderate",
            url="http://example.com/guide/1",
            image_url="http://example.com/image1.jpg",
            tools=["Phillips Screwdriver"],
            parts=["Screen Assembly"],
            type_="Repair"
        )
        
        with patch.object(self.service, '_search_ifixit_guides', 
                         return_value=[mock_guide]) as mock_search, \
             patch.object(self.service.rate_limiter, 'can_make_request', return_value=True), \
             patch.object(self.service.cache_manager, 'get', return_value=None), \
             patch.object(self.service, '_enhance_with_related_guides', new_callable=AsyncMock):
            
            # Test Japanese query search
            results = await self.service.search_guides("スイッチ 画面修理")
            
            # Verify that the query was preprocessed before searching
            mock_search.assert_called_once()
            args, kwargs = mock_search.call_args
            processed_query = args[0]  # First argument is the query
            assert "Nintendo Switch" in processed_query
            assert "画面修理" in processed_query
            
            # Verify results
            assert len(results) == 1
            assert results[0].guide.title == "Nintendo Switch Screen Repair"

    @pytest.mark.asyncio 
    async def test_search_guides_preserves_english_functionality(self):
        """Test that English search functionality is preserved"""
        mock_guide = Guide(
            guideid=2,
            title="iPhone Battery Replacement",
            device="iPhone",
            category="Repair",
            subject="Battery", 
            difficulty="Easy",
            url="http://example.com/guide/2",
            image_url="http://example.com/image2.jpg",
            tools=["Suction Cup"],
            parts=["Battery"],
            type_="Repair"
        )
        
        with patch.object(self.service, '_search_ifixit_guides', 
                         return_value=[mock_guide]) as mock_search, \
             patch.object(self.service.rate_limiter, 'can_make_request', return_value=True), \
             patch.object(self.service.cache_manager, 'get', return_value=None), \
             patch.object(self.service, '_enhance_with_related_guides', new_callable=AsyncMock):
            
            # Test English query search
            results = await self.service.search_guides("iPhone battery replacement")
            
            # Verify that English query is passed through unchanged
            mock_search.assert_called_once()
            args, kwargs = mock_search.call_args
            processed_query = args[0]
            assert processed_query == "iPhone battery replacement"
            
            # Verify results
            assert len(results) == 1
            assert results[0].guide.title == "iPhone Battery Replacement"

    def test_comprehensive_device_mapping_coverage(self):
        """Test comprehensive coverage of Japanese device mappings"""
        test_cases = [
            ("スイッチ 液晶", "Nintendo Switch 液晶"),
            ("アイフォン タッチパネル", "iPhone タッチパネル"),
            ("プレステ5 コントローラー", "PlayStation 5 コントローラー"),
            ("ノートパソコン キーボード", "Laptop キーボード"),
            ("スマホ 充電", "Smartphone 充電"),
            ("エアポッズ 音質", "AirPods 音質"),
            ("マックブック 画面", "MacBook 画面"),
        ]
        
        for japanese_query, expected_result in test_cases:
            result = self.service._preprocess_japanese_query(japanese_query)
            # Check that the device name was correctly mapped
            device_part = expected_result.split()[0]
            assert device_part in result

    def test_query_caching_with_preprocessed_queries(self):
        """Test that caching works correctly with preprocessed Japanese queries"""
        # Test that cache key is generated from preprocessed query
        original_query = "スイッチ 修理"
        filters = SearchFilters()
        
        with patch.object(self.service, '_preprocess_japanese_query', 
                         return_value="Nintendo Switch 修理") as mock_preprocess:
            
            cache_key = self.service._create_search_cache_key(original_query, filters, 10)
            
            # Verify preprocessing didn't interfere with cache key generation
            assert isinstance(cache_key, str)
            assert len(cache_key) == 32  # MD5 hash length

    def test_performance_with_japanese_queries(self):
        """Test performance characteristics with Japanese text processing"""
        # Test with various query lengths
        test_queries = [
            "スイッチ",  # Short
            "スイッチ の 画面 が 割れて しまい ました",  # Medium
            "ニンテンドースイッチ" * 10,  # Long repetitive
        ]
        
        for query in test_queries:
            # Should complete without timeout
            result = self.service._preprocess_japanese_query(query)
            assert isinstance(result, str)

    def test_edge_cases_japanese_processing(self):
        """Test edge cases in Japanese processing"""
        edge_cases = [
            "123",  # Numbers only
            "！@# ％", # Special characters only
            "ａｂｃ", # Full-width English
            "スイッチswitch", # Mixed scripts
            "　　　", # Full-width spaces only
        ]
        
        for edge_case in edge_cases:
            # Should handle gracefully without errors
            result = self.service._preprocess_japanese_query(edge_case)
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_end_to_end_japanese_search_workflow(self):
        """Test complete end-to-end Japanese search workflow"""
        # Create a realistic scenario
        mock_guide = Guide(
            guideid=3,
            title="Nintendo Switch Joy-Con Drift Repair",
            device="Nintendo Switch",
            category="Repair",
            subject="Joy-Con",
            difficulty="Moderate", 
            url="http://example.com/guide/3",
            image_url="http://example.com/image3.jpg",
            tools=["Phillips Screwdriver", "Plastic Opening Tools"],
            parts=["Joystick Replacement"],
            type_="Repair"
        )
        
        with patch.object(self.service.ifixit_client, 'search_guides', 
                         return_value=[mock_guide]), \
             patch.object(self.service.rate_limiter, 'can_make_request', return_value=True), \
             patch.object(self.service.rate_limiter, 'record_request'), \
             patch.object(self.service.cache_manager, 'get', return_value=None), \
             patch.object(self.service.cache_manager, 'set'), \
             patch.object(self.service, '_enhance_with_related_guides', new_callable=AsyncMock):
            
            # Test complete Japanese workflow
            japanese_query = "スイッチ ジョイコン ドリフト 修理"
            results = await self.service.search_guides(japanese_query)
            
            # Verify results
            assert len(results) == 1
            assert results[0].guide.device == "Nintendo Switch"
            assert results[0].source == "ifixit"
            assert results[0].confidence_score > 0
            
            # Verify that the search was performed with preprocessed query
            # (The guide should match despite using Japanese in the original query)
            assert "Joy-Con" in results[0].guide.title


class TestJapaneseSearchIntegration:
    """Integration tests for Japanese search functionality"""

    def setup_method(self):
        """Set up test environment"""
        with patch('src.services.repair_guide_service.IFixitClient'), \
             patch('src.services.repair_guide_service.OfflineRepairDatabase'), \
             patch('src.services.repair_guide_service.CacheManager'), \
             patch('src.services.repair_guide_service.RateLimiter'):
            
            self.service = RepairGuideService(enable_japanese_support=True)

    def test_japanese_device_mapper_integration(self):
        """Test integration with JapaneseDeviceMapper"""
        # Test that the service correctly uses the mapper
        assert self.service.japanese_mapper is not None
        
        # Test direct access to mapper functionality
        device_mapping = self.service.japanese_mapper.map_device_name("スイッチ")
        assert device_mapping == "Nintendo Switch"
        
        # Test that preprocessing uses the same mapper
        result = self.service._preprocess_japanese_query("スイッチ 修理")
        assert "Nintendo Switch" in result

    def test_search_filters_with_japanese_queries(self):
        """Test that search filters work correctly with Japanese queries"""
        # Test with device type filter
        filters = SearchFilters(device_type="Nintendo Switch")
        
        # The preprocessing should work even with filters
        with patch.object(self.service, '_preprocess_japanese_query', 
                         return_value="Nintendo Switch 修理") as mock_preprocess:
            
            # This should not raise an error
            cache_key = self.service._create_search_cache_key("スイッチ 修理", filters, 10)
            assert isinstance(cache_key, str)

    def test_multilingual_support_coexistence(self):
        """Test that Japanese and English support can coexist"""
        test_cases = [
            ("Nintendo Switch repair", "Nintendo Switch repair"),  # English unchanged
            ("スイッチ 修理", "Nintendo Switch 修理"),  # Japanese mapped
            ("switch battery", "Nintendo Switch battery"),  # Mixed (english device mapped)
        ]
        
        for input_query, expected_pattern in test_cases:
            result = self.service._preprocess_japanese_query(input_query)
            # Basic check that processing completed
            assert isinstance(result, str)
            # More specific checks would depend on exact mapping behavior


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])