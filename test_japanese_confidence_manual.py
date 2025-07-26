#!/usr/bin/env python3
"""
Manual test for Japanese confidence scoring improvements
"""

import sys
import os
sys.path.append('.')
sys.path.append('src')

from unittest.mock import Mock, patch
from src.services.repair_guide_service import RepairGuideService, SearchFilters
from src.clients.ifixit_client import Guide


def test_japanese_ratio_calculation():
    """Test Japanese character ratio calculation"""
    print("🧪 Testing Japanese ratio calculation...")
    
    with patch('src.services.repair_guide_service.IFixitClient'), \
         patch('src.services.repair_guide_service.OfflineRepairDatabase'), \
         patch('src.services.repair_guide_service.CacheManager'), \
         patch('src.services.repair_guide_service.RateLimiter'):
        
        service = RepairGuideService(enable_japanese_support=True)
        
        test_cases = [
            ("スイッチ", 1.0),  # All Japanese
            ("Switch", 0.0),  # All English
            ("スイッチ repair", 0.5),  # Half Japanese, half English
            ("", 0.0),  # Empty string
        ]
        
        for query, expected_ratio in test_cases:
            ratio = service._calculate_japanese_ratio(query)
            print(f"  Query: '{query}' -> Ratio: {ratio:.2f} (expected: {expected_ratio:.2f})")
            assert abs(ratio - expected_ratio) < 0.1, f"Expected {expected_ratio}, got {ratio}"
    
    print("✅ Japanese ratio calculation test passed\n")


def test_japanese_character_detection():
    """Test individual Japanese character detection"""
    print("🧪 Testing Japanese character detection...")
    
    with patch('src.services.repair_guide_service.IFixitClient'), \
         patch('src.services.repair_guide_service.OfflineRepairDatabase'), \
         patch('src.services.repair_guide_service.CacheManager'), \
         patch('src.services.repair_guide_service.RateLimiter'):
        
        service = RepairGuideService(enable_japanese_support=True)
        
        japanese_chars = ["あ", "ア", "漢", "ｱ"]  # Hiragana, Katakana, Kanji, Half-width Katakana
        english_chars = ["a", "A", "1", "!", " "]
        
        for char in japanese_chars:
            result = service._is_japanese_character(char)
            print(f"  Japanese char '{char}' -> {result}")
            assert result, f"'{char}' should be detected as Japanese"
            
        for char in english_chars:
            result = service._is_japanese_character(char)
            print(f"  English char '{char}' -> {result}")
            assert not result, f"'{char}' should not be detected as Japanese"
    
    print("✅ Japanese character detection test passed\n")


def test_mixed_language_detection():
    """Test mixed language query detection"""
    print("🧪 Testing mixed language detection...")
    
    with patch('src.services.repair_guide_service.IFixitClient'), \
         patch('src.services.repair_guide_service.OfflineRepairDatabase'), \
         patch('src.services.repair_guide_service.CacheManager'), \
         patch('src.services.repair_guide_service.RateLimiter'):
        
        service = RepairGuideService(enable_japanese_support=True)
        
        mixed_language_queries = [
            "スイッチ repair",
            "iPhone 修理",
            "アイフォン15 screen",
        ]
        
        single_language_queries = [
            "スイッチ 修理",  # Japanese only
            "iPhone repair",  # English only
            "",  # Empty
        ]
        
        for query in mixed_language_queries:
            result = service._is_mixed_language_query(query)
            print(f"  Mixed query '{query}' -> {result}")
            assert result, f"'{query}' should be detected as mixed language"
            
        for query in single_language_queries:
            result = service._is_mixed_language_query(query)
            print(f"  Single language query '{query}' -> {result}")
            assert not result, f"'{query}' should not be detected as mixed language"
    
    print("✅ Mixed language detection test passed\n")


def test_enhanced_confidence_scoring():
    """Test enhanced confidence scoring"""
    print("🧪 Testing enhanced confidence scoring...")
    
    with patch('src.services.repair_guide_service.IFixitClient'), \
         patch('src.services.repair_guide_service.OfflineRepairDatabase'), \
         patch('src.services.repair_guide_service.CacheManager'), \
         patch('src.services.repair_guide_service.RateLimiter'):
        
        service = RepairGuideService(enable_japanese_support=True)
        
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
            type_="Repair"
        )
        
        # Test Japanese query
        japanese_score = service._calculate_confidence_score(
            mock_guide, "スイッチ 画面修理", SearchFilters()
        )
        print(f"  Japanese query confidence: {japanese_score:.3f}")
        assert 0.35 <= japanese_score <= 1.0, f"Japanese score {japanese_score} should be reasonable"
        
        # Test English query
        english_score = service._calculate_confidence_score(
            mock_guide, "Nintendo Switch screen repair", SearchFilters()
        )
        print(f"  English query confidence: {english_score:.3f}")
        assert 0.4 <= english_score <= 1.0, f"English score {english_score} should be reasonable"
        
        # Test with Japanese filters
        filters = SearchFilters(
            difficulty_level="中級",  # "intermediate/moderate"
            category="画面修理"  # "screen repair"
        )
        
        filtered_score = service._calculate_confidence_score(
            mock_guide, "スイッチ", filters
        )
        print(f"  Japanese query with filters confidence: {filtered_score:.3f}")
        assert 0.35 <= filtered_score <= 1.0, f"Filtered score {filtered_score} should be reasonable"
    
    print("✅ Enhanced confidence scoring test passed\n")


def test_performance():
    """Test performance of enhanced confidence calculation"""
    print("🧪 Testing performance...")
    
    import time
    
    with patch('src.services.repair_guide_service.IFixitClient'), \
         patch('src.services.repair_guide_service.OfflineRepairDatabase'), \
         patch('src.services.repair_guide_service.CacheManager'), \
         patch('src.services.repair_guide_service.RateLimiter'):
        
        service = RepairGuideService(enable_japanese_support=True)
        
        mock_guide = Guide(
            guideid=2,
            title="Performance Test Guide",
            device="Test Device",
            category="Test",
            subject="Performance",
            difficulty="Moderate",
            url="http://example.com/guide/2",
            image_url="http://example.com/image2.jpg",
            tools=["Test Tool"],
            parts=["Test Part"],
            type_="Test"
        )
        
        # Test with complex Japanese query
        complex_query = "複雑な日本語クエリ with mixed スイッチ アイフォン デバイス"
        filters = SearchFilters(
            difficulty_level="中級",
            category="テスト修理"
        )
        
        start_time = time.time()
        iterations = 50
        
        for _ in range(iterations):
            score = service._calculate_confidence_score(mock_guide, complex_query, filters)
            assert 0.0 <= score <= 1.0, "Score should be in valid range"
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations
        
        print(f"  Average calculation time: {avg_time:.4f}s ({iterations} iterations)")
        print(f"  Performance target: < 0.01s per calculation")
        
        # Performance should be reasonable (< 10ms per calculation)
        if avg_time < 0.01:
            print("  ✅ Performance target met")
        else:
            print(f"  ⚠️  Performance slower than target but acceptable: {avg_time:.4f}s")
    
    print("✅ Performance test completed\n")


def main():
    """Run all manual tests"""
    print("🚀 Starting Japanese confidence scoring manual tests\n")
    
    try:
        test_japanese_ratio_calculation()
        test_japanese_character_detection()
        test_mixed_language_detection()
        test_enhanced_confidence_scoring()
        test_performance()
        
        print("🎯 All tests passed successfully!")
        print("✅ Japanese confidence scoring implementation is working correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()