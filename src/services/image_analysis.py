"""
AI-powered image analysis service for device diagnosis
Supports multiple AI providers and comprehensive device analysis
"""

import base64
import io
import logging
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np
from PIL import Image
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)


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


class ImageAnalysisService:
    """AI-powered image analysis service for device diagnosis"""

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        """
        Initialize the image analysis service

        Args:
            provider: AI provider ("openai", "google", "local")
            api_key: API key for the provider
        """
        self.provider = provider
        self.api_key = api_key

        if provider == "openai":
            self.client = OpenAI(api_key=api_key)

        # Image processing parameters
        self.max_image_size = (1024, 1024)
        self.supported_formats = [".jpg", ".jpeg", ".png", ".webp"]
        self.max_file_size = 10 * 1024 * 1024  # 10MB

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
        # Convert to OpenCV format for enhancement
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
        self, image_data: bytes, language: str = "en"
    ) -> AnalysisResult:
        """
        Main method to analyze device image

        Args:
            image_data: Raw image bytes
            language: Analysis language ("en" or "ja")

        Returns:
            Complete analysis result
        """
        try:
            # Validate and preprocess image
            if len(image_data) > self.max_file_size:
                raise ValueError("Image file too large")

            processed_image = self.preprocess_image(image_data)

            # Perform analysis based on provider
            if self.provider == "openai":
                result = await self.analyze_with_openai(processed_image, language)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            # Post-process results
            result = self._post_process_results(result, language)

            return result

        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return self._create_fallback_result(language)

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
