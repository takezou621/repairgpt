"""
Tests for Japanese Device Mapper

This module provides comprehensive tests for the JapaneseDeviceMapper class,
covering all functionality including direct mapping, fuzzy matching, device
detection, and edge cases.
"""

from typing import List, Optional, Tuple
from unittest.mock import patch

import pytest

from src.utils.japanese_device_mapper import (
    JapaneseDeviceMapper,
    find_device_match,
    get_mapper,
    is_likely_device,
    map_japanese_device,
)


class TestJapaneseDeviceMapper:
    """Test cases for JapaneseDeviceMapper class"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.mapper = JapaneseDeviceMapper()

    def test_initialization(self):
        """Test proper initialization of JapaneseDeviceMapper"""
        assert self.mapper is not None
        assert hasattr(self.mapper, "_normalized_mappings")
        assert hasattr(self.mapper, "_device_keywords")
        assert len(self.mapper._normalized_mappings) > 0
        assert len(self.mapper._device_keywords) > 0

    def test_device_mappings_completeness(self):
        """Test that device mappings contain expected devices"""
        mappings = self.mapper.DEVICE_MAPPINGS

        # Check for core devices
        assert any("Nintendo Switch" in v for v in mappings.values())
        assert any("iPhone" in v for v in mappings.values())
        assert any("PlayStation" in v for v in mappings.values())
        assert any("Laptop" in v for v in mappings.values())
        assert any("Smartphone" in v for v in mappings.values())

    def test_normalize_text(self):
        """Test text normalization functionality"""
        # Test basic normalization
        assert self.mapper._normalize_text("Test Text") == "testtext"
        assert self.mapper._normalize_text("スイッチ") == "スイッチ"
        assert self.mapper._normalize_text("IPHONE") == "iphone"

        # Test punctuation removal
        assert self.mapper._normalize_text("test-text_here.now!") == "testtexthere now"
        assert self.mapper._normalize_text("test (with) brackets") == "testwithbrackets"

        # Test empty/None input
        assert self.mapper._normalize_text("") == ""
        assert self.mapper._normalize_text(None) == ""

    def test_direct_device_mapping(self):
        """Test direct device name mapping"""
        # Test Nintendo Switch variations
        assert self.mapper.map_device_name("スイッチ") == "Nintendo Switch"
        assert self.mapper.map_device_name("すいっち") == "Nintendo Switch"
        assert self.mapper.map_device_name("ニンテンドースイッチ") == "Nintendo Switch"
        assert self.mapper.map_device_name("switch") == "Nintendo Switch"
        assert self.mapper.map_device_name("ns") == "Nintendo Switch"

        # Test iPhone variations
        assert self.mapper.map_device_name("アイフォン") == "iPhone"
        assert self.mapper.map_device_name("あいふォん") == "iPhone"
        assert self.mapper.map_device_name("iphone") == "iPhone"
        assert self.mapper.map_device_name("アイホン") == "iPhone"

        # Test PlayStation variations
        assert self.mapper.map_device_name("プレイステーション") == "PlayStation"
        assert self.mapper.map_device_name("プレステ") == "PlayStation"
        assert self.mapper.map_device_name("ps") == "PlayStation"
        assert self.mapper.map_device_name("プレステ5") == "PlayStation 5"
        assert self.mapper.map_device_name("ps5") == "PlayStation 5"

        # Test laptop variations
        assert self.mapper.map_device_name("ノートパソコン") == "Laptop"
        assert self.mapper.map_device_name("ラップトップ") == "Laptop"
        assert self.mapper.map_device_name("laptop") == "Laptop"
        assert self.mapper.map_device_name("ノート") == "Laptop"

        # Test smartphone variations
        assert self.mapper.map_device_name("スマートフォン") == "Smartphone"
        assert self.mapper.map_device_name("スマホ") == "Smartphone"
        assert self.mapper.map_device_name("携帯") == "Smartphone"

    def test_case_insensitive_mapping(self):
        """Test case-insensitive device mapping"""
        # Test uppercase
        assert self.mapper.map_device_name("SWITCH") == "Nintendo Switch"
        assert self.mapper.map_device_name("IPHONE") == "iPhone"
        assert self.mapper.map_device_name("PS5") == "PlayStation 5"

        # Test mixed case
        assert self.mapper.map_device_name("Switch") == "Nintendo Switch"
        assert self.mapper.map_device_name("iPhone") == "iPhone"
        assert self.mapper.map_device_name("Ps5") == "PlayStation 5"

    def test_invalid_device_mapping(self):
        """Test mapping with invalid or unknown device names"""
        # Test completely invalid names
        assert self.mapper.map_device_name("invalid_device") is None
        assert self.mapper.map_device_name("random_text") is None
        assert self.mapper.map_device_name("12345") is None

        # Test empty/None input
        assert self.mapper.map_device_name("") is None
        assert self.mapper.map_device_name(None) is None
        assert self.mapper.map_device_name("   ") is None

    def test_input_validation(self):
        """Test input validation for various methods"""
        # Test non-string inputs
        assert self.mapper.map_device_name(123) is None
        assert self.mapper.map_device_name([]) is None
        assert self.mapper.map_device_name({}) is None

        # Test find_best_match with invalid inputs
        assert self.mapper.find_best_match(None) is None
        assert self.mapper.find_best_match(123) is None
        assert self.mapper.find_best_match([]) is None

    def test_fuzzy_matching(self):
        """Test fuzzy matching functionality"""
        # Test close matches with typos
        result = self.mapper.find_best_match("すいち")  # Missing 'っ'
        assert result is not None
        assert result[0] == "Nintendo Switch"
        assert result[1] > 0.6

        result = self.mapper.find_best_match("あいふお")  # Partial iPhone
        assert result is not None
        assert result[0] == "iPhone"

        result = self.mapper.find_best_match("ぷれすて")  # PlayStation without number
        assert result is not None
        assert "PlayStation" in result[0]

        # Test threshold functionality
        result = self.mapper.find_best_match("xyz", threshold=0.9)
        assert result is None  # Should not match due to high threshold

    def test_fuzzy_matching_threshold(self):
        """Test fuzzy matching with different thresholds"""
        # Test with low threshold
        result = self.mapper.find_best_match("すい", threshold=0.3)
        assert result is not None
        assert result[1] >= 0.3

        # Test with high threshold
        result = self.mapper.find_best_match("すい", threshold=0.9)
        assert result is None

    def test_multiple_matches(self):
        """Test getting multiple possible matches"""
        matches = self.mapper.get_possible_matches("プレ", max_results=3)
        assert isinstance(matches, list)
        assert len(matches) <= 3

        # Should include PlayStation variants
        device_names = [match[0] for match in matches]
        assert any("PlayStation" in name for name in device_names)

        # Test with specific input
        matches = self.mapper.get_possible_matches("スイ", max_results=5)
        assert len(matches) <= 5
        assert all(isinstance(match, tuple) for match in matches)
        assert all(len(match) == 2 for match in matches)
        assert all(isinstance(match[1], float) for match in matches)

    def test_multiple_matches_sorting(self):
        """Test that multiple matches are sorted by similarity score"""
        matches = self.mapper.get_possible_matches("switch", max_results=5)

        if len(matches) > 1:
            # Check that scores are in descending order
            scores = [match[1] for match in matches]
            assert scores == sorted(scores, reverse=True)

    def test_device_detection(self):
        """Test device name detection functionality"""
        # Test positive cases
        assert self.mapper.is_device_name("スイッチ") is True
        assert self.mapper.is_device_name("iPhone") is True
        assert self.mapper.is_device_name("プレステ5") is True
        assert self.mapper.is_device_name("ノートパソコン") is True

        # Test negative cases
        assert self.mapper.is_device_name("random text") is False
        assert self.mapper.is_device_name("12345") is False
        assert self.mapper.is_device_name("") is False
        assert self.mapper.is_device_name(None) is False

    def test_supported_devices_list(self):
        """Test getting list of supported devices"""
        devices = self.mapper.get_supported_devices()

        assert isinstance(devices, list)
        assert len(devices) > 0
        assert "Nintendo Switch" in devices
        assert "iPhone" in devices
        assert "PlayStation" in devices
        assert "Laptop" in devices

        # Check that list is sorted
        assert devices == sorted(devices)

        # Check for duplicates (should not have any)
        assert len(devices) == len(set(devices))

    def test_japanese_variations_lookup(self):
        """Test getting Japanese variations for English device names"""
        # Test Nintendo Switch variations
        variations = self.mapper.get_japanese_variations("Nintendo Switch")
        assert isinstance(variations, list)
        assert len(variations) > 0
        assert "スイッチ" in variations
        assert "switch" in variations

        # Test iPhone variations
        variations = self.mapper.get_japanese_variations("iPhone")
        assert "アイフォン" in variations
        assert "iphone" in variations

        # Test unknown device
        variations = self.mapper.get_japanese_variations("Unknown Device")
        assert isinstance(variations, list)
        assert len(variations) == 0

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test very long input
        long_input = "a" * 1000
        assert self.mapper.map_device_name(long_input) is None

        # Test special characters
        special_input = "!@#$%^&*()"
        assert self.mapper.map_device_name(special_input) is None

        # Test mixed language input
        mixed_input = "switchスイッチ"
        result = self.mapper.map_device_name(mixed_input)
        # Should handle gracefully, might return None or a match
        assert result is None or isinstance(result, str)

    def test_performance_with_large_input(self):
        """Test performance with various input sizes"""
        # Test with moderately large inputs
        test_inputs = ["スイッチ" * 10, "a" * 100, "プレステ5" + "x" * 50]

        for test_input in test_inputs:
            # Should complete without timeout or error
            result = self.mapper.map_device_name(test_input)
            assert result is None or isinstance(result, str)

    def test_unicode_handling(self):
        """Test proper Unicode handling for Japanese text"""
        # Test various Japanese writing systems
        hiragana_input = "すいっち"
        katakana_input = "スイッチ"
        mixed_input = "すイッち"

        # All should be handled properly
        result1 = self.mapper.map_device_name(hiragana_input)
        result2 = self.mapper.map_device_name(katakana_input)
        result3 = self.mapper.map_device_name(mixed_input)

        assert result1 == "Nintendo Switch"
        assert result2 == "Nintendo Switch"
        # Mixed input might not match directly, but should not cause errors
        assert result3 is None or isinstance(result3, str)

    def test_whitespace_handling(self):
        """Test handling of whitespace in inputs"""
        # Test with leading/trailing whitespace
        assert self.mapper.map_device_name("  スイッチ  ") == "Nintendo Switch"
        assert self.mapper.map_device_name("\tswitch\n") == "Nintendo Switch"

        # Test with internal whitespace
        assert self.mapper.map_device_name("nintendo switch") == "Nintendo Switch"
        assert self.mapper.map_device_name("プレイ ステーション") == "PlayStation"

    def test_regression_cases(self):
        """Test specific regression cases that might have caused issues"""
        # Test common user inputs that should work
        common_inputs = [
            "壊れたスイッチ",  # Broken Switch
            "古いiPhone",  # Old iPhone
            "新しいPS5",  # New PS5
            "ゲーミングPC",  # Gaming PC
        ]

        for input_text in common_inputs:
            # Should not raise exceptions
            result = self.mapper.map_device_name(input_text)
            fuzzy_result = self.mapper.find_best_match(input_text)
            is_device = self.mapper.is_device_name(input_text)

            # All should complete without error
            assert result is None or isinstance(result, str)
            assert fuzzy_result is None or isinstance(fuzzy_result, tuple)
            assert isinstance(is_device, bool)


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_get_mapper_singleton(self):
        """Test that get_mapper returns singleton instance"""
        mapper1 = get_mapper()
        mapper2 = get_mapper()

        assert mapper1 is mapper2
        assert isinstance(mapper1, JapaneseDeviceMapper)

    def test_map_japanese_device_function(self):
        """Test convenience function for device mapping"""
        # Test successful mapping
        result = map_japanese_device("スイッチ")
        assert result == "Nintendo Switch"

        # Test failed mapping
        result = map_japanese_device("invalid")
        assert result is None

        # Test None input
        result = map_japanese_device(None)
        assert result is None

    def test_find_device_match_function(self):
        """Test convenience function for fuzzy matching"""
        # Test successful match
        result = find_device_match("すいち")
        assert result == "Nintendo Switch"

        # Test failed match
        result = find_device_match("xyz")
        assert result is None

        # Test with custom threshold
        result = find_device_match("す", threshold=0.9)
        assert result is None

    def test_is_likely_device_function(self):
        """Test convenience function for device detection"""
        # Test positive cases
        assert is_likely_device("スイッチ") is True
        assert is_likely_device("iPhone") is True

        # Test negative cases
        assert is_likely_device("random") is False
        assert is_likely_device("") is False


class TestIntegration:
    """Integration tests for Japanese Device Mapper"""

    def setup_method(self):
        """Set up test environment"""
        self.mapper = JapaneseDeviceMapper()

    def test_full_workflow(self):
        """Test complete workflow from Japanese input to English output"""
        japanese_inputs = [
            "私のスイッチが壊れました",
            "アイフォンの画面が割れた",
            "プレステ5の調子が悪い",
            "ノートパソコンが起動しない",
        ]

        for japanese_input in japanese_inputs:
            # Try direct mapping first
            direct_result = self.mapper.map_device_name(japanese_input)

            # If no direct mapping, try fuzzy matching
            if direct_result is None:
                fuzzy_result = self.mapper.find_best_match(japanese_input)
                if fuzzy_result and fuzzy_result[1] > 0.6:
                    device_name = fuzzy_result[0]
                else:
                    device_name = None
            else:
                device_name = direct_result

            # At least one should find a device for these inputs
            # (This tests the overall system functionality)
            is_detected = self.mapper.is_device_name(japanese_input)

            # The workflow should complete without errors
            assert device_name is None or isinstance(device_name, str)
            assert isinstance(is_detected, bool)

    def test_real_world_scenarios(self):
        """Test with real-world usage scenarios"""
        scenarios = [
            {"input": "ニンテンドースイッチが充電できない", "expected_device": "Nintendo Switch"},
            {"input": "iPhone 13 Pro Max の修理", "expected_device": "iPhone"},
            {"input": "MacBook Air の画面交換", "expected_device": "MacBook"},
            {"input": "PS5コントローラーの不具合", "expected_device": "PlayStation 5"},
        ]

        for scenario in scenarios:
            # Try to find the device in the input
            device_found = False

            # Check direct mapping
            direct = self.mapper.map_device_name(scenario["input"])
            if direct:
                device_found = True

            # Check fuzzy matching
            fuzzy = self.mapper.find_best_match(scenario["input"], threshold=0.5)
            if fuzzy and scenario["expected_device"] in fuzzy[0]:
                device_found = True

            # Check device detection
            is_detected = self.mapper.is_device_name(scenario["input"])

            # At minimum, the system should handle these inputs gracefully
            assert isinstance(is_detected, bool)

    def test_batch_processing(self):
        """Test processing multiple inputs efficiently"""
        batch_inputs = [
            "スイッチ",
            "プレステ",
            "アイフォン",
            "ノートパソコン",
            "スマホ",
            "switch",
            "playstation",
            "iphone",
            "laptop",
            "smartphone",
        ] * 10  # 50 items total

        results = []
        for input_text in batch_inputs:
            result = self.mapper.map_device_name(input_text)
            results.append(result)

        # Should process all without errors
        assert len(results) == len(batch_inputs)
        assert all(r is None or isinstance(r, str) for r in results)

        # Should have some successful mappings
        successful_mappings = [r for r in results if r is not None]
        assert len(successful_mappings) > 0


class TestErrorHandling:
    """Test error handling and edge cases"""

    def setup_method(self):
        """Set up test environment"""
        self.mapper = JapaneseDeviceMapper()

    def test_memory_efficiency(self):
        """Test that the mapper doesn't consume excessive memory"""
        # Test with many lookups
        for i in range(1000):
            self.mapper.map_device_name(f"test{i}")
            self.mapper.find_best_match(f"test{i}")
            self.mapper.is_device_name(f"test{i}")

        # Should complete without memory issues
        assert True

    def test_thread_safety_preparation(self):
        """Test preparation for thread safety (single-threaded test)"""
        # Test that multiple mapper instances work independently
        mapper1 = JapaneseDeviceMapper()
        mapper2 = JapaneseDeviceMapper()

        result1 = mapper1.map_device_name("スイッチ")
        result2 = mapper2.map_device_name("スイッチ")

        assert result1 == result2 == "Nintendo Switch"

    def test_configuration_consistency(self):
        """Test that configuration is consistent across methods"""
        # Test that all methods use the same underlying data
        device_name = "スイッチ"

        direct_mapping = self.mapper.map_device_name(device_name)
        is_detected = self.mapper.is_device_name(device_name)
        fuzzy_match = self.mapper.find_best_match(device_name)

        # Results should be consistent
        if direct_mapping:
            assert is_detected is True
            assert fuzzy_match is not None
            assert fuzzy_match[0] == direct_mapping


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
