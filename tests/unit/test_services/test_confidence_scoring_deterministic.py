"""
Test suite for deterministic confidence scoring in RepairGuideService

This module tests the fixed confidence scoring system to ensure
deterministic and consistent results across multiple runs.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.clients.ifixit_client import Guide
from src.services.repair_guide_service import (
    RepairGuideService,
    SearchFilters,
)


class TestDeterministicConfidenceScoring:
    """Test deterministic confidence scoring behavior"""

    def setup_method(self):
        """Set up test environment before each test"""
        with patch('src.services.repair_guide_service.IFixitClient'), \
             patch('src.services.repair_guide_service.OfflineRepairDatabase'), \
             patch('src.services.repair_guide_service.CacheManager'), \
             patch('src.services.repair_guide_service.RateLimiter'):
            
            self.service = RepairGuideService(
                ifixit_api_key="test_key",
                enable_japanese_support=True
            )

    def create_test_guide(self, **kwargs):
        """Create a test guide with consistent default values"""
        defaults = {
            'guideid': 1,
            'title': 'Nintendo Switch Screen Repair',
            'device': 'Nintendo Switch',
            'category': 'Screen Repair',
            'subject': 'Screen',
            'difficulty': 'Moderate',
            'url': 'http://example.com/guide/1',
            'image_url': 'http://example.com/image1.jpg',
            'tools': ['Phillips Screwdriver'],
            'parts': ['Screen Assembly'],
            'type_': 'Repair'
        }
        defaults.update(kwargs)
        return Guide(**defaults)

    def test_confidence_scoring_deterministic_english(self):
        """Test that English queries produce deterministic confidence scores"""
        guide = self.create_test_guide()
        query = "Nintendo Switch screen repair"
        filters = SearchFilters()

        # Run scoring multiple times
        scores = []
        for _ in range(10):
            score = self.service._calculate_confidence_score(guide, query, filters)
            scores.append(score)

        # All scores should be identical
        assert len(set(scores)) == 1, f"Confidence scores not deterministic: {scores}"
        assert all(0.0 <= score <= 1.0 for score in scores), "Scores outside valid range"
        
        # Should get high confidence for exact match
        assert scores[0] > 0.7, f"Expected high confidence score, got {scores[0]}"

    def test_confidence_scoring_deterministic_japanese(self):
        """Test that Japanese queries produce deterministic confidence scores"""
        guide = self.create_test_guide()
        query = "スイッチ 画面修理"
        filters = SearchFilters()

        # Mock Japanese mapper methods to return consistent values
        with patch.object(self.service, '_is_japanese_query', return_value=True), \
             patch.object(self.service, '_calculate_japanese_ratio', return_value=0.8), \
             patch.object(self.service, '_assess_japanese_mapping_quality', return_value=0.9), \
             patch.object(self.service, '_evaluate_fuzzy_matching_confidence', return_value=0.85), \
             patch.object(self.service, '_analyze_device_mapping_quality', 
                         return_value={'direct_mappings': 1, 'fuzzy_mappings': 0, 'total_device_terms': 1, 'unmapped_terms': 0}), \
             patch.object(self.service, '_is_mixed_language_query', return_value=False):

            # Run scoring multiple times
            scores = []
            for _ in range(10):
                score = self.service._calculate_confidence_score(guide, query, filters)
                scores.append(score)

            # All scores should be identical
            assert len(set(scores)) == 1, f"Japanese confidence scores not deterministic: {scores}"
            assert all(0.0 <= score <= 1.0 for score in scores), "Scores outside valid range"

    def test_confidence_scoring_with_filters_deterministic(self):
        """Test deterministic scoring with various filters"""
        guide = self.create_test_guide(difficulty='Easy', category='Screen Repair')
        query = "Nintendo Switch screen"
        
        test_filters = [
            SearchFilters(),
            SearchFilters(device_type='Nintendo Switch'),
            SearchFilters(difficulty_level='Easy'),
            SearchFilters(category='Screen Repair'),
            SearchFilters(device_type='Nintendo Switch', difficulty_level='Easy', category='Screen Repair')
        ]

        for filters in test_filters:
            # Run each filter test multiple times
            scores = []
            for _ in range(5):
                score = self.service._calculate_confidence_score(guide, query, filters)
                scores.append(score)

            # All scores should be identical for each filter configuration
            assert len(set(scores)) == 1, f"Scores not deterministic for filters {filters}: {scores}"
            assert all(0.0 <= score <= 1.0 for score in scores), "Scores outside valid range"

    def test_confidence_scoring_edge_cases_deterministic(self):
        """Test deterministic scoring with edge cases"""
        edge_cases = [
            # (guide_kwargs, query, expected_min_score)
            ({}, "", 0.4),  # Empty query
            ({'title': '', 'device': '', 'category': ''}, "test query", 0.4),  # Empty guide fields
            ({'difficulty': None}, "test", 0.4),  # None difficulty
            ({'tools': None, 'parts': None, 'image_url': None}, "test", 0.4),  # None optional fields
        ]

        for guide_kwargs, query, expected_min in edge_cases:
            guide = self.create_test_guide(**guide_kwargs)
            filters = SearchFilters()

            # Run multiple times to check determinism
            scores = []
            for _ in range(5):
                score = self.service._calculate_confidence_score(guide, query, filters)
                scores.append(score)

            # All scores should be identical
            assert len(set(scores)) == 1, f"Edge case not deterministic: {guide_kwargs}, {query}: {scores}"
            assert all(0.0 <= score <= 1.0 for score in scores), "Scores outside valid range"
            assert all(score >= expected_min for score in scores), f"Score below expected minimum {expected_min}: {scores}"

    def test_confidence_scoring_japanese_filters_deterministic(self):
        """Test deterministic scoring with Japanese filters"""
        guide = self.create_test_guide(difficulty='Easy', category='Screen Repair')
        query = "スイッチ修理"
        
        japanese_filters = SearchFilters(
            device_type="スイッチ",
            difficulty_level="簡単",  # "easy" in Japanese
            category="画面修理"  # "screen repair" in Japanese
        )

        # Mock filter normalization to return consistent values
        with patch.object(japanese_filters, 'normalize_japanese_difficulty', return_value='easy'), \
             patch.object(japanese_filters, 'normalize_japanese_category', return_value='screen repair'), \
             patch.object(self.service, '_is_japanese_query', return_value=True), \
             patch.object(self.service, '_calculate_japanese_ratio', return_value=1.0), \
             patch.object(self.service, '_assess_japanese_mapping_quality', return_value=0.95), \
             patch.object(self.service, '_evaluate_fuzzy_matching_confidence', return_value=0.9), \
             patch.object(self.service, '_analyze_device_mapping_quality', 
                         return_value={'direct_mappings': 1, 'fuzzy_mappings': 0, 'total_device_terms': 1, 'unmapped_terms': 0}):

            # Run scoring multiple times
            scores = []
            for _ in range(10):
                score = self.service._calculate_confidence_score(guide, query, japanese_filters)
                scores.append(score)

            # All scores should be identical
            assert len(set(scores)) == 1, f"Japanese filter scores not deterministic: {scores}"
            assert all(0.0 <= score <= 1.0 for score in scores), "Scores outside valid range"

    def test_confidence_scoring_with_null_handling(self):
        """Test that null/None values are handled deterministically"""
        guide = self.create_test_guide()
        
        null_cases = [
            (None, SearchFilters()),
            ("", SearchFilters()),
            ("test query", SearchFilters(device_type=None)),
            ("test query", SearchFilters(difficulty_level=None)),
            ("test query", SearchFilters(category=None)),
        ]

        for query, filters in null_cases:
            # Run multiple times to check determinism
            scores = []
            for _ in range(5):
                score = self.service._calculate_confidence_score(guide, query, filters)
                scores.append(score)

            # All scores should be identical and valid
            assert len(set(scores)) == 1, f"Null handling not deterministic: {query}, {filters}: {scores}"
            assert all(0.0 <= score <= 1.0 for score in scores), "Scores outside valid range"

    def test_confidence_scoring_performance_consistency(self):
        """Test that scoring performance is consistent"""
        import time
        
        guide = self.create_test_guide()
        query = "Nintendo Switch screen repair test query"
        filters = SearchFilters(device_type="Nintendo Switch", difficulty_level="Moderate")

        # Measure execution times
        times = []
        scores = []
        
        for _ in range(20):
            start_time = time.time()
            score = self.service._calculate_confidence_score(guide, query, filters)
            end_time = time.time()
            
            times.append(end_time - start_time)
            scores.append(score)

        # All scores should be identical
        assert len(set(scores)) == 1, f"Performance test scores not deterministic: {set(scores)}"
        
        # Execution times should be reasonable (< 10ms each)
        avg_time = sum(times) / len(times)
        assert avg_time < 0.01, f"Confidence scoring too slow: {avg_time:.4f}s average"

    def test_confidence_scoring_with_mixed_language_deterministic(self):
        """Test deterministic scoring with mixed language queries"""
        guide = self.create_test_guide()
        mixed_queries = [
            "スイッチ screen repair",
            "Nintendo スイッチ 修理",
            "iPhone バッテリー replacement",
            "PlayStation controller 修理",
        ]

        for query in mixed_queries:
            with patch.object(self.service, '_is_japanese_query', return_value=True), \
                 patch.object(self.service, '_is_mixed_language_query', return_value=True), \
                 patch.object(self.service, '_calculate_japanese_ratio', return_value=0.5), \
                 patch.object(self.service, '_assess_japanese_mapping_quality', return_value=0.8):

                # Run multiple times to check determinism
                scores = []
                for _ in range(5):
                    score = self.service._calculate_confidence_score(guide, query, SearchFilters())
                    scores.append(score)

                # All scores should be identical
                assert len(set(scores)) == 1, f"Mixed language scoring not deterministic for '{query}': {scores}"
                assert all(0.0 <= score <= 1.0 for score in scores), "Scores outside valid range"

    def test_confidence_scoring_bounds_enforcement(self):
        """Test that confidence scores are always within valid bounds"""
        # Create extreme cases that might push scores outside bounds
        extreme_cases = [
            # Guide with many quality indicators
            self.create_test_guide(
                title="Nintendo Switch Complete Ultimate Screen Repair Guide",
                tools=["Tool1", "Tool2", "Tool3", "Tool4", "Tool5"],
                parts=["Part1", "Part2", "Part3"],
                image_url="http://example.com/image.jpg"
            ),
            # Guide with minimal information
            self.create_test_guide(
                title="",
                device="",
                category="",
                tools=[],
                parts=[],
                image_url=None
            ),
        ]

        queries = [
            "Nintendo Switch screen repair guide ultimate complete",  # High match
            "completely unrelated query about cars",  # Low match
            "",  # Empty query
        ]

        for guide in extreme_cases:
            for query in queries:
                filters = SearchFilters()
                
                # Run multiple times
                scores = []
                for _ in range(5):
                    score = self.service._calculate_confidence_score(guide, query, filters)
                    scores.append(score)

                # All scores should be identical and within bounds
                assert len(set(scores)) == 1, f"Extreme case not deterministic: {scores}"
                assert all(0.0 <= score <= 1.0 for score in scores), f"Scores outside bounds: {scores}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])