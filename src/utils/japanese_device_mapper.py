"""
Japanese Device Name Mapper for RepairGPT

This module provides mapping functionality to convert Japanese device names
(including katakana, hiragana, kanji, and common abbreviations) to their
corresponding English device names for the RepairGPT system.

Features:
- Comprehensive device mapping dictionary
- Support for multiple Japanese writing systems
- Common abbreviations and colloquial terms
- Case-insensitive matching
- Fuzzy matching capabilities
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from difflib import SequenceMatcher


class JapaneseDeviceMapper:
    """
    Japanese device name mapper for RepairGPT.

    This class handles the mapping of Japanese device names to their English
    equivalents, supporting various writing systems and common abbreviations.
    """

    # Core device mapping dictionary
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

    # Additional aliases and variations
    DEVICE_ALIASES: Dict[str, List[str]] = {
        "Nintendo Switch": ["switch lite", "スイッチライト", "すいっちらいと", "ライト"],
        "iPhone": [
            "iphone 15",
            "iphone 14",
            "iphone 13",
            "iphone 12",
            "iphone 11",
            "アイフォン15",
            "アイフォン14",
            "アイフォン13",
            "アイフォン12",
            "アイフォン11",
        ],
        "PlayStation 5": ["ps5 pro", "プレステ5プロ", "ps5プロ"],
        "Xbox": ["xbox series x", "xbox series s", "エックスボックスシリーズ"],
        "Laptop": [
            "thinkpad",
            "シンクパッド",
            "lenovo",
            "レノボ",
            "dell",
            "デル",
            "hp",
            "エイチピー",
            "asus",
            "エイスース",
        ],
    }

    def __init__(self):
        """Initialize the Japanese device mapper."""
        self._normalized_mappings = self._create_normalized_mappings()
        self._device_keywords = self._extract_device_keywords()

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
        Normalize text for consistent matching.

        Args:
            text: Input text to normalize

        Returns:
            Normalized text (lowercase, no spaces, no special characters)
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove spaces and common punctuation
        text = re.sub(r"[\s\-_\.,!?()（）]", "", text)

        # Remove common prefixes/suffixes that might interfere
        text = re.sub(r"^(the|a|an)", "", text)

        return text

    def map_device_name(self, japanese_name: str) -> Optional[str]:
        """
        Map a Japanese device name to its English equivalent.

        Args:
            japanese_name: Japanese device name to map

        Returns:
            English device name if found, None otherwise
        """
        if not japanese_name or not isinstance(japanese_name, str):
            return None

        normalized = self._normalize_text(japanese_name)

        # Direct mapping lookup
        if normalized in self._normalized_mappings:
            return self._normalized_mappings[normalized]

        return None

    def find_best_match(self, japanese_name: str, threshold: float = 0.6) -> Optional[Tuple[str, float]]:
        """
        Find the best matching device name using fuzzy matching.

        Args:
            japanese_name: Japanese device name to match
            threshold: Minimum similarity threshold (0.0 to 1.0)

        Returns:
            Tuple of (matched_device_name, similarity_score) or None
        """
        if not japanese_name or not isinstance(japanese_name, str):
            return None

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
        Get multiple possible matches for a Japanese device name.

        Args:
            japanese_name: Japanese device name to match
            max_results: Maximum number of results to return

        Returns:
            List of tuples (device_name, similarity_score) sorted by score
        """
        if not japanese_name or not isinstance(japanese_name, str):
            return []

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
        Check if the given text appears to be a device name.

        Args:
            text: Text to check

        Returns:
            True if text appears to be a device name, False otherwise
        """
        if not text or not isinstance(text, str):
            return False

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
        variations = []

        # Find direct mappings
        for japanese, english in self.DEVICE_MAPPINGS.items():
            if english == english_device_name:
                variations.append(japanese)

        # Find aliases
        if english_device_name in self.DEVICE_ALIASES:
            variations.extend(self.DEVICE_ALIASES[english_device_name])

        return variations


# Convenience functions for common use cases
_mapper_instance: Optional[JapaneseDeviceMapper] = None


def get_mapper() -> JapaneseDeviceMapper:
    """
    Get singleton instance of JapaneseDeviceMapper.

    Returns:
        JapaneseDeviceMapper instance
    """
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = JapaneseDeviceMapper()
    return _mapper_instance


def map_japanese_device(japanese_name: str) -> Optional[str]:
    """
    Map Japanese device name to English (convenience function).

    Args:
        japanese_name: Japanese device name

    Returns:
        English device name or None
    """
    return get_mapper().map_device_name(japanese_name)


def find_device_match(japanese_name: str, threshold: float = 0.6) -> Optional[str]:
    """
    Find best matching device name (convenience function).

    Args:
        japanese_name: Japanese device name
        threshold: Minimum similarity threshold

    Returns:
        Best matching English device name or None
    """
    result = get_mapper().find_best_match(japanese_name, threshold)
    return result[0] if result else None


def is_likely_device(text: str) -> bool:
    """
    Check if text is likely a device name (convenience function).

    Args:
        text: Text to check

    Returns:
        True if likely a device name
    """
    return get_mapper().is_device_name(text)


# Example usage and testing
if __name__ == "__main__":
    # Test the mapper functionality
    print("Testing Japanese Device Mapper...")

    mapper = JapaneseDeviceMapper()

    # Test cases
    test_cases = [
        "スイッチ",
        "アイフォン",
        "プレステ5",
        "ノートパソコン",
        "すまほ",
        "えあぽっず",
        "ゲーム機",
        "invalid_device",
        "スイッチライト",
        "アイフォン13",
    ]

    print("\n=== Direct Mapping Tests ===")
    for test_case in test_cases:
        result = mapper.map_device_name(test_case)
        print(f"'{test_case}' -> {result}")

    print("\n=== Fuzzy Matching Tests ===")
    fuzzy_cases = ["すいち", "あいふお", "ぷれすて", "のーと"]
    for test_case in fuzzy_cases:
        result = mapper.find_best_match(test_case)
        if result:
            print(f"'{test_case}' -> {result[0]} (score: {result[1]:.3f})")
        else:
            print(f"'{test_case}' -> No match found")

    print("\n=== Device Detection Tests ===")
    detection_cases = ["これはスイッチの問題です", "プレステ", "random text", "アイフォンが動かない"]
    for test_case in detection_cases:
        is_device = mapper.is_device_name(test_case)
        print(f"'{test_case}' -> Is device: {is_device}")

    print("\n=== Supported Devices ===")
    devices = mapper.get_supported_devices()
    print(f"Total supported devices: {len(devices)}")
    for device in devices[:10]:  # Show first 10
        print(f"  - {device}")
    if len(devices) > 10:
        print(f"  ... and {len(devices) - 10} more")

    print("\nTesting completed successfully!")
