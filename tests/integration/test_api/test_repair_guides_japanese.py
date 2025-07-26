"""
Integration tests for Repair Guide API with Japanese support
Tests Japanese search functionality, character encoding, and API responses
"""

import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

# Import the API models and app
from src.api.main import app
from src.api.models import (
    RepairGuideSearchRequest,
    RepairGuideSearchResponse,
    SearchLanguage,
    RepairGuideSearchFilters,
)
from src.services.repair_guide_service import RepairGuideResult, SearchFilters
from src.clients.ifixit_client import Guide


class TestJapaneseRepairGuideAPI:
    """Test suite for Japanese repair guide API functionality"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_guide(self):
        """Create mock repair guide"""
        return Guide(
            guideid=12345,
            title="Nintendo Switch Screen Replacement",
            device="Nintendo Switch",
            difficulty="Moderate",
            time_estimate="30-45 minutes",
            summary="Replace the cracked screen on your Nintendo Switch",
            tools=["Phillips screwdriver", "Spudger", "Tweezers"],
            parts=["Nintendo Switch LCD Screen"],
            category="Screen Repair",
            image_url="https://example.com/guide.jpg",
            steps=["Step 1: Power off device", "Step 2: Remove screws"],
        )

    @pytest.fixture
    def mock_repair_guide_result(self, mock_guide):
        """Create mock repair guide result"""
        from datetime import datetime
        
        return RepairGuideResult(
            guide=mock_guide,
            source="ifixit",
            confidence_score=0.95,
            last_updated=datetime.now(),
            difficulty_explanation="Moderate difficulty repair",
            estimated_cost="$50-$80",
            success_rate=0.85,
        )

    @pytest.mark.asyncio
    async def test_japanese_search_post_endpoint(self, client, mock_repair_guide_result):
        """Test Japanese search via POST endpoint"""
        with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
            # Setup mock service
            service_instance = MagicMock()
            service_instance.search_guides = AsyncMock(return_value=[mock_repair_guide_result])
            service_instance._is_japanese_query = MagicMock(return_value=True)
            service_instance._preprocess_japanese_query = MagicMock(return_value="Nintendo Switch screen repair")
            service_instance._assess_japanese_mapping_quality = MagicMock(return_value=0.95)
            service_instance.japanese_mapper = MagicMock()
            mock_service.return_value = service_instance

            # Test data with Japanese query
            test_request = {
                "query": "スイッチ 画面修理",
                "language": "ja",
                "filters": {
                    "difficulty_level": "初心者",
                    "category": "画面修理",
                    "device_type": "スイッチ"
                },
                "limit": 10
            }

            response = client.post("/api/repair-guides/search", json=test_request)

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "results" in data
            assert "metadata" in data
            assert len(data["results"]) == 1

            # Verify metadata
            metadata = data["metadata"]
            assert metadata["language_detected"] == "ja"
            assert metadata["query_processed"] == "Nintendo Switch screen repair"
            assert metadata["japanese_mapping_quality"] == 0.95
            assert metadata["total_found"] == 1

            # Verify guide data
            guide = data["results"][0]
            assert guide["title"] == "Nintendo Switch Screen Replacement"
            assert guide["confidence_score"] == 0.95
            assert guide["source"] == "ifixit"

    @pytest.mark.asyncio
    async def test_japanese_search_get_endpoint(self, client, mock_repair_guide_result):
        """Test Japanese search via GET endpoint with query parameters"""
        with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
            # Setup mock service
            service_instance = MagicMock()
            service_instance.search_guides = AsyncMock(return_value=[mock_repair_guide_result])
            service_instance._is_japanese_query = MagicMock(return_value=True)
            service_instance._preprocess_japanese_query = MagicMock(return_value="Nintendo Switch battery")
            service_instance._assess_japanese_mapping_quality = MagicMock(return_value=0.90)
            service_instance.japanese_mapper = MagicMock()
            mock_service.return_value = service_instance

            # Test Japanese query parameters
            response = client.get(
                "/api/repair-guides/search",
                params={
                    "query": "スイッチ バッテリー交換",
                    "language": "ja",
                    "device_type": "スイッチ",
                    "difficulty_level": "中級者",
                    "limit": 5
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response
            assert data["metadata"]["language_detected"] == "ja"
            assert data["metadata"]["query_processed"] == "Nintendo Switch battery"
            assert len(data["results"]) == 1

    def test_japanese_character_encoding(self, client):
        """Test proper handling of Japanese character encoding"""
        # Test various Japanese character sets
        japanese_queries = [
            "Nintendo Switch 画面修理",  # Kanji
            "ニンテンドー スイッチ",  # Katakana
            "すいっち はいせん",  # Hiragana
            "iPhone アイフォン 修理",  # Mixed scripts
        ]

        for query in japanese_queries:
            test_request = {
                "query": query,
                "language": "ja",
                "limit": 5
            }

            with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
                service_instance = MagicMock()
                service_instance.search_guides = AsyncMock(return_value=[])
                service_instance._is_japanese_query = MagicMock(return_value=True)
                service_instance._preprocess_japanese_query = MagicMock(return_value=query)
                service_instance._assess_japanese_mapping_quality = MagicMock(return_value=1.0)
                service_instance.japanese_mapper = MagicMock()
                mock_service.return_value = service_instance

                response = client.post("/api/repair-guides/search", json=test_request)
                
                # Should not fail with encoding errors
                assert response.status_code == 200
                
                # Verify UTF-8 encoding is preserved
                assert response.headers.get("content-type") == "application/json"

    def test_japanese_difficulty_mapping(self, client, mock_repair_guide_result):
        """Test Japanese difficulty level mapping"""
        japanese_difficulties = [
            ("初心者", "beginner"),
            ("中級者", "intermediate"),
            ("上級者", "expert"),
            ("簡単", "easy"),
            ("難しい", "difficult"),
        ]

        for japanese_diff, expected_english in japanese_difficulties:
            test_request = {
                "query": "修理ガイド",
                "language": "ja",
                "filters": {
                    "difficulty_level": japanese_diff
                },
                "limit": 5
            }

            with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
                service_instance = MagicMock()
                service_instance.search_guides = AsyncMock(return_value=[mock_repair_guide_result])
                service_instance._is_japanese_query = MagicMock(return_value=True)
                service_instance._preprocess_japanese_query = MagicMock(return_value="repair guide")
                service_instance._assess_japanese_mapping_quality = MagicMock(return_value=1.0)
                service_instance.japanese_mapper = MagicMock()
                mock_service.return_value = service_instance

                response = client.post("/api/repair-guides/search", json=test_request)
                assert response.status_code == 200

                # Verify the service was called with correct filters
                call_args = service_instance.search_guides.call_args
                filters = call_args[1]['filters']
                assert filters.difficulty_level == japanese_diff

    def test_japanese_category_mapping(self, client, mock_repair_guide_result):
        """Test Japanese category mapping"""
        japanese_categories = [
            ("画面修理", "screen repair"),
            ("バッテリー交換", "battery replacement"),
            ("基板修理", "motherboard repair"),
            ("充電器修理", "charger repair"),
        ]

        for japanese_cat, expected_english in japanese_categories:
            test_request = {
                "query": "修理",
                "language": "ja",
                "filters": {
                    "category": japanese_cat
                },
                "limit": 5
            }

            with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
                service_instance = MagicMock()
                service_instance.search_guides = AsyncMock(return_value=[mock_repair_guide_result])
                service_instance._is_japanese_query = MagicMock(return_value=True)
                service_instance._preprocess_japanese_query = MagicMock(return_value="repair")
                service_instance._assess_japanese_mapping_quality = MagicMock(return_value=1.0)
                service_instance.japanese_mapper = MagicMock()
                mock_service.return_value = service_instance

                response = client.post("/api/repair-guides/search", json=test_request)
                assert response.status_code == 200

    def test_mixed_language_query(self, client, mock_repair_guide_result):
        """Test mixed Japanese-English queries"""
        mixed_queries = [
            "iPhone 画面修理",
            "Nintendo Switch バッテリー",
            "MacBook キーボード 修理",
        ]

        for query in mixed_queries:
            test_request = {
                "query": query,
                "language": "ja",
                "limit": 5
            }

            with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
                service_instance = MagicMock()
                service_instance.search_guides = AsyncMock(return_value=[mock_repair_guide_result])
                service_instance._is_japanese_query = MagicMock(return_value=True)
                service_instance._preprocess_japanese_query = MagicMock(return_value=query)
                service_instance._assess_japanese_mapping_quality = MagicMock(return_value=0.8)
                service_instance.japanese_mapper = MagicMock()
                mock_service.return_value = service_instance

                response = client.post("/api/repair-guides/search", json=test_request)
                assert response.status_code == 200

    def test_japanese_device_endpoint(self, client, mock_repair_guide_result):
        """Test device-specific endpoint with Japanese device names"""
        japanese_devices = ["スイッチ", "アイフォン", "マックブック"]

        for device in japanese_devices:
            with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
                service_instance = MagicMock()
                service_instance.search_guides = AsyncMock(return_value=[mock_repair_guide_result])
                service_instance._is_japanese_query = MagicMock(return_value=True)
                service_instance._preprocess_japanese_query = MagicMock(return_value=device)
                service_instance._assess_japanese_mapping_quality = MagicMock(return_value=0.95)
                service_instance.japanese_mapper = MagicMock()
                mock_service.return_value = service_instance

                response = client.get(
                    f"/api/repair-guides/device/{device}",
                    params={"language": "ja", "limit": 10}
                )

                assert response.status_code == 200
                data = response.json()
                assert "results" in data
                assert "metadata" in data

    def test_error_handling_invalid_japanese(self, client):
        """Test error handling for invalid Japanese input"""
        # Test invalid character sequences that might cause encoding issues
        invalid_inputs = [
            "\x80\x81\x82",  # Invalid UTF-8 bytes
            "�",  # Replacement character
        ]

        for invalid_input in invalid_inputs:
            test_request = {
                "query": invalid_input,
                "language": "ja",
                "limit": 5
            }

            response = client.post("/api/repair-guides/search", json=test_request)
            
            # Should handle gracefully, either 200 with empty results or 400 with clear error
            assert response.status_code in [200, 400]
            
            if response.status_code == 400:
                error_data = response.json()
                assert "detail" in error_data

    def test_performance_japanese_search(self, client, mock_repair_guide_result):
        """Test performance metrics for Japanese search"""
        test_request = {
            "query": "大きなスイッチの画面修理ガイド",
            "language": "ja",
            "limit": 20
        }

        with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
            service_instance = MagicMock()
            service_instance.search_guides = AsyncMock(return_value=[mock_repair_guide_result] * 20)
            service_instance._is_japanese_query = MagicMock(return_value=True)
            service_instance._preprocess_japanese_query = MagicMock(return_value="Nintendo Switch screen repair guide")
            service_instance._assess_japanese_mapping_quality = MagicMock(return_value=0.85)
            service_instance.japanese_mapper = MagicMock()
            mock_service.return_value = service_instance

            response = client.post("/api/repair-guides/search", json=test_request)

            assert response.status_code == 200
            data = response.json()

            # Verify performance metrics are included
            metadata = data["metadata"]
            assert "processing_time_ms" in metadata
            assert isinstance(metadata["processing_time_ms"], int)
            assert metadata["processing_time_ms"] >= 0

    def test_cache_behavior_japanese(self, client, mock_repair_guide_result):
        """Test caching behavior with Japanese queries"""
        test_request = {
            "query": "スイッチ修理",
            "language": "ja",
            "use_cache": True,
            "limit": 5
        }

        with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
            service_instance = MagicMock()
            service_instance.search_guides = AsyncMock(return_value=[mock_repair_guide_result])
            service_instance._is_japanese_query = MagicMock(return_value=True)
            service_instance._preprocess_japanese_query = MagicMock(return_value="switch repair")
            service_instance._assess_japanese_mapping_quality = MagicMock(return_value=0.9)
            service_instance.japanese_mapper = MagicMock()
            mock_service.return_value = service_instance

            # First request
            response1 = client.post("/api/repair-guides/search", json=test_request)
            assert response1.status_code == 200

            # Second request (should potentially use cache)
            response2 = client.post("/api/repair-guides/search", json=test_request)
            assert response2.status_code == 200

            # Verify both responses are consistent
            assert response1.json() == response2.json()

    def test_api_documentation_examples(self, client):
        """Test that API documentation examples work correctly"""
        # Test the example from the model schema
        example_request = {
            "query": "スイッチ 画面修理",
            "language": "ja",
            "filters": {
                "difficulty_level": "初心者",
                "category": "画面修理",
                "device_type": "スイッチ"
            },
            "limit": 10
        }

        with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
            service_instance = MagicMock()
            service_instance.search_guides = AsyncMock(return_value=[])
            service_instance._is_japanese_query = MagicMock(return_value=True)
            service_instance._preprocess_japanese_query = MagicMock(return_value="Nintendo Switch screen repair")
            service_instance._assess_japanese_mapping_quality = MagicMock(return_value=0.95)
            service_instance.japanese_mapper = MagicMock()
            mock_service.return_value = service_instance

            response = client.post("/api/repair-guides/search", json=example_request)
            assert response.status_code == 200

            # Verify response matches expected structure
            data = response.json()
            assert "results" in data
            assert "metadata" in data
            assert data["metadata"]["language_detected"] == "ja"

    def test_edge_cases_japanese(self, client):
        """Test edge cases for Japanese input"""
        edge_cases = [
            "",  # Empty string
            " ",  # Whitespace only
            "   スイッチ   ",  # Leading/trailing whitespace
            "スイッチ\n修理",  # Newline characters
            "スイッチ　修理",  # Full-width spaces
        ]

        for query in edge_cases:
            test_request = {
                "query": query,
                "language": "ja",
                "limit": 5
            }

            if query.strip():  # Non-empty after stripping
                with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
                    service_instance = MagicMock()
                    service_instance.search_guides = AsyncMock(return_value=[])
                    service_instance._is_japanese_query = MagicMock(return_value=True)
                    service_instance._preprocess_japanese_query = MagicMock(return_value=query.strip())
                    service_instance._assess_japanese_mapping_quality = MagicMock(return_value=1.0)
                    service_instance.japanese_mapper = MagicMock()
                    mock_service.return_value = service_instance

                    response = client.post("/api/repair-guides/search", json=test_request)
                    assert response.status_code == 200
            else:
                # Empty queries should return validation error
                response = client.post("/api/repair-guides/search", json=test_request)
                assert response.status_code == 422  # Validation error

    def test_japanese_response_headers(self, client):
        """Test that response headers are properly set for Japanese content"""
        test_request = {
            "query": "スイッチ修理",
            "language": "ja",
            "limit": 5
        }

        with patch('src.services.repair_guide_service.get_repair_guide_service') as mock_service:
            service_instance = MagicMock()
            service_instance.search_guides = AsyncMock(return_value=[])
            service_instance._is_japanese_query = MagicMock(return_value=True)
            service_instance._preprocess_japanese_query = MagicMock(return_value="switch repair")
            service_instance._assess_japanese_mapping_quality = MagicMock(return_value=1.0)
            service_instance.japanese_mapper = MagicMock()
            mock_service.return_value = service_instance

            response = client.post("/api/repair-guides/search", json=test_request)
            assert response.status_code == 200

            # Verify content type is properly set for JSON with UTF-8
            content_type = response.headers.get("content-type", "")
            assert "application/json" in content_type

    @pytest.mark.parametrize("endpoint", [
        "/api/repair-guides/search",
        "/api/repair-guides/trending",
    ])
    def test_endpoint_availability(self, client, endpoint):
        """Test that all Japanese-enabled endpoints are available"""
        if endpoint == "/api/repair-guides/search":
            # POST request
            response = client.post(endpoint, json={"query": "test", "language": "ja"})
        else:
            # GET request
            response = client.get(endpoint)
        
        # Should not return 404 - endpoint exists
        assert response.status_code != 404