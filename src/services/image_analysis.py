"""
AI-powered image analysis service for device diagnosis
Supports multiple AI providers and comprehensive device analysis
"""

import base64
import io
import logging
import hashlib
import json
import os
import time
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

try:
    import cv2
    import numpy as np

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None

try:
    from PIL import Image, ImageEnhance, ImageFilter

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

try:
    import openai
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
    OpenAI = None

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    from ..utils.logger import get_logger
except ImportError:
    # Fallback for direct execution
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from utils.logger import get_logger

logger = get_logger(__name__)


class DamageType(Enum):
    """Types of damage that can be detected"""

    SCREEN_CRACK = "screen_crack"
    LIQUID_DAMAGE = "liquid_damage"
    PHYSICAL_DAMAGE = "physical_damage"
    BUTTON_DAMAGE = "button_damage"
    PORT_DAMAGE = "port_damage"
    BATTERY_SWELLING = "battery_swelling"
    CORROSION = "corrosion"
    SCRATCHES = "scratches"
    DENTS = "dents"
    MISSING_PARTS = "missing_parts"


class DeviceType(Enum):
    """Types of devices that can be analyzed"""

    SMARTPHONE = "smartphone"
    TABLET = "tablet"
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    GAMING_CONSOLE = "gaming_console"
    SMARTWATCH = "smartwatch"
    HEADPHONES = "headphones"
    OTHER = "other"


@dataclass
class DamageAssessment:
    """Represents detected damage"""

    damage_type: DamageType
    confidence: float
    severity: str  # "low", "medium", "high", "critical"
    location: Optional[str] = None
    description: str = ""


@dataclass
class DeviceInfo:
    """Represents detected device information"""

    device_type: DeviceType
    brand: Optional[str] = None
    model: Optional[str] = None
    confidence: float = 0.0


@dataclass
class AnalysisResult:
    """Complete image analysis result"""

    device_info: DeviceInfo
    damage_detected: List[DamageAssessment]
    overall_condition: str  # "excellent", "good", "fair", "poor", "critical"
    repair_urgency: str  # "none", "low", "medium", "high", "critical"
    estimated_repair_cost: Optional[str] = None
    repair_difficulty: Optional[str] = None
    analysis_confidence: float = 0.0
    recommended_actions: List[str] = None
    warnings: List[str] = None
    language: str = "en"

    def __post_init__(self):
        if self.recommended_actions is None:
            self.recommended_actions = []
        if self.warnings is None:
            self.warnings = []


