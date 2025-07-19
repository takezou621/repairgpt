#!/usr/bin/env python3
"""
Image Analysis Feature Implementation for Issue #115
Integrates with OpenAI Vision API for device damage detection
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_analysis import (
    ImageAnalysisService,
    get_image_analysis_service,
    AnalysisResult,
    DamageType,
    DeviceType
)
from utils.logger import get_logger

logger = get_logger(__name__)


class ImageAnalysisFeature:
    """Main feature class for image analysis functionality"""
    
    def __init__(self):
        """Initialize the image analysis feature"""
        self.service = get_image_analysis_service()
        logger.info("Image Analysis Feature initialized")
    
    async def analyze_image(
        self,
        image_data: bytes,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze device image for damage detection
        
        Args:
            image_data: Raw image bytes
            language: Analysis language ("en" or "ja")
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Validate image format
            if not self.service.validate_image_format(image_data):
                return {
                    "success": False,
                    "error": "Invalid image format. Supported formats: JPEG, PNG",
                    "issue": 115
                }
            
            # Perform analysis
            result = await self.service.analyze_device_image(
                image_data,
                language=language,
                use_cache=True
            )
            
            # Convert to API response format
            return self._format_analysis_response(result)
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "issue": 115
            }
    
    def _format_analysis_response(self, result: AnalysisResult) -> Dict[str, Any]:
        """Format analysis result for API response"""
        return {
            "success": True,
            "issue": 115,
            "device": {
                "type": result.device_info.device_type.value,
                "brand": result.device_info.brand,
                "model": result.device_info.model,
                "confidence": result.device_info.confidence
            },
            "damage": [
                {
                    "type": damage.damage_type.value,
                    "severity": damage.severity,
                    "confidence": damage.confidence,
                    "location": damage.location,
                    "description": damage.description
                }
                for damage in result.damage_detected
            ],
            "overall_condition": result.overall_condition,
            "repair_urgency": result.repair_urgency,
            "estimated_cost": result.estimated_repair_cost,
            "recommendations": result.recommended_actions,
            "warnings": result.warnings,
            "analysis_confidence": result.analysis_confidence,
            "language": result.language
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get analysis service statistics"""
        stats = self.service.get_analysis_stats()
        stats["issue"] = 115
        return stats


async def demo_analysis():
    """Demonstrate the image analysis feature"""
    feature = ImageAnalysisFeature()
    
    # Example: Create a mock image for demonstration
    try:
        from PIL import Image
        import io
        
        # Create a simple test image
        img = Image.new('RGB', (800, 600), color='gray')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_data = img_buffer.getvalue()
        
        print("🔍 Analyzing test image...")
        result = await feature.analyze_image(img_data, language="en")
        
        if result["success"]:
            print(f"✅ Analysis completed!")
            print(f"   Device Type: {result['device']['type']}")
            print(f"   Condition: {result['overall_condition']}")
            print(f"   Repair Urgency: {result['repair_urgency']}")
            if result['damage']:
                print(f"   Damage Found: {len(result['damage'])} issues")
        else:
            print(f"❌ Analysis failed: {result['error']}")
        
        # Show service statistics
        stats = feature.get_service_stats()
        print(f"\n📊 Service Statistics:")
        print(f"   Total Analyses: {stats['total_analyses']}")
        print(f"   Cache Hit Rate: {stats['cache_hit_rate']}")
        print(f"   Provider: {stats['provider']}")
        
    except ImportError:
        print("⚠️  PIL not available - install with: pip install Pillow")
        print("   Using mock analysis instead...")
        
        # Use the service's fallback mechanism
        result = await feature.service.analyze_device_image(b"mock_data", "en")
        print(f"Mock result: {result.overall_condition}")


def auto_feature_115():
    """Entry point for auto-generated feature"""
    print("🎨 Image Analysis Feature with OpenAI Vision API")
    print("=" * 50)
    
    # Check if API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("   The feature will work with fallback analysis")
    
    # Run the demo
    asyncio.run(demo_analysis())
    
    return {
        "status": "implemented",
        "issue": 115,
        "features": [
            "OpenAI Vision API integration",
            "Multi-language support (EN/JA)",
            "Device type detection",
            "Damage assessment with confidence scores",
            "Redis caching for performance",
            "Fallback analysis methods",
            "Comprehensive error handling"
        ]
    }


if __name__ == "__main__":
    result = auto_feature_115()
    print(f"\n✅ Feature implementation complete!")
    print(f"   Issue: #{result['issue']}")
    print(f"   Status: {result['status']}")
    print(f"   Features: {len(result['features'])} capabilities")\n