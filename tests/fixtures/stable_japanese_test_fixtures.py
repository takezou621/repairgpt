"""
Stable test fixtures for Japanese search functionality

This module provides deterministic test fixtures that ensure consistent
results across test runs, addressing the confidence scoring stability issues.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, List, Any

from src.clients.ifixit_client import Guide
from src.services.repair_guide_service import RepairGuideService, SearchFilters
from src.utils.japanese_device_mapper import JapaneseDeviceMapper


@pytest.fixture
def stable_japanese_mapper():
    """Provide a stable Japanese device mapper with consistent behavior"""
    mapper = Mock(spec=JapaneseDeviceMapper)
    
    # Consistent device mappings
    def stable_map_device_name(device_name):
        mappings = {
            "スイッチ": "Nintendo Switch",
            "すいっち": "Nintendo Switch",
            "switch": "Nintendo Switch",
            "アイフォン": "iPhone",
            "あいふぉん": "iPhone",
            "iphone": "iPhone",
            "プレステ": "PlayStation",
            "プレステ5": "PlayStation 5",
            "ps5": "PlayStation 5",
        }
        return mappings.get(device_name.lower(), device_name)
    
    # Consistent fuzzy matching
    def stable_find_best_match(device_name):
        device_name_lower = device_name.lower()
        if "スイッ" in device_name_lower or "swit" in device_name_lower:
            return ("Nintendo Switch", 0.85)
        elif "アイフォ" in device_name_lower or "iphon" in device_name_lower:
            return ("iPhone", 0.85)
        elif "プレス" in device_name_lower or "play" in device_name_lower:
            return ("PlayStation", 0.85)
        return (device_name, 0.0)
    
    mapper.map_device_name.side_effect = stable_map_device_name
    mapper.find_best_match.side_effect = stable_find_best_match
    
    return mapper


@pytest.fixture
def stable_search_filters():
    """Provide SearchFilters with stable Japanese normalization"""
    filters = SearchFilters()
    
    # Mock normalize methods to return consistent results
    def stable_normalize_difficulty(difficulty):
        mappings = {
            "簡単": "easy",
            "初心者": "beginner",
            "中級": "moderate",
            "上級": "expert",
            "難しい": "difficult"
        }
        return mappings.get(difficulty, difficulty)
    
    def stable_normalize_category(category):
        mappings = {
            "画面修理": "screen repair",
            "バッテリー交換": "battery replacement",
            "コントローラー修理": "controller repair",
            "充電ポート": "charging port repair"
        }
        return mappings.get(category, category)
    
    filters.normalize_japanese_difficulty = Mock(side_effect=stable_normalize_difficulty)
    filters.normalize_japanese_category = Mock(side_effect=stable_normalize_category)
    
    return filters


@pytest.fixture
def stable_test_guides():
    """Provide consistent test guide data"""
    return [
        Guide(
            guideid=1,
            title="Nintendo Switch Joy-Con Analog Stick Replacement",
            device="Nintendo Switch",
            category="Joy-Con Repair",
            summary="Analog Stick",
            difficulty="Moderate",
            url="https://www.ifixit.com/Guide/Nintendo+Switch+Joy-Con+Analog+Stick+Replacement/113182",
            image_url="https://d3nevzfk7ii3be.cloudfront.net/igi/tQoUdWAZpOQnyiuI.medium",
            tools=["Phillips #00 Screwdriver", "Plastic Opening Tools", "Tweezers"],
            parts=["Joy-Con Analog Stick"],
            time_required="60-90 minutes"
        ),
        Guide(
            guideid=2,
            title="Nintendo Switch Battery Replacement",
            device="Nintendo Switch",
            category="Battery Replacement",
            summary="Battery",
            difficulty="Easy",
            url="https://www.ifixit.com/Guide/Nintendo+Switch+Battery+Replacement/113186",
            image_url="https://d3nevzfk7ii3be.cloudfront.net/igi/example3.medium",
            tools=["Phillips #00 Screwdriver", "Plastic Opening Tools"],
            parts=["Switch Battery"],
            time_required="45-60 minutes"
        ),
        Guide(
            guideid=3,
            title="iPhone 15 Screen Replacement",
            device="iPhone 15",
            category="Screen Repair",
            summary="Display",
            difficulty="Moderate",
            url="https://www.ifixit.com/Guide/iPhone+15+Screen+Replacement/example",
            image_url="https://d3nevzfk7ii3be.cloudfront.net/igi/example4.medium",
            tools=["Pentalobe Screwdriver", "Suction Cup", "Heat Gun"],
            parts=["iPhone 15 Screen"],
            time_required="45-60 minutes"
        )
    ]


@pytest.fixture
def stable_repair_guide_service(stable_japanese_mapper):
    """Provide RepairGuideService with stable, mocked dependencies"""
    
    with patch('src.services.repair_guide_service.IFixitClient'), \
         patch('src.services.repair_guide_service.CacheManager'), \
         patch('src.services.repair_guide_service.RateLimiter'), \
         patch('src.services.repair_guide_service.OfflineRepairDatabase'), \
         patch('src.services.repair_guide_service.get_mapper', return_value=stable_japanese_mapper):
        
        service = RepairGuideService(
            ifixit_api_key="test_key",
            enable_japanese_support=True,
            enable_offline_fallback=True
        )
        
        # Replace the mapper with our stable one
        service.japanese_mapper = stable_japanese_mapper
        
        # Mock rate limiter and cache to avoid external dependencies
        service.rate_limiter.can_make_request.return_value = True
        service.rate_limiter.record_request.return_value = None
        service.cache_manager.get.return_value = None
        service.cache_manager.set.return_value = None
        
        return service


@pytest.fixture
def deterministic_confidence_scoring():
    """Patch confidence scoring to be deterministic"""
    
    def stable_calculate_confidence_score(self, guide, query, filters):
        """Deterministic confidence scoring for testing"""
        score = 0.5  # Base score
        
        query_lower = query.lower()
        title_lower = guide.title.lower()
        device_lower = guide.device.lower()
        
        # Simple, predictable scoring logic
        if query_lower in title_lower:
            score += 0.3
        elif any(word in title_lower for word in query_lower.split()):
            score += 0.2
            
        if guide.device.lower() in query_lower:
            score += 0.2
            
        if hasattr(filters, 'difficulty_level') and filters.difficulty_level:
            if guide.difficulty.lower() == filters.difficulty_level.lower():
                score += 0.1
                
        # Ensure score stays within bounds
        return min(max(score, 0.0), 1.0)
    
    return patch.object(
        RepairGuideService, 
        '_calculate_confidence_score', 
        stable_calculate_confidence_score
    )


class StableMockData:
    """Class containing stable mock data for tests"""
    
    JAPANESE_QUERIES = [
        "スイッチ修理",
        "アイフォン画面",
        "プレステコントローラー",
        "ノートパソコンキーボード"
    ]
    
    EXPECTED_MAPPINGS = {
        "スイッチ": "Nintendo Switch",
        "アイフォン": "iPhone", 
        "プレステ": "PlayStation",
        "ノートパソコン": "Laptop"
    }
    
    CONFIDENCE_SCORE_RANGES = {
        "exact_match": (0.8, 1.0),
        "good_match": (0.6, 0.8),
        "fair_match": (0.4, 0.6),
        "poor_match": (0.0, 0.4)
    }


@pytest.fixture
def stable_mock_data():
    """Provide stable mock data"""
    return StableMockData()