class AnalysisCache:
    """Cache for image analysis results"""

    def __init__(self, redis_url: Optional[str] = None, ttl: int = 86400):
        self.ttl = ttl  # 24 hours default
        self.redis_client = None
        self.memory_cache = {}

        if REDIS_AVAILABLE and (redis_url or os.getenv("REDIS_URL")):
            try:
                self.redis_client = redis.from_url(
                    redis_url or os.getenv("REDIS_URL"), decode_responses=True
                )
                self.redis_client.ping()
                logger.info("Analysis cache initialized with Redis")
            except Exception as e:
                logger.warning(f"Redis cache failed, using memory: {e}")
                self.redis_client = None
        else:
            logger.info("Using memory cache for image analysis")

    def _make_image_hash(self, image_data: bytes) -> str:
        """Create hash from image data"""
        return hashlib.md5(image_data).hexdigest()

    def get(self, image_hash: str, language: str = "en") -> Optional[AnalysisResult]:
        """Get cached analysis result"""
        cache_key = f"analysis:{image_hash}:{language}"

        if self.redis_client:
            try:
                data = self.redis_client.get(cache_key)
                if data:
                    result_dict = json.loads(data)
                    return self._dict_to_analysis_result(result_dict)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        # Memory cache fallback
        cached_item = self.memory_cache.get(cache_key)
        if cached_item:
            if datetime.now() - cached_item["timestamp"] < timedelta(seconds=self.ttl):
                return self._dict_to_analysis_result(cached_item["data"])
            else:
                del self.memory_cache[cache_key]

        return None

    def set(self, image_hash: str, result: AnalysisResult, language: str = "en"):
        """Cache analysis result"""
        cache_key = f"analysis:{image_hash}:{language}"
        result_dict = self._analysis_result_to_dict(result)

        if self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key, self.ttl, json.dumps(result_dict, default=str)
                )
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        # Memory cache fallback
        self.memory_cache[cache_key] = {
            "data": result_dict,
            "timestamp": datetime.now(),
        }

    def _analysis_result_to_dict(self, result: AnalysisResult) -> Dict[str, Any]:
        """Convert AnalysisResult to dict for caching"""
        result_dict = asdict(result)
        # Convert enums to strings
        result_dict["device_info"]["device_type"] = result.device_info.device_type.value
        for damage in result_dict["damage_detected"]:
            damage["damage_type"] = (
                damage["damage_type"].value
                if hasattr(damage["damage_type"], "value")
                else damage["damage_type"]
            )
        return result_dict

    def _dict_to_analysis_result(self, data: Dict[str, Any]) -> AnalysisResult:
        """Convert cached dict back to AnalysisResult"""
        # Reconstruct device info
        device_info = DeviceInfo(
            device_type=DeviceType(data["device_info"]["device_type"]),
            brand=data["device_info"]["brand"],
            model=data["device_info"]["model"],
            confidence=data["device_info"]["confidence"],
        )

        # Reconstruct damage assessments
        damage_list = []
        for damage_data in data["damage_detected"]:
            damage_list.append(
                DamageAssessment(
                    damage_type=DamageType(damage_data["damage_type"]),
                    confidence=damage_data["confidence"],
                    severity=damage_data["severity"],
                    location=damage_data["location"],
                    description=damage_data["description"],
                )
            )

        return AnalysisResult(
            device_info=device_info,
            damage_detected=damage_list,
            overall_condition=data["overall_condition"],
            repair_urgency=data["repair_urgency"],
            estimated_repair_cost=data.get("estimated_repair_cost"),
            repair_difficulty=data.get("repair_difficulty"),
            analysis_confidence=data["analysis_confidence"],
            recommended_actions=data["recommended_actions"],
            warnings=data["warnings"],
            language=data["language"],
        )


