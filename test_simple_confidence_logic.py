#!/usr/bin/env python3
"""
Simple test for Japanese confidence scoring logic without dependencies
"""

def test_japanese_character_detection():
    """Test Japanese character detection logic"""
    print("🧪 Testing Japanese character detection...")
    
    def is_japanese_character(char):
        """Check if a single character is Japanese"""
        char_code = ord(char)
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FAF),  # CJK Unified Ideographs (Kanji)
            (0xFF66, 0xFF9D),  # Half-width Katakana
        ]
        
        for start, end in japanese_ranges:
            if start <= char_code <= end:
                return True
        return False
    
    # Test Japanese characters
    japanese_chars = ["あ", "ア", "漢", "ｱ"]
    for char in japanese_chars:
        result = is_japanese_character(char)
        print(f"  Japanese char '{char}' (U+{ord(char):04X}) -> {result}")
        assert result, f"'{char}' should be detected as Japanese"
    
    # Test non-Japanese characters
    english_chars = ["a", "A", "1", "!", " "]
    for char in english_chars:
        result = is_japanese_character(char)
        print(f"  English char '{char}' -> {result}")
        assert not result, f"'{char}' should not be detected as Japanese"
    
    print("✅ Japanese character detection passed\n")


def test_japanese_ratio_calculation():
    """Test Japanese character ratio calculation"""
    print("🧪 Testing Japanese ratio calculation...")
    
    def calculate_japanese_ratio(query):
        """Calculate the ratio of Japanese characters in the query"""
        if not query:
            return 0.0
            
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FAF),  # CJK Unified Ideographs (Kanji)
            (0xFF66, 0xFF9D),  # Half-width Katakana
        ]
        
        japanese_char_count = 0
        total_char_count = 0
        
        for char in query:
            if char.isspace():
                continue  # Skip whitespace
                
            total_char_count += 1
            char_code = ord(char)
            
            for start, end in japanese_ranges:
                if start <= char_code <= end:
                    japanese_char_count += 1
                    break
        
        if total_char_count == 0:
            return 0.0
            
        return japanese_char_count / total_char_count
    
    test_cases = [
        ("スイッチ", 1.0),  # All Japanese
        ("Switch", 0.0),  # All English
        ("スイッチ repair", 0.4),  # 4 Japanese chars, 6 English chars (4/10 = 0.4)
        ("アイフォン15", 0.7),  # 5 Japanese chars, 2 English chars (5/7 ≈ 0.71)
        ("", 0.0),  # Empty string
        ("   ", 0.0),  # Only whitespace
        ("123", 0.0),  # Numbers only
    ]
    
    for query, expected_ratio in test_cases:
        ratio = calculate_japanese_ratio(query)
        print(f"  Query: '{query}' -> Ratio: {ratio:.2f} (expected: {expected_ratio:.2f})")
        assert abs(ratio - expected_ratio) < 0.1, f"Expected {expected_ratio}, got {ratio}"
    
    print("✅ Japanese ratio calculation passed\n")


def test_mixed_language_detection():
    """Test mixed language query detection"""
    print("🧪 Testing mixed language detection...")
    
    def is_japanese_query(query):
        """Check if query contains Japanese characters"""
        if not query:
            return False
            
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FAF),  # CJK Unified Ideographs (Kanji)
            (0xFF66, 0xFF9D),  # Half-width Katakana
        ]
        
        for char in query:
            char_code = ord(char)
            for start, end in japanese_ranges:
                if start <= char_code <= end:
                    return True
        return False
    
    def is_japanese_character(char):
        """Check if a single character is Japanese"""
        char_code = ord(char)
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FAF),  # CJK Unified Ideographs (Kanji)
            (0xFF66, 0xFF9D),  # Half-width Katakana
        ]
        
        for start, end in japanese_ranges:
            if start <= char_code <= end:
                return True
        return False
    
    def is_mixed_language_query(query):
        """Check if query contains both Japanese and non-Japanese characters"""
        if not query:
            return False
            
        has_japanese = is_japanese_query(query)
        if not has_japanese:
            return False
            
        # Check for non-Japanese alphanumeric characters
        has_non_japanese = False
        for char in query:
            if char.isalnum() and not is_japanese_character(char):
                has_non_japanese = True
                break
                
        return has_japanese and has_non_japanese
    
    mixed_queries = [
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
    
    for query in mixed_queries:
        result = is_mixed_language_query(query)
        print(f"  Mixed query '{query}' -> {result}")
        assert result, f"'{query}' should be detected as mixed language"
        
    for query in single_language_queries:
        result = is_mixed_language_query(query)
        print(f"  Single language query '{query}' -> {result}")
        assert not result, f"'{query}' should not be detected as mixed language"
    
    print("✅ Mixed language detection passed\n")


def test_confidence_score_logic():
    """Test confidence scoring logic components"""
    print("🧪 Testing confidence score logic components...")
    
    # Test difficulty similarity matching
    def is_similar_difficulty(guide_difficulty, target_difficulty):
        """Check if two difficulty levels are similar"""
        difficulty_groups = [
            ["easy", "beginner"],
            ["moderate", "intermediate"],
            ["difficult", "expert", "very difficult"],
        ]
        
        guide_lower = guide_difficulty.lower()
        target_lower = target_difficulty.lower()
        
        for group in difficulty_groups:
            if guide_lower in group and target_lower in group:
                return True
        return False
    
    similarity_tests = [
        (["easy", "beginner"], True),
        (["moderate", "intermediate"], True),
        (["difficult", "expert"], True),
        (["easy", "difficult"], False),
        (["beginner", "expert"], False),
    ]
    
    for difficulties, should_be_similar in similarity_tests:
        result = is_similar_difficulty(difficulties[0], difficulties[1])
        print(f"  Difficulty '{difficulties[0]}' vs '{difficulties[1]}' -> similar: {result}")
        assert result == should_be_similar, f"Expected {should_be_similar}, got {result}"
    
    print("✅ Confidence score logic components passed\n")


def main():
    """Run all simple tests"""
    print("🚀 Starting simple Japanese confidence scoring tests\n")
    
    try:
        test_japanese_character_detection()
        test_japanese_ratio_calculation()
        test_mixed_language_detection()
        test_confidence_score_logic()
        
        print("🎯 All simple tests passed successfully!")
        print("✅ Core Japanese confidence scoring logic is working correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)