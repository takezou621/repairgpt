#!/usr/bin/env python3
"""
Unit tests for Image Analysis Feature (Issue #115)
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from auto_feature_115 import ImageAnalysisFeature, auto_feature_115
from services.image_analysis import (
    AnalysisResult,
    DeviceInfo,
    DamageAssessment,
    DeviceType,
    DamageType
)


class TestImageAnalysisFeature(unittest.TestCase):
    """Test cases for ImageAnalysisFeature class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_service = Mock()
        self.feature = ImageAnalysisFeature()
        self.feature.service = self.mock_service
    
    def test_init(self):
        """Test feature initialization"""
        with patch('auto_feature_115.get_image_analysis_service') as mock_get_service:
            feature = ImageAnalysisFeature()
            mock_get_service.assert_called_once()
            self.assertIsNotNone(feature.service)
    
    async def test_analyze_image_success(self):
        """Test successful image analysis"""
        # Mock image validation
        self.mock_service.validate_image_format.return_value = True
        
        # Create mock analysis result
        mock_result = AnalysisResult(
            device_info=DeviceInfo(
                device_type=DeviceType.SMARTPHONE,
                brand="TestBrand",
                model="TestModel",
                confidence=0.9
            ),
            damage_detected=[
                DamageAssessment(
                    damage_type=DamageType.SCREEN_CRACK,
                    confidence=0.8,
                    severity="high",
                    location="Top left",
                    description="Major crack"
                )
            ],
            overall_condition="poor",
            repair_urgency="high",
            estimated_repair_cost="$100-200",
            repair_difficulty="moderate",
            analysis_confidence=0.85,
            recommended_actions=["Replace screen"],
            warnings=["Handle with care"],
            language="en"
        )
        
        # Mock analyze_device_image
        self.mock_service.analyze_device_image = asyncio.coroutine(
            lambda *args, **kwargs: mock_result
        )
        
        # Test analysis
        result = await self.feature.analyze_image(b"test_image_data")
        
        # Verify results
        self.assertTrue(result["success"])
        self.assertEqual(result["issue"], 115)
        self.assertEqual(result["device"]["type"], "smartphone")
        self.assertEqual(result["device"]["brand"], "TestBrand")
        self.assertEqual(len(result["damage"]), 1)
        self.assertEqual(result["damage"][0]["type"], "screen_crack")
        self.assertEqual(result["overall_condition"], "poor")
        self.assertEqual(result["repair_urgency"], "high")
    
    async def test_analyze_image_invalid_format(self):
        """Test analysis with invalid image format"""
        # Mock invalid format
        self.mock_service.validate_image_format.return_value = False
        
        # Test analysis
        result = await self.feature.analyze_image(b"invalid_data")
        
        # Verify error result
        self.assertFalse(result["success"])
        self.assertIn("Invalid image format", result["error"])
        self.assertEqual(result["issue"], 115)
    
    async def test_analyze_image_exception(self):
        """Test analysis with exception"""
        # Mock validation success but analysis failure
        self.mock_service.validate_image_format.return_value = True
        self.mock_service.analyze_device_image = asyncio.coroutine(
            lambda *args, **kwargs: (_ for _ in ()).throw(Exception("API Error"))
        )
        
        # Test analysis
        result = await self.feature.analyze_image(b"test_data")
        
        # Verify error handling
        self.assertFalse(result["success"])
        self.assertIn("API Error", result["error"])
        self.assertEqual(result["issue"], 115)
    
    def test_get_service_stats(self):
        """Test service statistics retrieval"""
        # Mock stats
        mock_stats = {
            "total_analyses": 100,
            "cache_hits": 75,
            "cache_hit_rate": "75.00%",
            "provider": "openai"
        }
        self.mock_service.get_analysis_stats.return_value = mock_stats
        
        # Get stats
        stats = self.feature.get_service_stats()
        
        # Verify stats
        self.assertEqual(stats["total_analyses"], 100)
        self.assertEqual(stats["cache_hits"], 75)
        self.assertEqual(stats["issue"], 115)


class TestAutoFeature115(unittest.TestCase):
    """Test cases for auto_feature_115 function"""
    
    @patch('auto_feature_115.asyncio.run')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_auto_feature_115_with_api_key(self, mock_run):
        """Test auto_feature_115 with API key set"""
        result = auto_feature_115()
        
        # Verify result
        self.assertEqual(result["status"], "implemented")
        self.assertEqual(result["issue"], 115)
        self.assertIsInstance(result["features"], list)
        self.assertGreater(len(result["features"]), 0)
        
        # Verify asyncio.run was called
        mock_run.assert_called_once()
    
    @patch('auto_feature_115.asyncio.run')
    @patch.dict(os.environ, {}, clear=True)
    def test_auto_feature_115_without_api_key(self, mock_run):
        """Test auto_feature_115 without API key"""
        # Remove OPENAI_API_KEY if it exists
        os.environ.pop("OPENAI_API_KEY", None)
        
        result = auto_feature_115()
        
        # Verify result
        self.assertEqual(result["status"], "implemented")
        self.assertEqual(result["issue"], 115)
        
        # Verify asyncio.run was called
        mock_run.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests for the feature"""
    
    @patch('auto_feature_115.get_image_analysis_service')
    async def test_demo_analysis_with_pil(self, mock_get_service):
        """Test demo analysis with PIL available"""
        # Mock service
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        # Mock successful analysis
        mock_result = MagicMock()
        mock_result.overall_condition = "good"
        mock_service.analyze_device_image = asyncio.coroutine(
            lambda *args, **kwargs: mock_result
        )
        mock_service.get_analysis_stats.return_value = {
            "total_analyses": 1,
            "cache_hit_rate": "0.00%",
            "provider": "openai"
        }
        
        # Import and run demo
        from auto_feature_115 import demo_analysis
        
        # Test should complete without errors
        await demo_analysis()


def run_async_test(coro):
    """Helper to run async tests"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


if __name__ == "__main__":
    # Run async tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestImageAnalysisFeature)
    for test in suite:
        if asyncio.iscoroutinefunction(test._testMethodName):
            test_method = getattr(test, test._testMethodName)
            setattr(test, test._testMethodName, 
                    lambda self, tm=test_method: run_async_test(tm(self)))
    
    unittest.main()