class ImageAnalysisService:
    """AI-powered image analysis service for device diagnosis"""

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        redis_url: Optional[str] = None,
        enable_caching: bool = True,
    ):
        """
        Initialize the image analysis service

        Args:
            provider: AI provider ("openai", "google", "local")
            api_key: API key for the provider
            redis_url: Redis URL for caching
            enable_caching: Whether to enable result caching
        """
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Initialize providers
        self.client = None
        if provider == "openai" and OPENAI_AVAILABLE:
            if not self.api_key:
                logger.warning(
                    "OpenAI API key not provided - analysis will use fallback methods"
                )
            else:
                try:
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info("OpenAI Vision API client initialized")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {e}")

        # Initialize caching
        self.cache = AnalysisCache(redis_url) if enable_caching else None

        # Image processing parameters
        self.max_image_size = (1024, 1024)
        self.supported_formats = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
        self.max_file_size = 10 * 1024 * 1024  # 10MB

        # Analysis statistics
        self.analysis_count = 0
        self.cache_hits = 0
        self.last_analysis_time = None

        logger.info(
            "ImageAnalysisService initialized",
            provider=provider,
            has_api_key=bool(self.api_key),
            caching_enabled=bool(self.cache),
        )

    def preprocess_image(self, image_data: bytes) -> Image.Image:
        """
        Preprocess image for analysis

        Args:
            image_data: Raw image bytes

        Returns:
            Processed PIL Image
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Resize if too large
            if (
                image.size[0] > self.max_image_size[0]
                or image.size[1] > self.max_image_size[1]
            ):
                image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)

            # Basic image enhancement
            image = self._enhance_image(image)

            return image

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise ValueError(f"Invalid image data: {e}")

    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Apply basic image enhancement for better analysis"""
        if not PIL_AVAILABLE:
            logger.warning("PIL not available - skipping image enhancement")
            return image

        try:
            # Apply basic PIL enhancements
            enhancer = ImageEnhance.Contrast(image)
            enhanced = enhancer.enhance(1.2)  # Increase contrast slightly

            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(1.1)  # Slight sharpening

            # If OpenCV is available, apply advanced enhancement
            if CV2_AVAILABLE:
                enhanced = self._advanced_enhancement(enhanced)

            return enhanced
        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            return image

    def _advanced_enhancement(self, image: Image.Image) -> Image.Image:
        """Apply advanced OpenCV enhancement"""
        try:
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

            # Convert back to PIL
            return Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
        except Exception as e:
            logger.warning(f"Advanced enhancement failed: {e}")
            return image

    def _encode_image_base64(self, image: Image.Image) -> str:
        """Encode image as base64 for API transmission"""
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=95)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    async def analyze_with_openai(
        self, image: Image.Image, language: str = "en"
    ) -> AnalysisResult:
        """Analyze image using OpenAI Vision API"""
        try:
            # Encode image
            base64_image = self._encode_image_base64(image)

            # Create analysis prompt based on language
            prompt = self._create_analysis_prompt(language)

            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=1500,
                temperature=0.1,
            )

            # Parse response into structured format
            analysis_text = response.choices[0].message.content
            return self._parse_openai_response(analysis_text, language)

        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            raise RuntimeError(f"AI analysis failed: {e}")

    def _create_analysis_prompt(self, language: str) -> str:
        """Create analysis prompt based on language"""
        if language == "ja":
            return """この画像に写っている電子機器を詳しく分析してください。以下の情報を提供してください：

1. デバイスタイプと機種（スマートフォン、タブレット、ラップトップなど）
2. ブランドとモデル（可能であれば）
3. 発見された損傷の種類と重要度
4. 全体的な状態評価
5. 修理の緊急度
6. 推奨される対処法
7. 注意事項

損傷の種類：画面割れ、液体損傷、物理的損傷、ボタン損傷、ポート損傷、バッテリー膨張、腐食、傷、凹み、部品の欠損

JSON形式で回答してください。"""
        else:
            return """Analyze this electronic device image in detail. Provide the following information:

1. Device type and model (smartphone, tablet, laptop, etc.)
2. Brand and model (if identifiable)
3. Types and severity of damage detected
4. Overall condition assessment
5. Repair urgency level
6. Recommended actions
7. Warnings and safety concerns

Damage types to look for: screen cracks, liquid damage, physical damage, button damage, port damage, battery swelling, corrosion, scratches, dents, missing parts

Please respond in JSON format."""

    def _parse_openai_response(
        self, response_text: str, language: str
    ) -> AnalysisResult:
        """Parse OpenAI response into structured AnalysisResult"""
        import json
        import re

        try:
            # Try to extract JSON from response
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback: create structured response from text
                data = self._fallback_parse(response_text, language)

            # Extract device info
            device_info = DeviceInfo(
                device_type=DeviceType(data.get("device_type", "other")),
                brand=data.get("brand"),
                model=data.get("model"),
                confidence=data.get("device_confidence", 0.8),
            )

            # Extract damage assessments
            damage_list = []
            for damage in data.get("damages", []):
                damage_list.append(
                    DamageAssessment(
                        damage_type=DamageType(damage.get("type", "physical_damage")),
                        confidence=damage.get("confidence", 0.7),
                        severity=damage.get("severity", "medium"),
                        location=damage.get("location"),
                        description=damage.get("description", ""),
                    )
                )

            return AnalysisResult(
                device_info=device_info,
                damage_detected=damage_list,
                overall_condition=data.get("overall_condition", "unknown"),
                repair_urgency=data.get("repair_urgency", "medium"),
                estimated_repair_cost=data.get("estimated_cost"),
                repair_difficulty=data.get("repair_difficulty"),
                analysis_confidence=data.get("analysis_confidence", 0.8),
                recommended_actions=data.get("recommended_actions", []),
                warnings=data.get("warnings", []),
                language=language,
            )

        except Exception as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            # Return basic analysis
            return self._create_fallback_result(language)

    def _fallback_parse(self, text: str, language: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        # Basic text analysis to extract key information
        return {
            "device_type": "other",
            "overall_condition": "unknown",
            "repair_urgency": "medium",
            "damages": [],
            "analysis_confidence": 0.5,
            "recommended_actions": ["Professional diagnosis recommended"],
            "warnings": ["Unable to perform detailed analysis"],
        }

    def _create_fallback_result(self, language: str) -> AnalysisResult:
        """Create fallback result when analysis fails"""
        return AnalysisResult(
            device_info=DeviceInfo(device_type=DeviceType.OTHER, confidence=0.1),
            damage_detected=[],
            overall_condition="unknown",
            repair_urgency="medium",
            analysis_confidence=0.1,
            recommended_actions=["Professional diagnosis recommended"],
            warnings=["Analysis failed - manual inspection needed"],
            language=language,
        )

    async def analyze_device_image(
        self, image_data: bytes, language: str = "en", use_cache: bool = True
    ) -> AnalysisResult:
        """
        Main method to analyze device image

        Args:
            image_data: Raw image bytes
            language: Analysis language ("en" or "ja")
            use_cache: Whether to use cached results

        Returns:
            Complete analysis result
        """
        start_time = time.time()
        self.analysis_count += 1

        try:
            # Validate image
            if len(image_data) > self.max_file_size:
                raise ValueError(
                    f"Image file too large: {len(image_data)} bytes (max: {self.max_file_size})"
                )

            # Check cache first
            image_hash = hashlib.md5(image_data).hexdigest()
            if use_cache and self.cache:
                cached_result = self.cache.get(image_hash, language)
                if cached_result:
                    self.cache_hits += 1
                    logger.info(
                        "Retrieved analysis from cache",
                        image_hash=image_hash[:8],
                        language=language,
                        cache_hit_rate=f"{self.cache_hits/self.analysis_count:.2%}",
                    )
                    return cached_result

            # Validate and preprocess image
            if not PIL_AVAILABLE:
                raise RuntimeError("PIL (Pillow) is required for image processing")

            processed_image = self.preprocess_image(image_data)

            # Perform analysis based on provider
            if self.provider == "openai" and self.client:
                result = await self.analyze_with_openai(processed_image, language)
            elif self.provider == "local":
                result = await self.analyze_with_local_model(processed_image, language)
            else:
                # Fallback to rule-based analysis
                result = await self.analyze_with_fallback(processed_image, language)

            # Post-process results
            result = self._post_process_results(result, language)

            # Cache the result
            if use_cache and self.cache:
                self.cache.set(image_hash, result, language)

            # Update statistics
            analysis_time = time.time() - start_time
            self.last_analysis_time = analysis_time

            logger.info(
                "Image analysis completed",
                provider=self.provider,
                language=language,
                analysis_time=f"{analysis_time:.2f}s",
                confidence=result.analysis_confidence,
                damage_count=len(result.damage_detected),
            )

            return result

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return self._create_fallback_result(language)

    async def analyze_with_local_model(
        self, image: Image.Image, language: str = "en"
    ) -> AnalysisResult:
        """Analyze image using local computer vision models"""
        logger.info("Using local model analysis (basic computer vision)")

        # This is a placeholder for local model analysis
        # In a real implementation, you might use:
        # - OpenCV feature detection
        # - Traditional computer vision algorithms
        # - Local neural networks (ONNX, TensorFlow Lite)

        return self._create_basic_analysis_result(image, language)

    async def analyze_with_fallback(
        self, image: Image.Image, language: str = "en"
    ) -> AnalysisResult:
        """Fallback analysis using image metadata and basic processing"""
        logger.info("Using fallback analysis method")

        try:
            # Get basic image information
            width, height = image.size
            mode = image.mode

            # Basic heuristics based on image properties
            device_type = self._guess_device_type_from_image(image)
            condition = self._assess_basic_condition(image)

            return AnalysisResult(
                device_info=DeviceInfo(device_type=device_type, confidence=0.3),
                damage_detected=[],
                overall_condition=condition,
                repair_urgency="medium",
                analysis_confidence=0.3,
                recommended_actions=[
                    (
                        "Upload a clearer image for better analysis"
                        if language == "en"
                        else "より鮮明な画像をアップロードしてください"
                    ),
                    (
                        "Consider professional diagnosis"
                        if language == "en"
                        else "専門家による診断をご検討ください"
                    ),
                ],
                warnings=[
                    (
                        "Analysis performed without AI assistance"
                        if language == "en"
                        else "AI支援なしでの分析を実行しました"
                    )
                ],
                language=language,
            )

        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
            return self._create_fallback_result(language)

    def _guess_device_type_from_image(self, image: Image.Image) -> DeviceType:
        """Guess device type from image dimensions and properties"""
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 1.0

        # Simple heuristics based on aspect ratio
        if 0.5 <= aspect_ratio <= 0.7:  # Portrait phone-like
            return DeviceType.SMARTPHONE
        elif 1.2 <= aspect_ratio <= 1.4:  # Landscape tablet-like
            return DeviceType.TABLET
        elif aspect_ratio >= 1.5:  # Wide laptop-like
            return DeviceType.LAPTOP
        else:
            return DeviceType.OTHER

    def _assess_basic_condition(self, image: Image.Image) -> str:
        """Basic condition assessment using image statistics"""
        try:
            if not PIL_AVAILABLE:
                return "unknown"

            # Convert to grayscale for analysis
            gray = image.convert("L")

            # Calculate image statistics
            extrema = gray.getextrema()
            min_val, max_val = extrema
            contrast = max_val - min_val

            # Basic heuristics
            if contrast < 50:
                return "poor"  # Low contrast might indicate damage
            elif contrast > 200:
                return "good"  # High contrast suggests clear image
            else:
                return "fair"

        except Exception:
            return "unknown"

    def _create_basic_analysis_result(
        self, image: Image.Image, language: str
    ) -> AnalysisResult:
        """Create basic analysis result when advanced analysis isn't available"""
        device_type = self._guess_device_type_from_image(image)
        condition = self._assess_basic_condition(image)

        return AnalysisResult(
            device_info=DeviceInfo(device_type=device_type, confidence=0.5),
            damage_detected=[],
            overall_condition=condition,
            repair_urgency="medium",
            analysis_confidence=0.5,
            recommended_actions=[
                (
                    "Consider professional analysis for detailed diagnosis"
                    if language == "en"
                    else "詳細な診断には専門的な分析をご検討ください"
                )
            ],
            warnings=[
                (
                    "Basic analysis only - limited accuracy"
                    if language == "en"
                    else "基本分析のみ - 精度は限定的です"
                )
            ],
            language=language,
        )

    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis service statistics"""
        return {
            "total_analyses": self.analysis_count,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": f"{self.cache_hits/max(self.analysis_count, 1):.2%}",
            "last_analysis_time": self.last_analysis_time,
            "provider": self.provider,
            "has_api_key": bool(self.api_key),
            "cache_enabled": bool(self.cache),
            "supported_formats": self.supported_formats,
            "max_file_size_mb": self.max_file_size / (1024 * 1024),
        }

    def validate_image_format(
        self, image_data: bytes, filename: Optional[str] = None
    ) -> bool:
        """Validate if image format is supported"""
        try:
            if not PIL_AVAILABLE:
                return False

            image = Image.open(io.BytesIO(image_data))
            format_name = image.format.lower() if image.format else None

            # Check by format
            if format_name in ["jpeg", "jpg", "png", "webp", "gif"]:
                return True

            # Check by filename extension if provided
            if filename:
                ext = os.path.splitext(filename.lower())[1]
                return ext in self.supported_formats

            return False

        except Exception as e:
            logger.warning(f"Image format validation failed: {e}")
            return False

    def _post_process_results(
        self, result: AnalysisResult, language: str
    ) -> AnalysisResult:
        """Post-process analysis results for consistency"""
        # Ensure damage list is not empty if condition is poor
        if (
            result.overall_condition in ["poor", "critical"]
            and not result.damage_detected
        ):
            result.damage_detected.append(
                DamageAssessment(
                    damage_type=DamageType.PHYSICAL_DAMAGE,
                    confidence=0.6,
                    severity="medium",
                    description="General wear and damage detected",
                )
            )

        # Add safety warnings for critical conditions
        if result.overall_condition == "critical":
            safety_warning = (
                "⚠️ Critical condition detected - Stop using device immediately"
                if language == "en"
                else "⚠️ 危険な状態を検出 - 直ちに使用を中止してください"
            )
            if safety_warning not in result.warnings:
                result.warnings.append(safety_warning)

        return result


# Global service instance
_image_analysis_service: Optional[ImageAnalysisService] = None


def get_image_analysis_service() -> ImageAnalysisService:
    """Get global image analysis service instance"""
    global _image_analysis_service
    if _image_analysis_service is None:
        _image_analysis_service = ImageAnalysisService(
            provider="openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            redis_url=os.getenv("REDIS_URL"),
            enable_caching=True,
        )
    return _image_analysis_service


def reset_image_analysis_service():
    """Reset global service instance (for testing)"""
    global _image_analysis_service
    _image_analysis_service = None


# Utility functions for common use cases
async def quick_analyze_image(
    image_data: bytes, language: str = "en", provider: str = "openai"
) -> AnalysisResult:
    """Quick image analysis without using global service"""
    service = ImageAnalysisService(
        provider=provider,
        api_key=os.getenv("OPENAI_API_KEY") if provider == "openai" else None,
    )
    return await service.analyze_device_image(image_data, language)


def create_mock_analysis_result(
    device_type: str = "smartphone", condition: str = "fair", language: str = "en"
) -> AnalysisResult:
    """Create mock analysis result for testing/demo purposes"""
    return AnalysisResult(
        device_info=DeviceInfo(
            device_type=DeviceType(device_type.lower()),
            brand="Mock Brand",
            model="Demo Model",
            confidence=0.8,
        ),
        damage_detected=[
            DamageAssessment(
                damage_type=DamageType.SCREEN_CRACK,
                confidence=0.7,
                severity="medium",
                location="Top left corner",
                description=(
                    "Visible crack in display"
                    if language == "en"
                    else "ディスプレイに亀裂が見られます"
                ),
            )
        ],
        overall_condition=condition,
        repair_urgency="medium",
        estimated_repair_cost="$50-150" if language == "en" else "¥5,000-15,000",
        repair_difficulty="Moderate",
        analysis_confidence=0.8,
        recommended_actions=[
            (
                "Avoid using the device until repaired"
                if language == "en"
                else "修理するまで使用を控えてください"
            ),
            (
                "Seek professional repair service"
                if language == "en"
                else "専門的な修理サービスをお求めください"
            ),
        ],
        warnings=[
            (
                "This is a mock result for demonstration"
                if language == "en"
                else "これはデモンストレーション用の模擬結果です"
            )
        ],
        language=language,
    )
