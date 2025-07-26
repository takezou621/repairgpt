"""
Japanese Device Name Mapper for RepairGPT - Improved Version with QA Fixes

This module provides mapping functionality to convert Japanese device names
(including katakana, hiragana, kanji, and common abbreviations) to their
corresponding English device names for the RepairGPT system.

Improvements based on QA analysis:
- Enhanced text normalization with better special character handling
- Memory optimization with class-level shared data structures
- Improved input validation and security measures
- Better error handling and performance optimizations

Features:
- Comprehensive device mapping dictionary
- Support for multiple Japanese writing systems
- Common abbreviations and colloquial terms
- Case-insensitive matching
- Fuzzy matching capabilities
- Memory-efficient shared data structures
- Security input validation
- Performance optimizations
"""

import re
import threading
from typing import Dict, List, Optional, Set, Tuple
from difflib import SequenceMatcher


class JapaneseDeviceMapper:
    """
    Japanese device name mapper for RepairGPT with enhanced performance and security.
    
    This class handles the mapping of Japanese device names to their English
    equivalents, supporting various writing systems and common abbreviations.
    
    Improvements:
    - Memory optimization with shared data structures
    - Enhanced input validation and security
    - Better text normalization
    - Performance monitoring capabilities
    """

    # Core device mapping dictionary (unchanged from original)
    DEVICE_MAPPINGS: Dict[str, str] = {
        # Nintendo Switch variations
        "スイッチ": "Nintendo Switch",
        "すいっち": "Nintendo Switch", 
        "ニンテンドースイッチ": "Nintendo Switch",
        "ニンテンドーswitch": "Nintendo Switch",
        "任天堂スイッチ": "Nintendo Switch",
        "任天堂switch": "Nintendo Switch",
        "switch": "Nintendo Switch",
        "ns": "Nintendo Switch",
        "ニンテンドー": "Nintendo Switch",
        "にんてんどー": "Nintendo Switch",
        "任天堂": "Nintendo Switch",
        
        # iPhone variations
        "アイフォン": "iPhone",
        "あいふォん": "iPhone",
        "アイフォーン": "iPhone",
        "iphone": "iPhone",
        "iphon": "iPhone",
        "アイホン": "iPhone",
        "あいほん": "iPhone",
        "愛phone": "iPhone",
        
        # PlayStation variations
        "プレイステーション": "PlayStation",
        "プレステ": "PlayStation",
        "ぷれすて": "PlayStation",
        "playstation": "PlayStation",
        "ps": "PlayStation",
        "ピーエス": "PlayStation",
        "プレステーション": "PlayStation",
        
        # PlayStation 5 specific
        "プレイステーション5": "PlayStation 5",
        "プレステ5": "PlayStation 5",
        "ps5": "PlayStation 5",
        "ピーエス5": "PlayStation 5",
        "プレイステーション５": "PlayStation 5",
        "プレステ５": "PlayStation 5",
        "ピーエス５": "PlayStation 5",
        
        # PlayStation 4 specific
        "プレイステーション4": "PlayStation 4",
        "プレステ4": "PlayStation 4", 
        "ps4": "PlayStation 4",
        "ピーエス4": "PlayStation 4",
        "プレイステーション４": "PlayStation 4",
        "プレステ４": "PlayStation 4",
        "ピーエス４": "PlayStation 4",
        
        # Xbox variations
        "エックスボックス": "Xbox",
        "えっくすぼっくす": "Xbox",
        "xbox": "Xbox",
        "エクボ": "Xbox",
        "えくぼ": "Xbox",
        
        # Laptop variations
        "ラップトップ": "Laptop",
        "らっぷとっぷ": "Laptop",
        "laptop": "Laptop",
        "ノートパソコン": "Laptop",
        "ノートpc": "Laptop",
        "ノート": "Laptop",
        "のーと": "Laptop",
        "ノーパソ": "Laptop",
        "のーぱそ": "Laptop",
        
        # Desktop PC variations
        "デスクトップ": "Desktop PC",
        "でするとっぷ": "Desktop PC",
        "desktop": "Desktop PC",
        "パソコン": "Desktop PC",
        "ぱそこん": "Desktop PC",
        "pc": "Desktop PC",
        "ピーシー": "Desktop PC",
        "ぴーしー": "Desktop PC",
        "コンピューター": "Desktop PC",
        "こんぴゅーたー": "Desktop PC",
        
        # Smartphone variations (general)
        "スマートフォン": "Smartphone",
        "すまーとふぉん": "Smartphone",
        "smartphone": "Smartphone",
        "スマホ": "Smartphone",
        "すまほ": "Smartphone",
        "携帯": "Smartphone",
        "けいたい": "Smartphone",
        "携帯電話": "Smartphone",
        "けいたいでんわ": "Smartphone",
        
        # Android variations
        "アンドロイド": "Android",
        "あんどろいど": "Android",
        "android": "Android",
        "アンドロ": "Android",
        "あんどろ": "Android",
        
        # iPad variations
        "アイパッド": "iPad",
        "あいぱっど": "iPad",
        "ipad": "iPad",
        "アイパド": "iPad",
        "あいぱど": "iPad",
        
        # Tablet variations
        "タブレット": "Tablet",
        "たぶれっと": "Tablet",
        "tablet": "Tablet",
        "タブ": "Tablet",
        "たぶ": "Tablet",
        
        # MacBook variations
        "マックブック": "MacBook",
        "まっくぶっく": "MacBook",
        "macbook": "MacBook",
        "マック": "MacBook",
        "まっく": "MacBook",
        "mac": "MacBook",
        
        # Surface variations
        "サーフェス": "Surface",
        "さーふぇす": "Surface",
        "surface": "Surface",
        
        # Gaming console general
        "ゲーム機": "Gaming Console",
        "げーむき": "Gaming Console",
        "ゲーム": "Gaming Console",
        "げーむ": "Gaming Console",
        "ゲームコンソール": "Gaming Console",
        "げーむこんそーる": "Gaming Console",
        
        # Headphones variations
        "ヘッドフォン": "Headphones",
        "へっどふぉん": "Headphones",
        "headphones": "Headphones",
        "ヘッドホン": "Headphones",
        "へっどほん": "Headphones",
        "イヤホン": "Earphones",
        "いやほん": "Earphones",
        "earphones": "Earphones",
        
        # Smart Watch variations
        "スマートウォッチ": "Smart Watch",
        "すまーとうぉっち": "Smart Watch",
        "smartwatch": "Smart Watch",
        "スマウォ": "Smart Watch",
        "すまうぉ": "Smart Watch",
        "腕時計": "Smart Watch",
        "うでどけい": "Smart Watch",
        
        # Apple Watch specific
        "アップルウォッチ": "Apple Watch",
        "あっぷるうぉっち": "Apple Watch",
        "apple watch": "Apple Watch",
        "applewatch": "Apple Watch",
        
        # AirPods variations
        "エアポッズ": "AirPods",
        "えあぽっず": "AirPods",
        "airpods": "AirPods",
        "エアポ": "AirPods",
        "えあぽ": "AirPods",
        
        # TV variations
        "テレビ": "TV",
        "てれび": "TV",
        "tv": "TV",
        "ティーブイ": "TV",
        "てぃーぶい": "TV",
        "スマートテレビ": "Smart TV",
        "すまーとてれび": "Smart TV",
        "smart tv": "Smart TV",
        
        # Camera variations
        "カメラ": "Camera",
        "かめら": "Camera",
        "camera": "Camera",
        "デジカメ": "Digital Camera",
        "でじかめ": "Digital Camera",
        "デジタルカメラ": "Digital Camera",
        "でじたるかめら": "Digital Camera",
        
        # Router variations
        "ルーター": "Router",
        "るーたー": "Router",
        "router": "Router",
        "ルータ": "Router",
        "るーた": "Router",
        "無線ルーター": "Wireless Router",
        "むせんるーたー": "Wireless Router",
        
        # VR Headset variations
        "VRヘッドセット": "VR Headset",
        "vrへっどせっと": "VR Headset",
        "vr headset": "VR Headset",
        "バーチャルリアリティ": "VR Headset",
        "ばーちゃるりありてぃ": "VR Headset",
        "VR": "VR Headset",
        "vr": "VR Headset",
        "ブイアール": "VR Headset",
        "ぶいあーる": "VR Headset",
    }

    # Additional aliases and variations (unchanged from original)
    DEVICE_ALIASES: Dict[str, List[str]] = {
        "Nintendo Switch": ["switch lite", "スイッチライト", "すいっちらいと", "ライト"],
        "iPhone": ["iphone 15", "iphone 14", "iphone 13", "iphone 12", "iphone 11", 
                  "アイフォン15", "アイフォン14", "アイフォン13", "アイフォン12", "アイフォン11"],
        "PlayStation 5": ["ps5 pro", "プレステ5プロ", "ps5プロ"],
        "Xbox": ["xbox series x", "xbox series s", "エックスボックスシリーズ"],
        "Laptop": ["thinkpad", "シンクパッド", "lenovo", "レノボ", "dell", "デル", 
                  "hp", "エイチピー", "asus", "エイスース"],
    }

    # Class-level cache to share data across instances (Memory optimization)
    _shared_normalized_mappings: Optional[Dict[str, str]] = None
    _shared_device_keywords: Optional[Set[str]] = None
    _initialization_lock = threading.Lock()
    
    # Input validation constants
    MAX_INPUT_LENGTH = 1000  # Prevent DoS attacks
    MALICIOUS_PATTERNS = [
        r'<script',
        r'javascript:',
        r'\$\{.*\}',  # Template injection
        r'\.\.[\\/]',  # Path traversal
        r'\|\s*\w+',  # Command injection
        r';\s*\w+',   # Command injection
    ]

    # Use slots to reduce memory overhead
    __slots__ = ['_initialized']

    def __init__(self):
        """Initialize the Japanese device mapper with shared data structures."""
        self._initialized = True
        
        # Use class-level shared data structures (thread-safe initialization)
        if JapaneseDeviceMapper._shared_normalized_mappings is None:
            with JapaneseDeviceMapper._initialization_lock:
                # Double-check locking pattern
                if JapaneseDeviceMapper._shared_normalized_mappings is None:
                    JapaneseDeviceMapper._shared_normalized_mappings = self._create_normalized_mappings()
                    JapaneseDeviceMapper._shared_device_keywords = self._extract_device_keywords()

    @property
    def _normalized_mappings(self) -> Dict[str, str]:
        """Access shared normalized mappings."""
        return JapaneseDeviceMapper._shared_normalized_mappings

    @property
    def _device_keywords(self) -> Set[str]:
        """Access shared device keywords."""
        return JapaneseDeviceMapper._shared_device_keywords

    def _create_normalized_mappings(self) -> Dict[str, str]:
        """
        Create normalized mappings for case-insensitive matching.
        
        Returns:
            Dictionary with normalized keys and original values
        """
        normalized = {}
        
        # Add main mappings
        for japanese_name, english_name in self.DEVICE_MAPPINGS.items():
            normalized[self._normalize_text(japanese_name)] = english_name
            
        # Add aliases
        for device, aliases in self.DEVICE_ALIASES.items():
            for alias in aliases:
                normalized[self._normalize_text(alias)] = device
                
        return normalized

    def _extract_device_keywords(self) -> Set[str]:
        """
        Extract keywords from device names for fuzzy matching.
        
        Returns:
            Set of device keywords
        """
        keywords = set()
        
        for japanese_name in self.DEVICE_MAPPINGS.keys():
            # Add original name
            keywords.add(self._normalize_text(japanese_name))
            
            # Add substrings for partial matching
            normalized = self._normalize_text(japanese_name)
            if len(normalized) > 2:
                for i in range(len(normalized) - 1):
                    for j in range(i + 2, len(normalized) + 1):
                        substring = normalized[i:j]
                        if len(substring) >= 2:
                            keywords.add(substring)
                            
        return keywords

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent matching with improved special character handling.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text (lowercase, no spaces, no special characters)
        """
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Enhanced regex to handle more special characters and punctuation
        # Including common Japanese punctuation and symbols
        text = re.sub(r'[\s\-_\.,!?()（）\[\]{}【】「」『』〈〉《》〔〕\\/@#$%^&*+=|~`"\'；：、。！？]', '', text)
        
        # Remove common prefixes/suffixes that might interfere
        text = re.sub(r'^(the|a|an)', '', text)
        
        # Handle full-width to half-width conversion for better matching
        text = text.translate(str.maketrans(
            'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９',
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        ))
        
        return text

    def _validate_input(self, input_text: str) -> bool:
        """
        Validate input for security and safety.
        
        Args:
            input_text: Input text to validate
            
        Returns:
            True if input is safe, False otherwise
        """
        # Type check
        if not isinstance(input_text, str):
            return False
            
        # Length validation to prevent DoS attacks
        if len(input_text) > self.MAX_INPUT_LENGTH:
            return False
            
        # Check for malicious patterns
        input_lower = input_text.lower()
        for pattern in self.MALICIOUS_PATTERNS:
            if re.search(pattern, input_lower):
                return False
                
        return True

    def _sanitize_input(self, input_text: str) -> str:
        """
        Sanitize input by removing control characters.
        
        Args:
            input_text: Input text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove control characters
        return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', input_text)

    def map_device_name(self, japanese_name: str) -> Optional[str]:
        """
        Map a Japanese device name to its English equivalent with enhanced validation.
        
        Args:
            japanese_name: Japanese device name to map
            
        Returns:
            English device name if found, None otherwise
        """
        # Enhanced input validation
        if not japanese_name:
            return None
            
        if not self._validate_input(japanese_name):
            return None
            
        # Sanitize input
        japanese_name = self._sanitize_input(japanese_name)
        
        normalized = self._normalize_text(japanese_name)
        
        # Direct mapping lookup
        if normalized in self._normalized_mappings:
            return self._normalized_mappings[normalized]
            
        return None

    def find_best_match(self, japanese_name: str, threshold: float = 0.6) -> Optional[Tuple[str, float]]:
        """
        Find the best matching device name using fuzzy matching with enhanced validation.
        
        Args:
            japanese_name: Japanese device name to match
            threshold: Minimum similarity threshold (0.0 to 1.0)
            
        Returns:
            Tuple of (matched_device_name, similarity_score) or None
        """
        if not japanese_name or not self._validate_input(japanese_name):
            return None
            
        japanese_name = self._sanitize_input(japanese_name)
        normalized_input = self._normalize_text(japanese_name)
        best_match = None
        best_score = 0.0
        
        # Check against all normalized mappings
        for normalized_key, english_name in self._normalized_mappings.items():
            # Calculate similarity using SequenceMatcher
            similarity = SequenceMatcher(None, normalized_input, normalized_key).ratio()
            
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = english_name
                
        if best_match:
            return (best_match, best_score)
            
        return None

    def get_possible_matches(self, japanese_name: str, max_results: int = 5) -> List[Tuple[str, float]]:
        """
        Get multiple possible matches for a Japanese device name with enhanced validation.
        
        Args:
            japanese_name: Japanese device name to match
            max_results: Maximum number of results to return
            
        Returns:
            List of tuples (device_name, similarity_score) sorted by score
        """
        if not japanese_name or not self._validate_input(japanese_name):
            return []
            
        japanese_name = self._sanitize_input(japanese_name)
        normalized_input = self._normalize_text(japanese_name)
        matches = []
        
        # Check against all normalized mappings
        for normalized_key, english_name in self._normalized_mappings.items():
            similarity = SequenceMatcher(None, normalized_input, normalized_key).ratio()
            
            if similarity > 0.3:  # Lower threshold for multiple matches
                matches.append((english_name, similarity))
                
        # Sort by similarity score (descending) and remove duplicates
        matches = sorted(set(matches), key=lambda x: x[1], reverse=True)
        
        return matches[:max_results]

    def is_device_name(self, text: str) -> bool:
        """
        Check if the given text appears to be a device name with enhanced validation.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be a device name, False otherwise
        """
        if not text or not self._validate_input(text):
            return False
            
        text = self._sanitize_input(text)
        normalized = self._normalize_text(text)
        
        # Check direct mapping first (most reliable)
        if normalized in self._normalized_mappings:
            return True
            
        # Check if text contains significant device keywords (more precise matching)
        for keyword in self._device_keywords:
            if len(keyword) >= 3:  # Only check keywords of significant length
                if keyword == normalized:  # Exact match
                    return True
                elif len(normalized) >= 4 and keyword in normalized:  # Substring match for longer text
                    return True
                    
        return False

    def get_supported_devices(self) -> List[str]:
        """
        Get list of all supported English device names.
        
        Returns:
            Sorted list of unique English device names
        """
        devices = set(self.DEVICE_MAPPINGS.values())
        devices.update(self.DEVICE_ALIASES.keys())
        return sorted(list(devices))

    def get_japanese_variations(self, english_device_name: str) -> List[str]:
        """
        Get all Japanese variations for a given English device name.
        
        Args:
            english_device_name: English device name
            
        Returns:
            List of Japanese variations
        """
        if not english_device_name or not isinstance(english_device_name, str):
            return []
            
        variations = []
        
        # Find direct mappings
        for japanese, english in self.DEVICE_MAPPINGS.items():
            if english == english_device_name:
                variations.append(japanese)
                
        # Find aliases
        if english_device_name in self.DEVICE_ALIASES:
            variations.extend(self.DEVICE_ALIASES[english_device_name])
            
        return variations

    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the mapper.
        
        Returns:
            Dictionary with mapper statistics
        """
        return {
            'total_mappings': len(self.DEVICE_MAPPINGS),
            'total_aliases': sum(len(aliases) for aliases in self.DEVICE_ALIASES.values()),
            'normalized_mappings': len(self._normalized_mappings),
            'device_keywords': len(self._device_keywords),
            'supported_devices': len(self.get_supported_devices()),
        }


# Enhanced convenience functions with validation
_mapper_instance: Optional[JapaneseDeviceMapper] = None
_instance_lock = threading.Lock()


def get_mapper() -> JapaneseDeviceMapper:
    """
    Get thread-safe singleton instance of JapaneseDeviceMapper.
    
    Returns:
        JapaneseDeviceMapper instance
    """
    global _mapper_instance
    if _mapper_instance is None:
        with _instance_lock:
            if _mapper_instance is None:
                _mapper_instance = JapaneseDeviceMapper()
    return _mapper_instance


def map_japanese_device(japanese_name: str) -> Optional[str]:
    """
    Map Japanese device name to English (convenience function with validation).
    
    Args:
        japanese_name: Japanese device name
        
    Returns:
        English device name or None
    """
    if not japanese_name or not isinstance(japanese_name, str):
        return None
    return get_mapper().map_device_name(japanese_name)


def find_device_match(japanese_name: str, threshold: float = 0.6) -> Optional[str]:
    """
    Find best matching device name (convenience function with validation).
    
    Args:
        japanese_name: Japanese device name
        threshold: Minimum similarity threshold
        
    Returns:
        Best matching English device name or None
    """
    if not japanese_name or not isinstance(japanese_name, str):
        return None
    result = get_mapper().find_best_match(japanese_name, threshold)
    return result[0] if result else None


def is_likely_device(text: str) -> bool:
    """
    Check if text is likely a device name (convenience function with validation).
    
    Args:
        text: Text to check
        
    Returns:
        True if likely a device name
    """
    if not text or not isinstance(text, str):
        return False
    return get_mapper().is_device_name(text)


# Example usage and testing
if __name__ == "__main__":
    # Test the improved mapper functionality
    print("Testing Improved Japanese Device Mapper...")
    print("=========================================")
    
    mapper = JapaneseDeviceMapper()
    
    # Test cases including the fixes
    test_cases = [
        "スイッチ",
        "アイフォン",
        "プレステ5",
        "ノートパソコン",
        "すまほ",
        "えあぽっず",
        "ゲーム機",
        "スイッチ!@#",  # Fixed: should now work
        "iPhone!!!",    # Fixed: should now work
        "ＩＰＨＯＮＥ",  # Fixed: full-width characters
        "invalid_device",
        "スイッチライト",
        "アイフォン13",
    ]
    
    print("\n=== Direct Mapping Tests (Including Fixes) ===")
    for test_case in test_cases:
        result = mapper.map_device_name(test_case)
        status = "✅" if result else "❌"
        print(f"{status} '{test_case}' -> {result}")
        
    print("\n=== Security Tests ===")
    security_cases = [
        "<script>alert('xss')</script>",
        "javascript:alert('test')",
        "スイッチ" + "x" * 1000,  # Too long
        "valid input",
    ]
    for test_case in security_cases:
        result = mapper.map_device_name(test_case)
        status = "🛡️" if result is None and len(test_case) > 20 else "✅"
        print(f"{status} Security test: {result}")
        
    print("\n=== Performance Test ===")
    import time
    start_time = time.time()
    for i in range(1000):
        mapper.map_device_name("スイッチ")
    end_time = time.time()
    print(f"1000 operations in {end_time - start_time:.4f}s")
    
    print("\n=== Statistics ===")
    stats = mapper.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
        
    print("\n✅ Improved mapper testing completed successfully!")