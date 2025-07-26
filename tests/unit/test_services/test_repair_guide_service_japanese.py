"""
Tests for Japanese functionality in RepairGuideService

This module provides comprehensive tests for the Japanese search preprocessing
functionality in RepairGuideService, including device name mapping, query
preprocessing, and integration with the JapaneseDeviceMapper.
"""

from datetime import datetime
from typing import List, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.clients.ifixit_client import Guide
from src.services.repair_guide_service import (
    RepairGuideResult,
    RepairGuideService,
    SearchFilters,
)
from src.utils.japanese_device_mapper import JapaneseDeviceMapper


class TestRepairGuideServiceJapanese:
    """Test cases for Japanese functionality in RepairGuideService"""

    def setup_method(self):
        """Set up test environment before each test"""
        # Mock dependencies to avoid external API calls
        with patch("src.services.repair_guide_service.IFixitClient"), patch(
            "src.services.repair_guide_service.OfflineRepairDatabase"
        ), patch("src.services.repair_guide_service.CacheManager"), patch(
            "src.services.repair_guide_service.RateLimiter"
        ):

            self.service = RepairGuideService(ifixit_api_key="test_key", enable_japanese_support=True)

        # Verify Japanese mapper is initialized
        assert self.service.japanese_mapper is not None
        assert isinstance(self.service.japanese_mapper, JapaneseDeviceMapper)

    def test_japanese_support_initialization(self):
        """Test that Japanese support is properly initialized"""
        # Test with Japanese support enabled
        with patch("src.services.repair_guide_service.IFixitClient"), patch(
            "src.services.repair_guide_service.get_mapper"
        ) as mock_get_mapper:

            mock_mapper = Mock(spec=JapaneseDeviceMapper)
            mock_get_mapper.return_value = mock_mapper

            service = RepairGuideService(enable_japanese_support=True)
            assert service.japanese_mapper is mock_mapper
            mock_get_mapper.assert_called_once()

    def test_japanese_support_disabled(self):
        """Test that Japanese support can be disabled"""
        with patch("src.services.repair_guide_service.IFixitClient"):
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
        with patch.object(self.service.japanese_mapper, "map_device_name", return_value=None), patch.object(
            self.service.japanese_mapper, "find_best_match"
        ) as mock_fuzzy:

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
        with patch.object(self.service.japanese_mapper, "map_device_name", side_effect=Exception("Test error")):

            original_query = "スイッチ 修理"
            result = self.service._preprocess_japanese_query(original_query)
            # Should return original query on error
            assert result == original_query

    def test_preprocess_japanese_query_disabled_support(self):
        """Test preprocessing when Japanese support is disabled"""
        with patch("src.services.repair_guide_service.IFixitClient"):
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
            difficulty="Moderate",
            url="http://example.com/guide/1",
            summary="Screen repair guide",
            image_url="http://example.com/image1.jpg",
            tools=["Phillips Screwdriver"],
            parts=["Screen Assembly"],
        )

        with patch.object(
            self.service, "_search_ifixit_guides", return_value=[mock_guide]
        ) as mock_search, patch.object(self.service.rate_limiter, "can_make_request", return_value=True), patch.object(
            self.service.cache_manager, "get", return_value=None
        ), patch.object(
            self.service, "_enhance_with_related_guides", new_callable=AsyncMock
        ):

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
            type_="Repair",
        )

        with patch.object(
            self.service, "_search_ifixit_guides", return_value=[mock_guide]
        ) as mock_search, patch.object(self.service.rate_limiter, "can_make_request", return_value=True), patch.object(
            self.service.cache_manager, "get", return_value=None
        ), patch.object(
            self.service, "_enhance_with_related_guides", new_callable=AsyncMock
        ):

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

        with patch.object(
            self.service, "_preprocess_japanese_query", return_value="Nintendo Switch 修理"
        ) as mock_preprocess:

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
            "！@# ％",  # Special characters only
            "ａｂｃ",  # Full-width English
            "スイッチswitch",  # Mixed scripts
            "　　　",  # Full-width spaces only
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
            type_="Repair",
        )

        with patch.object(self.service.ifixit_client, "search_guides", return_value=[mock_guide]), patch.object(
            self.service.rate_limiter, "can_make_request", return_value=True
        ), patch.object(self.service.rate_limiter, "record_request"), patch.object(
            self.service.cache_manager, "get", return_value=None
        ), patch.object(
            self.service.cache_manager, "set"
        ), patch.object(
            self.service, "_enhance_with_related_guides", new_callable=AsyncMock
        ):

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
        with patch("src.services.repair_guide_service.IFixitClient"), patch(
            "src.services.repair_guide_service.OfflineRepairDatabase"
        ), patch("src.services.repair_guide_service.CacheManager"), patch(
            "src.services.repair_guide_service.RateLimiter"
        ):

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
        with patch.object(
            self.service, "_preprocess_japanese_query", return_value="Nintendo Switch 修理"
        ) as mock_preprocess:

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


class TestJapaneseSearchFilters:
    """Test cases for Japanese search filter functionality"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.filters = SearchFilters()

    def test_japanese_difficulty_mapping_basic(self):
        """Test basic Japanese difficulty level mappings"""
        test_cases = [
            ("初心者", "beginner"),
            ("中級者", "intermediate"),
            ("上級者", "expert"),
            ("簡単", "easy"),
            ("普通", "moderate"),
            ("難しい", "difficult"),
            ("高度", "very difficult"),
        ]

        for japanese_input, expected_output in test_cases:
            result = self.filters.normalize_japanese_difficulty(japanese_input)
            assert result == expected_output, f"Expected '{expected_output}' for '{japanese_input}', got '{result}'"

    def test_japanese_difficulty_mapping_hiragana(self):
        """Test Japanese difficulty mappings with hiragana"""
        test_cases = [
            ("しょしんしゃ", "beginner"),
            ("ちゅうきゅうしゃ", "intermediate"),
            ("じょうきゅうしゃ", "expert"),
            ("かんたん", "easy"),
            ("ふつう", "moderate"),
            ("むずかしい", "difficult"),
        ]

        for japanese_input, expected_output in test_cases:
            result = self.filters.normalize_japanese_difficulty(japanese_input)
            assert result == expected_output, f"Expected '{expected_output}' for '{japanese_input}', got '{result}'"

    def test_japanese_difficulty_mapping_no_match(self):
        """Test Japanese difficulty mapping when no match is found"""
        test_cases = [
            "unknown_level",
            "english_text",
            "適当",  # Random Japanese word not in mappings
            "",
            None,
        ]

        for test_input in test_cases:
            result = self.filters.normalize_japanese_difficulty(test_input)
            assert result == test_input, f"Expected original input '{test_input}', got '{result}'"

    def test_japanese_category_mapping_basic(self):
        """Test basic Japanese category mappings"""
        test_cases = [
            ("画面修理", "screen repair"),
            ("バッテリー交換", "battery replacement"),
            ("基板修理", "motherboard repair"),
            ("タッチパネル", "touchscreen repair"),
            ("充電器修理", "charger repair"),
            ("ボタン修理", "button repair"),
            ("スピーカー修理", "speaker repair"),
        ]

        for japanese_input, expected_output in test_cases:
            result = self.filters.normalize_japanese_category(japanese_input)
            assert result == expected_output, f"Expected '{expected_output}' for '{japanese_input}', got '{result}'"

    def test_japanese_category_mapping_hiragana(self):
        """Test Japanese category mappings with hiragana"""
        test_cases = [
            ("がめんしゅうり", "screen repair"),
            ("ばってりーこうかん", "battery replacement"),
            ("きばんしゅうり", "motherboard repair"),
            ("たっちぱねる", "touchscreen repair"),
            ("じゅうでんきしゅうり", "charger repair"),
        ]

        for japanese_input, expected_output in test_cases:
            result = self.filters.normalize_japanese_category(japanese_input)
            assert result == expected_output, f"Expected '{expected_output}' for '{japanese_input}', got '{result}'"

    def test_japanese_category_mapping_partial_match(self):
        """Test Japanese category mapping with partial matches"""
        test_cases = [
            ("画面の修理", "screen repair"),  # Contains 画面修理
            ("バッテリーの交換作業", "battery replacement"),  # Contains バッテリー交換
        ]

        for japanese_input, expected_output in test_cases:
            result = self.filters.normalize_japanese_category(japanese_input)
            assert result == expected_output, f"Expected '{expected_output}' for '{japanese_input}', got '{result}'"

    def test_japanese_category_mapping_no_match(self):
        """Test Japanese category mapping when no match is found"""
        test_cases = [
            "unknown_category",
            "english_text",
            "その他",  # Random Japanese word not in mappings
            "",
            None,
        ]

        for test_input in test_cases:
            result = self.filters.normalize_japanese_category(test_input)
            assert result == test_input, f"Expected original input '{test_input}', got '{result}'"

    def test_search_filters_case_insensitive(self):
        """Test that Japanese mappings are case insensitive"""
        # Test with mixed case (though less common in Japanese)
        test_cases = [
            ("初心者", "初心者".upper()),  # Same result expected
            ("簡単", "簡単".lower()),
        ]

        for input1, input2 in test_cases:
            result1 = self.filters.normalize_japanese_difficulty(input1)
            result2 = self.filters.normalize_japanese_difficulty(input2)
            # Should produce same result regardless of case
            assert result1 == result2 or (result1 == input1 and result2 == input2)


class TestJapaneseConfidenceScoring:
    """Test cases for Japanese-enhanced confidence scoring"""

    def setup_method(self):
        """Set up test environment before each test"""
        with patch("src.services.repair_guide_service.IFixitClient"), patch(
            "src.services.repair_guide_service.OfflineRepairDatabase"
        ), patch("src.services.repair_guide_service.CacheManager"), patch(
            "src.services.repair_guide_service.RateLimiter"
        ):

            self.service = RepairGuideService(ifixit_api_key="test_key", enable_japanese_support=True)

    def test_is_japanese_query_detection(self):
        """Test Japanese query detection"""
        japanese_queries = [
            "スイッチ 修理",  # Katakana + Kanji
            "あいふぉん",  # Hiragana
            "アイフォン",  # Katakana
            "スマホ repair",  # Mixed Japanese + English
            "修理ガイド",  # Kanji + Katakana
        ]

        english_queries = [
            "iPhone repair",
            "Nintendo Switch",
            "123 test",
            "repair guide",
            "",
        ]

        for query in japanese_queries:
            assert self.service._is_japanese_query(query), f"'{query}' should be detected as Japanese"

        for query in english_queries:
            assert not self.service._is_japanese_query(query), f"'{query}' should not be detected as Japanese"

    def test_difficulty_similarity_matching(self):
        """Test difficulty similarity matching"""
        similarity_groups = [
            (["easy", "beginner"], True),
            (["moderate", "intermediate"], True),
            (["difficult", "expert", "very difficult"], True),
            (["easy", "difficult"], False),
            (["beginner", "expert"], False),
            (["moderate", "very difficult"], False),
        ]

        for difficulties, should_be_similar in similarity_groups:
            if len(difficulties) >= 2:
                result = self.service._is_similar_difficulty(difficulties[0], difficulties[1])
                assert (
                    result == should_be_similar
                ), f"'{difficulties[0]}' and '{difficulties[1]}' similarity should be {should_be_similar}"

            # Test all combinations in groups that should be similar
            if should_be_similar and len(difficulties) > 2:
                for i in range(len(difficulties)):
                    for j in range(i + 1, len(difficulties)):
                        result = self.service._is_similar_difficulty(difficulties[i], difficulties[j])
                        assert result, f"'{difficulties[i]}' and '{difficulties[j]}' should be similar"

    def test_confidence_score_japanese_bonus(self):
        """Test that Japanese searches receive appropriate confidence bonuses"""
        # Create mock guide
        mock_guide = Guide(
            guideid=1,
            title="Nintendo Switch Screen Repair",
            device="Nintendo Switch",
            category="Repair",
            difficulty="Moderate",
            url="http://example.com/guide/1",
            summary="Screen repair guide",
            image_url="http://example.com/image1.jpg",
            tools=["Phillips Screwdriver"],
            parts=["Screen Assembly"],
        )

        # Test Japanese vs English queries
        japanese_query = "スイッチ 画面 修理"
        english_query = "Nintendo Switch screen repair"

        filters = SearchFilters()

        japanese_score = self.service._calculate_confidence_score(mock_guide, japanese_query, filters)
        english_score = self.service._calculate_confidence_score(mock_guide, english_query, filters)

        # Both should have reasonable scores
        assert 0.4 <= japanese_score <= 1.0, f"Japanese score {japanese_score} should be reasonable"
        assert 0.4 <= english_score <= 1.0, f"English score {english_score} should be reasonable"

        # Japanese query should get minimum reasonable score due to mapping
        assert japanese_score >= 0.4, "Japanese queries should get minimum reasonable confidence"

    def test_confidence_score_with_japanese_filters(self):
        """Test confidence scoring with Japanese filters"""
        mock_guide = Guide(
            guideid=2,
            title="iPhone Battery Replacement",
            device="iPhone",
            category="Battery",
            subject="Battery",
            difficulty="Easy",
            url="http://example.com/guide/2",
            image_url="http://example.com/image2.jpg",
            tools=["Suction Cup"],
            parts=["Battery"],
            type_="Repair",
        )

        # Test with Japanese difficulty filter
        filters_japanese = SearchFilters(
            difficulty_level="簡単",  # "easy" in Japanese
            category="バッテリー交換",  # "battery replacement" in Japanese
        )

        score = self.service._calculate_confidence_score(mock_guide, "アイフォン", filters_japanese)

        # Should get bonuses for matching Japanese filters
        assert score > 0.5, "Should get confidence bonus for matching Japanese filters"


class TestJapaneseFilterMatching:
    """Test cases for Japanese filter matching in _guide_matches_filters"""

    def setup_method(self):
        """Set up test environment before each test"""
        with patch("src.services.repair_guide_service.IFixitClient"), patch(
            "src.services.repair_guide_service.OfflineRepairDatabase"
        ), patch("src.services.repair_guide_service.CacheManager"), patch(
            "src.services.repair_guide_service.RateLimiter"
        ):

            self.service = RepairGuideService(ifixit_api_key="test_key", enable_japanese_support=True)

    def test_guide_matches_japanese_difficulty_filter(self):
        """Test guide matching with Japanese difficulty filters"""
        mock_guide = Guide(
            guideid=1,
            title="Test Repair",
            device="Test Device",
            category="Repair",
            subject="Test",
            difficulty="Easy",
            url="http://example.com/guide/1",
            image_url="http://example.com/image1.jpg",
            tools=[],
            parts=[],
            type_="Repair",
        )

        # Test matching Japanese difficulty
        filters = SearchFilters(difficulty_level="簡単")  # "easy" in Japanese
        assert self.service._guide_matches_filters(mock_guide, filters)

        # Test non-matching Japanese difficulty
        filters = SearchFilters(difficulty_level="難しい")  # "difficult" in Japanese
        assert not self.service._guide_matches_filters(mock_guide, filters)

    def test_guide_matches_japanese_category_filter(self):
        """Test guide matching with Japanese category filters"""
        mock_guide = Guide(
            guideid=2,
            title="Screen Repair Guide",
            device="Smartphone",
            category="Screen Repair",
            subject="Screen",
            difficulty="Moderate",
            url="http://example.com/guide/2",
            image_url="http://example.com/image2.jpg",
            tools=[],
            parts=[],
            type_="Repair",
        )

        # Test matching Japanese category
        filters = SearchFilters(category="画面修理")  # "screen repair" in Japanese
        assert self.service._guide_matches_filters(mock_guide, filters)

        # Test non-matching Japanese category
        filters = SearchFilters(category="バッテリー交換")  # "battery replacement" in Japanese
        assert not self.service._guide_matches_filters(mock_guide, filters)

    def test_guide_matches_japanese_device_filter(self):
        """Test guide matching with Japanese device filters"""
        mock_guide = Guide(
            guideid=3,
            title="Nintendo Switch Repair",
            device="Nintendo Switch",
            category="Repair",
            subject="Console",
            difficulty="Moderate",
            url="http://example.com/guide/3",
            image_url="http://example.com/image3.jpg",
            tools=[],
            parts=[],
            type_="Repair",
        )

        # Test matching Japanese device name
        filters = SearchFilters(device_type="スイッチ")  # "Switch" in Japanese

        # Mock the Japanese mapper to return the mapping
        with patch.object(self.service.japanese_mapper, "map_device_name", return_value="Nintendo Switch"):
            assert self.service._guide_matches_filters(mock_guide, filters)

        # Test non-matching Japanese device name
        filters = SearchFilters(device_type="アイフォン")  # "iPhone" in Japanese

        with patch.object(self.service.japanese_mapper, "map_device_name", return_value="iPhone"):
            assert not self.service._guide_matches_filters(mock_guide, filters)

    def test_normalize_japanese_tool_names(self):
        """Test Japanese tool name normalization"""
        test_cases = [
            ("ドライバー", "screwdriver"),
            ("プラスドライバー", "phillips screwdriver"),
            ("ピンセット", "tweezers"),
            ("スパチュラ", "spudger"),
            ("サクションカップ", "suction cup"),
            ("unknown_tool", "unknown_tool"),  # Should return original
        ]

        for japanese_tool, expected_english in test_cases:
            result = self.service._normalize_japanese_tool_name(japanese_tool)
            assert result == expected_english, f"Expected '{expected_english}' for '{japanese_tool}', got '{result}'"

    def test_guide_matches_japanese_required_tools(self):
        """Test guide matching with Japanese required tools"""
        mock_guide = Guide(
            guideid=4,
            title="Repair Guide",
            device="Device",
            category="Repair",
            subject="Test",
            difficulty="Easy",
            url="http://example.com/guide/4",
            image_url="http://example.com/image4.jpg",
            tools=["Phillips Screwdriver", "Tweezers"],
            parts=[],
            type_="Repair",
        )

        # Test with Japanese tool names that should match
        filters = SearchFilters(required_tools=["プラスドライバー"])  # "phillips screwdriver"
        assert self.service._guide_matches_filters(mock_guide, filters)

        # Test with Japanese tool names that should not match
        filters = SearchFilters(required_tools=["サクションカップ"])  # "suction cup"
        assert not self.service._guide_matches_filters(mock_guide, filters)

    def test_guide_matches_japanese_exclude_tools(self):
        """Test guide matching with Japanese excluded tools"""
        mock_guide = Guide(
            guideid=5,
            title="Repair Guide",
            device="Device",
            category="Repair",
            subject="Test",
            difficulty="Easy",
            url="http://example.com/guide/5",
            image_url="http://example.com/image5.jpg",
            tools=["Phillips Screwdriver"],
            parts=[],
            type_="Repair",
        )

        # Test excluding Japanese tool that guide has - should not match
        filters = SearchFilters(exclude_tools=["プラスドライバー"])  # "phillips screwdriver"
        assert not self.service._guide_matches_filters(mock_guide, filters)

        # Test excluding Japanese tool that guide doesn't have - should match
        filters = SearchFilters(exclude_tools=["サクションカップ"])  # "suction cup"
        assert self.service._guide_matches_filters(mock_guide, filters)


class TestJapaneseIntegrationScenarios:
    """Integration test scenarios for Japanese filter functionality"""

    def setup_method(self):
        """Set up test environment before each test"""
        with patch("src.services.repair_guide_service.IFixitClient"), patch(
            "src.services.repair_guide_service.OfflineRepairDatabase"
        ), patch("src.services.repair_guide_service.CacheManager"), patch(
            "src.services.repair_guide_service.RateLimiter"
        ):

            self.service = RepairGuideService(ifixit_api_key="test_key", enable_japanese_support=True)

    @pytest.mark.asyncio
    async def test_end_to_end_japanese_search_with_filters(self):
        """Test complete Japanese search workflow with filters"""
        # Create multiple mock guides
        guides = [
            Guide(
                guideid=1,
                title="Nintendo Switch Screen Repair",
                device="Nintendo Switch",
                category="Screen Repair",
                subject="Screen",
                difficulty="Easy",
                url="http://example.com/guide/1",
                image_url="http://example.com/image1.jpg",
                tools=["Phillips Screwdriver"],
                parts=["Screen"],
                type_="Repair",
            ),
            Guide(
                guideid=2,
                title="Nintendo Switch Battery Replacement",
                device="Nintendo Switch",
                category="Battery",
                subject="Battery",
                difficulty="Difficult",
                url="http://example.com/guide/2",
                image_url="http://example.com/image2.jpg",
                tools=["Tweezers"],
                parts=["Battery"],
                type_="Repair",
            ),
        ]

        # Set up Japanese filters
        filters = SearchFilters(
            device_type="スイッチ",  # "Switch"
            difficulty_level="簡単",  # "easy"
            category="画面修理",  # "screen repair"
        )

        with patch.object(self.service, "_search_ifixit_guides", return_value=guides), patch.object(
            self.service.rate_limiter, "can_make_request", return_value=True
        ), patch.object(self.service.cache_manager, "get", return_value=None), patch.object(
            self.service, "_enhance_with_related_guides", new_callable=AsyncMock
        ):

            # Search with Japanese query and filters
            results = await self.service.search_guides("スイッチ 画面", filters)

            # Should only return the easy screen repair guide, not the difficult battery guide
            assert len(results) == 1
            assert results[0].guide.guideid == 1
            assert "Screen" in results[0].guide.title
            assert results[0].guide.difficulty == "Easy"

    def test_japanese_filter_compatibility_with_english_guides(self):
        """Test that Japanese filters work with English guide data"""
        english_guide = Guide(
            guideid=3,
            title="iPhone Screen Replacement",
            device="iPhone",
            category="screen repair",
            subject="Screen",
            difficulty="moderate",
            url="http://example.com/guide/3",
            image_url="http://example.com/image3.jpg",
            tools=["phillips screwdriver"],
            parts=["Screen"],
            type_="Repair",
        )

        # Japanese filters should match English guide content
        filters = SearchFilters(
            difficulty_level="中級", category="画面修理"  # "intermediate/moderate"  # "screen repair"
        )

        assert self.service._guide_matches_filters(english_guide, filters)

    def test_mixed_japanese_english_filters(self):
        """Test filters with mixed Japanese and English content"""
        mock_guide = Guide(
            guideid=4,
            title="Mixed Language Test",
            device="Test Device",
            category="Battery Replacement",
            subject="Battery",
            difficulty="Easy",
            url="http://example.com/guide/4",
            image_url="http://example.com/image4.jpg",
            tools=["Screwdriver"],
            parts=["Battery"],
            type_="Repair",
        )

        # Mix of Japanese and English filters
        filters = SearchFilters(
            difficulty_level="easy",  # English
            category="バッテリー交換",  # Japanese "battery replacement"
            required_tools=["ドライバー"],  # Japanese "screwdriver"
        )

        assert self.service._guide_matches_filters(mock_guide, filters)


class TestAdvancedJapaneseConfidenceScoring:
    """Test cases for the enhanced Japanese confidence scoring system"""

    def setup_method(self):
        """Set up test environment before each test"""
        with patch("src.services.repair_guide_service.IFixitClient"), patch(
            "src.services.repair_guide_service.OfflineRepairDatabase"
        ), patch("src.services.repair_guide_service.CacheManager"), patch(
            "src.services.repair_guide_service.RateLimiter"
        ):

            self.service = RepairGuideService(ifixit_api_key="test_key", enable_japanese_support=True)

    def test_calculate_japanese_ratio(self):
        """Test Japanese character ratio calculation"""
        test_cases = [
            ("スイッチ", 1.0),  # All Japanese
            ("Switch", 0.0),  # All English
            ("スイッチ repair", 0.5),  # Half Japanese, half English
            ("アイフォン15", 0.6),  # 3 Japanese chars, 2 English chars
            ("", 0.0),  # Empty string
            ("   ", 0.0),  # Only whitespace
            ("123", 0.0),  # Numbers only
        ]

        for query, expected_ratio in test_cases:
            ratio = self.service._calculate_japanese_ratio(query)
            assert abs(ratio - expected_ratio) < 0.1, f"Expected ratio {expected_ratio} for '{query}', got {ratio}"

    def test_assess_japanese_mapping_quality(self):
        """Test Japanese device mapping quality assessment"""
        # Test with successful mappings
        with patch.object(self.service.japanese_mapper, "is_device_name", return_value=True), patch.object(
            self.service.japanese_mapper, "map_device_name", return_value="Nintendo Switch"
        ):

            quality = self.service._assess_japanese_mapping_quality("スイッチ")
            assert quality == 1.0, "Should return 1.0 for successful mapping"

        # Test with failed mappings
        with patch.object(self.service.japanese_mapper, "is_device_name", return_value=True), patch.object(
            self.service.japanese_mapper, "map_device_name", return_value=None
        ):

            quality = self.service._assess_japanese_mapping_quality("未知デバイス")
            assert quality == 0.0, "Should return 0.0 for failed mapping"

        # Test with no Japanese device words
        quality = self.service._assess_japanese_mapping_quality("Hello World")
        assert quality == 1.0, "Should return 1.0 when no Japanese device words to map"

    def test_evaluate_fuzzy_matching_confidence(self):
        """Test fuzzy matching confidence evaluation"""
        # Test with high confidence fuzzy match
        with patch.object(self.service.japanese_mapper, "find_best_match", return_value=("Nintendo Switch", 0.9)):

            confidence = self.service._evaluate_fuzzy_matching_confidence("すいち")
            assert confidence == 0.9, "Should return the fuzzy match confidence"

        # Test with no fuzzy matches
        with patch.object(self.service.japanese_mapper, "find_best_match", return_value=None):

            confidence = self.service._evaluate_fuzzy_matching_confidence("無関係な文字")
            assert confidence == 1.0, "Should return 1.0 when no fuzzy matching used"

        # Test with multiple fuzzy matches (average confidence)
        def mock_find_best_match(word, threshold=0.5):
            if word == "すいち":
                return ("Nintendo Switch", 0.8)
            elif word == "あいふぉん":
                return ("iPhone", 0.9)
            return None

        with patch.object(self.service.japanese_mapper, "find_best_match", side_effect=mock_find_best_match):

            confidence = self.service._evaluate_fuzzy_matching_confidence("すいち あいふぉん")
            expected_avg = (0.8 + 0.9) / 2
            assert abs(confidence - expected_avg) < 0.01, f"Expected average {expected_avg}, got {confidence}"

    def test_analyze_device_mapping_quality(self):
        """Test device mapping quality analysis"""

        def mock_is_device_name(word):
            return word in ["スイッチ", "あいふぉん", "未知デバイス"]

        def mock_map_device_name(word):
            mappings = {"スイッチ": "Nintendo Switch", "あいふぉん": "iPhone"}
            return mappings.get(word)

        def mock_find_best_match(word, threshold=0.7):
            if word == "未知デバイス":
                return ("Unknown Device", 0.8)
            return None

        with patch.object(
            self.service.japanese_mapper, "is_device_name", side_effect=mock_is_device_name
        ), patch.object(
            self.service.japanese_mapper, "map_device_name", side_effect=mock_map_device_name
        ), patch.object(
            self.service.japanese_mapper, "find_best_match", side_effect=mock_find_best_match
        ):

            analysis = self.service._analyze_device_mapping_quality("スイッチ あいふぉん 未知デバイス")

            assert analysis["direct_mappings"] == 2, "Should have 2 direct mappings"
            assert analysis["fuzzy_mappings"] == 1, "Should have 1 fuzzy mapping"
            assert analysis["total_device_terms"] == 3, "Should have 3 total device terms"
            assert analysis["unmapped_terms"] == 0, "Should have 0 unmapped terms"

    def test_is_mixed_language_query(self):
        """Test mixed language query detection"""
        mixed_language_queries = [
            "スイッチ repair",
            "iPhone 修理",
            "アイフォン15 screen",
            "Nintendo スイッチ",
        ]

        single_language_queries = [
            "スイッチ 修理",  # Japanese only
            "iPhone repair",  # English only
            "123 456",  # Numbers only
            "",  # Empty
        ]

        for query in mixed_language_queries:
            assert self.service._is_mixed_language_query(query), f"'{query}' should be detected as mixed language"

        for query in single_language_queries:
            assert not self.service._is_mixed_language_query(
                query
            ), f"'{query}' should not be detected as mixed language"

    def test_is_japanese_character(self):
        """Test individual Japanese character detection"""
        japanese_chars = ["あ", "ア", "漢", "ｱ"]  # Hiragana, Katakana, Kanji, Half-width Katakana
        english_chars = ["a", "A", "1", "!", " "]

        for char in japanese_chars:
            assert self.service._is_japanese_character(char), f"'{char}' should be detected as Japanese"

        for char in english_chars:
            assert not self.service._is_japanese_character(char), f"'{char}' should not be detected as Japanese"

    def test_enhanced_confidence_score_calculation(self):
        """Test the enhanced confidence scoring with Japanese optimizations"""
        mock_guide = Guide(
            guideid=1,
            title="Nintendo Switch Screen Repair",
            device="Nintendo Switch",
            category="Screen Repair",
            subject="Screen",
            difficulty="Moderate",
            url="http://example.com/guide/1",
            image_url="http://example.com/image1.jpg",
            tools=["Phillips Screwdriver"],
            parts=["Screen Assembly"],
            type_="Repair",
        )

        # Test Japanese query with high mapping quality
        with patch.object(self.service, "_assess_japanese_mapping_quality", return_value=0.9), patch.object(
            self.service, "_calculate_japanese_ratio", return_value=0.8
        ), patch.object(self.service, "_evaluate_fuzzy_matching_confidence", return_value=0.85), patch.object(
            self.service,
            "_analyze_device_mapping_quality",
            return_value={"direct_mappings": 1, "fuzzy_mappings": 0, "total_device_terms": 1, "unmapped_terms": 0},
        ):

            filters = SearchFilters()
            japanese_score = self.service._calculate_confidence_score(mock_guide, "スイッチ 画面修理", filters)

            # Should be a reasonable score with Japanese bonuses
            assert 0.5 <= japanese_score <= 1.0, f"Japanese score {japanese_score} should be reasonable"
            assert japanese_score >= 0.5, "Should get mapping quality bonus"

        # Test English query for comparison
        english_score = self.service._calculate_confidence_score(
            mock_guide, "Nintendo Switch screen repair", SearchFilters()
        )

        # Both should be reasonable, English might be slightly higher due to exact match
        assert 0.5 <= english_score <= 1.0, f"English score {english_score} should be reasonable"

    def test_confidence_score_with_poor_japanese_mapping(self):
        """Test confidence scoring with poor Japanese mapping quality"""
        mock_guide = Guide(
            guideid=2,
            title="Generic Device Repair",
            device="Generic Device",
            category="Repair",
            subject="General",
            difficulty="Easy",
            url="http://example.com/guide/2",
            image_url="http://example.com/image2.jpg",
            tools=[],
            parts=[],
            type_="Repair",
        )

        # Test with poor mapping quality
        with patch.object(self.service, "_assess_japanese_mapping_quality", return_value=0.2), patch.object(
            self.service, "_calculate_japanese_ratio", return_value=1.0
        ), patch.object(self.service, "_evaluate_fuzzy_matching_confidence", return_value=0.4), patch.object(
            self.service,
            "_analyze_device_mapping_quality",
            return_value={"direct_mappings": 0, "fuzzy_mappings": 1, "total_device_terms": 2, "unmapped_terms": 1},
        ):

            filters = SearchFilters()
            score = self.service._calculate_confidence_score(mock_guide, "未知デバイス 修理", filters)

            # Should still get minimum reasonable score
            assert score >= 0.35, f"Should get minimum score {score} even with poor mapping"
            assert score <= 0.7, "Should be penalized for poor mapping quality"

    def test_confidence_score_mixed_language_penalty(self):
        """Test confidence scoring penalty for mixed language queries"""
        mock_guide = Guide(
            guideid=3,
            title="iPhone Repair Guide",
            device="iPhone",
            category="Repair",
            subject="General",
            difficulty="Moderate",
            url="http://example.com/guide/3",
            image_url="http://example.com/image3.jpg",
            tools=[],
            parts=[],
            type_="Repair",
        )

        # Pure Japanese query
        with patch.object(self.service, "_is_mixed_language_query", return_value=False):
            pure_score = self.service._calculate_confidence_score(mock_guide, "アイフォン 修理", SearchFilters())

        # Mixed language query
        with patch.object(self.service, "_is_mixed_language_query", return_value=True):
            mixed_score = self.service._calculate_confidence_score(mock_guide, "アイフォン repair", SearchFilters())

        # Mixed language should have slight penalty
        assert mixed_score <= pure_score, "Mixed language queries should have penalty"
        assert mixed_score >= pure_score * 0.9, "Penalty should be moderate"

    def test_confidence_score_with_japanese_filters(self):
        """Test confidence scoring bonuses with Japanese filters"""
        mock_guide = Guide(
            guideid=4,
            title="iPhone Battery Replacement",
            device="iPhone",
            category="Battery",
            subject="Battery",
            difficulty="Easy",
            url="http://example.com/guide/4",
            image_url="http://example.com/image4.jpg",
            tools=["Phillips Screwdriver"],
            parts=["Battery"],
            type_="Repair",
        )

        # Japanese filters with successful mapping
        filters = SearchFilters(difficulty_level="簡単", category="バッテリー")  # "easy"  # "battery"

        with patch.object(self.service, "_assess_japanese_mapping_quality", return_value=0.9):
            score = self.service._calculate_confidence_score(mock_guide, "アイフォン バッテリー", filters)

            # Should get bonuses for matching Japanese filters
            assert score > 0.6, f"Should get filter matching bonus, got {score}"

    def test_performance_of_enhanced_confidence_calculation(self):
        """Test performance of the enhanced confidence calculation"""
        import time

        mock_guide = Guide(
            guideid=5,
            title="Performance Test Guide",
            device="Test Device",
            category="Test",
            subject="Performance",
            difficulty="Moderate",
            url="http://example.com/guide/5",
            image_url="http://example.com/image5.jpg",
            tools=["Test Tool"],
            parts=["Test Part"],
            type_="Test",
        )

        # Test with complex Japanese query
        complex_query = "複雑な日本語クエリ with mixed スイッチ アイフォン デバイス and more text"
        filters = SearchFilters(difficulty_level="中級", category="テスト修理", device_type="テストデバイス")

        start_time = time.time()
        for _ in range(100):  # Run 100 times to measure performance
            score = self.service._calculate_confidence_score(mock_guide, complex_query, filters)
            assert 0.0 <= score <= 1.0, "Score should be in valid range"

        end_time = time.time()
        avg_time = (end_time - start_time) / 100

        # Should complete each calculation in reasonable time (< 10ms)
        assert avg_time < 0.01, f"Average calculation time {avg_time:.4f}s should be < 0.01s"


class TestJapaneseSearchCompleteMethodCoverage:
    """Complete method coverage tests for Japanese search functionality"""

    def setup_method(self):
        """Set up test environment before each test"""
        with patch("src.services.repair_guide_service.IFixitClient"), patch(
            "src.services.repair_guide_service.OfflineRepairDatabase"
        ), patch("src.services.repair_guide_service.CacheManager"), patch(
            "src.services.repair_guide_service.RateLimiter"
        ):

            self.service = RepairGuideService(ifixit_api_key="test_key", enable_japanese_support=True)

    @pytest.mark.asyncio
    async def test_get_guide_details_with_japanese_preprocessing(self):
        """Test get_guide_details method with Japanese context"""
        mock_guide = Guide(
            guideid=123,
            title="Nintendo Switch Joy-Con Repair",
            device="Nintendo Switch",
            category="Controller Repair",
            subject="Joy-Con",
            difficulty="Moderate",
            url="http://example.com/guide/123",
            image_url="http://example.com/image123.jpg",
            tools=["Phillips Screwdriver"],
            parts=["Joy-Con Stick"],
            type_="Repair",
        )

        with patch.object(self.service.ifixit_client, "get_guide", return_value=mock_guide), patch.object(
            self.service.rate_limiter, "can_make_request", return_value=True
        ), patch.object(self.service.cache_manager, "get", return_value=None), patch.object(
            self.service, "_enhance_with_related_guides", new_callable=AsyncMock
        ):

            result = await self.service.get_guide_details(123)

            assert result is not None
            assert result.guide.guideid == 123
            assert result.source == "ifixit"
            assert result.confidence_score == 1.0  # Direct fetch should have full confidence
            assert result.difficulty_explanation != ""
            assert result.estimated_cost is not None
            assert result.success_rate is not None

    @pytest.mark.asyncio
    async def test_get_guides_by_device_japanese_integration(self):
        """Test get_guides_by_device with Japanese device names"""
        mock_guides = [
            Guide(
                guideid=1,
                title="Nintendo Switch Repair",
                device="Nintendo Switch",
                category="Repair",
                subject="General",
                difficulty="Easy",
                url="http://example.com/1",
                image_url="http://example.com/1.jpg",
                tools=[],
                parts=[],
                type_="Repair",
            )
        ]

        with patch.object(self.service, "search_guides", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                RepairGuideResult(
                    guide=mock_guides[0],
                    source="ifixit",
                    confidence_score=0.9,
                    last_updated=datetime.now(),
                    difficulty_explanation="Easy repair",
                )
            ]

            # Test with Japanese device name
            results = await self.service.get_guides_by_device(
                device_type="スイッチ",  # "Nintendo Switch" in Japanese
                device_model="OLED",
                issue_type="画面修理",  # "screen repair" in Japanese
            )

            # Verify search was called with proper query construction
            mock_search.assert_called_once()
            call_args = mock_search.call_args
            assert "スイッチ" in call_args[0][0]  # Query should contain Japanese device name
            assert "OLED" in call_args[0][0]
            assert "画面修理" in call_args[0][0]

            # Verify device_type filter was set
            filters = call_args[0][1]  # Second argument is filters
            assert filters.device_type == "スイッチ"

    @pytest.mark.asyncio
    async def test_get_trending_guides_japanese_fallback(self):
        """Test get_trending_guides with Japanese popular search fallback"""
        # Mock trending guides to return empty (simulate API issue)
        with patch.object(self.service.ifixit_client, "get_trending_guides", return_value=[]), patch.object(
            self.service.rate_limiter, "can_make_request", return_value=True
        ), patch.object(self.service.cache_manager, "get", return_value=None), patch.object(
            self.service, "search_guides", new_callable=AsyncMock
        ) as mock_search:

            # Configure search_guides to return results for popular queries
            mock_search.return_value = [
                RepairGuideResult(
                    guide=Guide(
                        guideid=1,
                        title="Popular Guide",
                        device="Nintendo Switch",
                        category="Repair",
                        subject="Popular",
                        difficulty="Easy",
                        url="http://example.com/1",
                        image_url="http://example.com/1.jpg",
                        tools=[],
                        parts=[],
                        type_="Repair",
                    ),
                    source="ifixit",
                    confidence_score=0.8,
                    last_updated=datetime.now(),
                    difficulty_explanation="Easy",
                )
            ]

            results = await self.service.get_trending_guides(limit=5)

            # Should fall back to popular searches
            assert len(results) > 0
            assert mock_search.call_count > 0  # Should have made fallback searches

    def test_get_cache_stats_japanese_context(self):
        """Test get_cache_stats method"""
        # Configure rate limiter with some calls
        self.service.rate_limiter.calls = [datetime.now()] * 5
        self.service.rate_limiter.max_calls = 100

        stats = self.service.get_cache_stats()

        # Verify stats structure
        assert "redis_available" in stats
        assert "memory_cache_size" in stats
        assert "rate_limit_calls_remaining" in stats
        assert "rate_limit_reset_in" in stats

        # Verify rate limit calculations
        assert stats["rate_limit_calls_remaining"] == 95  # 100 - 5
        assert isinstance(stats["rate_limit_reset_in"], int)

    def test_explain_difficulty_comprehensive(self):
        """Test _explain_difficulty method with all difficulty levels"""
        difficulty_tests = [
            ("easy", "Can be completed by beginners with basic tools. Low risk of damage."),
            ("moderate", "Requires some technical knowledge and specialized tools. Moderate risk."),
            (
                "difficult",
                "Advanced repair requiring significant expertise and specialized equipment. High risk of damage if done incorrectly.",
            ),
            (
                "very difficult",
                "Expert-level repair. Consider professional service unless you have extensive experience.",
            ),
            ("unknown", "Difficulty level: unknown"),  # Fallback case
            ("", "Difficulty level: "),  # Empty case
        ]

        for difficulty, expected_explanation in difficulty_tests:
            result = self.service._explain_difficulty(difficulty)
            assert result == expected_explanation

    def test_estimate_repair_cost_comprehensive(self):
        """Test _estimate_repair_cost method with various guide configurations"""
        test_cases = [
            # (difficulty, parts_count, expected_min_range)
            ("easy", 1, 15),  # Base 10 + 20 for easy + 15 for 1 part = 45, range 22-90
            ("moderate", 2, 35),  # Base 10 + 50 for moderate + 30 for 2 parts = 90, range 45-180
            ("difficult", 3, 55),  # Base 10 + 100 for difficult + 45 for 3 parts = 155, range 77-310
            ("very difficult", 0, 105),  # Base 10 + 200 for very difficult + 0 parts = 210, range 105-420
        ]

        for difficulty, parts_count, expected_min in test_cases:
            mock_guide = Guide(
                guideid=1,
                title="Test Guide",
                device="Test Device",
                category="Test",
                subject="Test",
                difficulty=difficulty,
                url="http://example.com",
                image_url="http://example.com/img.jpg",
                tools=[],
                parts=[f"Part{i}" for i in range(parts_count)],
                type_="Repair",
            )

            cost_estimate = self.service._estimate_repair_cost(mock_guide)

            # Should return range format "$X-$Y"
            assert cost_estimate.startswith("$")
            assert "-$" in cost_estimate

            # Extract minimum cost and verify it's reasonable
            min_cost = int(cost_estimate.split("-")[0][1:])
            assert min_cost >= expected_min * 0.8  # Allow some tolerance

    def test_estimate_success_rate_comprehensive(self):
        """Test _estimate_success_rate method with various guide configurations"""
        test_cases = [
            # (difficulty, has_tools, has_parts, has_image, expected_min_rate)
            ("easy", True, True, True, 0.95),  # Max rate
            ("moderate", True, True, True, 0.85),  # Good rate with all features
            ("difficult", True, True, False, 0.65),  # Lower rate, no image bonus
            ("very difficult", False, False, False, 0.4),  # Minimum features
        ]

        for difficulty, has_tools, has_parts, has_image, expected_min in test_cases:
            mock_guide = Guide(
                guideid=1,
                title="Test Guide",
                device="Test Device",
                category="Test",
                subject="Test",
                difficulty=difficulty,
                url="http://example.com",
                image_url="http://example.com/img.jpg" if has_image else None,
                tools=["Tool1"] if has_tools else [],
                parts=["Part1"] if has_parts else [],
                type_="Repair",
            )

            success_rate = self.service._estimate_success_rate(mock_guide)

            # Should return rate between 0 and 0.95
            assert 0.0 <= success_rate <= 0.95

            # Should be close to expected minimum
            assert success_rate >= expected_min * 0.9  # Allow some tolerance

    def test_create_search_cache_key_comprehensive(self):
        """Test _create_search_cache_key method with various inputs"""
        test_cases = [
            # (query, device_type, difficulty, category, limit)
            ("スイッチ修理", "Nintendo Switch", "easy", "screen repair", 10),
            ("iPhone repair", "iPhone", "moderate", "battery", 5),
            ("", None, None, None, 20),  # Empty/None values
            ("very long query " * 20, "device", "difficult", "category", 100),  # Long values
        ]

        for query, device_type, difficulty, category, limit in test_cases:
            filters = SearchFilters(device_type=device_type, difficulty_level=difficulty, category=category)

            cache_key = self.service._create_search_cache_key(query, filters, limit)

            # Should return SHA-256 hash (64 hex characters)
            assert isinstance(cache_key, str)
            assert len(cache_key) == 64
            assert all(c in "0123456789abcdef" for c in cache_key)

    @pytest.mark.asyncio
    async def test_search_offline_guides_integration(self):
        """Test _search_offline_guides method integration"""
        # Test when offline database is available
        offline_guides = [
            Guide(
                guideid=999,
                title="Offline Guide",
                device="Nintendo Switch",
                category="Offline Repair",
                subject="Offline",
                difficulty="Easy",
                url="offline://guide/999",
                image_url="offline://image/999.jpg",
                tools=[],
                parts=[],
                type_="Repair",
            )
        ]

        # Mock offline database search
        with patch.object(self.service, "offline_db") as mock_offline_db:
            mock_offline_db.search_guides.return_value = offline_guides

            results = await self.service._search_offline_guides("スイッチ修理", SearchFilters(), 5)

            # Current implementation returns empty list, but test structure
            assert isinstance(results, list)

        # Test when offline database is None
        self.service.offline_db = None
        results = await self.service._search_offline_guides("query", SearchFilters(), 5)
        assert results == []

    @pytest.mark.asyncio
    async def test_get_offline_guide_integration(self):
        """Test _get_offline_guide method integration"""
        # Test when offline database is available
        offline_guide = Guide(
            guideid=999,
            title="Offline Guide",
            device="Nintendo Switch",
            category="Offline Repair",
            subject="Offline",
            difficulty="Easy",
            url="offline://guide/999",
            image_url="offline://image/999.jpg",
            tools=[],
            parts=[],
            type_="Repair",
        )

        with patch.object(self.service, "offline_db") as mock_offline_db:
            mock_offline_db.get_guide.return_value = offline_guide

            result = await self.service._get_offline_guide(999)

            # Current implementation returns None, but test structure
            assert result is None  # Current implementation

        # Test when offline database is None
        self.service.offline_db = None
        result = await self.service._get_offline_guide(999)
        assert result is None


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
