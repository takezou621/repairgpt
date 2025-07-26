"""
Repair Guide API Routes - Japanese Search Support
Provides endpoints for searching and retrieving repair guides with Japanese language support
"""

import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from ...services.repair_guide_service import (
    SearchFilters,
    get_repair_guide_service,
)
from ...utils.logger import get_logger
from ..models import (
    RepairGuide,
    RepairGuideSearchRequest,
    RepairGuideSearchResponse,
    SearchLanguage,
    SearchMetadata,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/repair-guides", tags=["repair-guides"])


@router.post(
    "/search",
    response_model=RepairGuideSearchResponse,
    summary="Search repair guides with Japanese support",
    description="""
    Search for repair guides with enhanced Japanese language support.

    Features:
    - Japanese device name mapping (e.g., "スイッチ" → "Nintendo Switch")
    - Japanese difficulty level mapping (e.g., "初心者" → "beginner")
    - Japanese category mapping (e.g., "画面修理" → "screen repair")
    - Confidence scoring for search relevance
    - UTF-8 encoding support for Japanese characters
    """,
)
async def search_repair_guides(
    request: RepairGuideSearchRequest,
) -> RepairGuideSearchResponse:
    """
    Search for repair guides with Japanese language support.

    Args:
        request: Search request with query, language, and filters

    Returns:
        RepairGuideSearchResponse with results and metadata

    Raises:
        HTTPException: If search fails or invalid parameters provided
    """
    start_time = time.time()

    try:
        logger.info(
            f"Searching repair guides: query='{request.query}', " f"language={request.language}, limit={request.limit}"
        )

        # Get repair guide service
        service = get_repair_guide_service()

        # Convert API models to service models
        service_filters = None
        if request.filters:
            service_filters = SearchFilters(
                device_type=request.filters.device_type,
                difficulty_level=request.filters.difficulty_level,
                category=request.filters.category,
                max_time=request.filters.max_time,
                required_tools=request.filters.required_tools,
                exclude_tools=request.filters.exclude_tools,
                language=request.language.value,
                include_community_guides=request.filters.include_community_guides,
                min_rating=request.filters.min_rating,
            )

        # Perform search
        search_results = await service.search_guides(
            query=request.query,
            filters=service_filters,
            limit=request.limit,
            use_cache=request.use_cache,
        )

        # Convert service results to API models
        api_results = []
        total_confidence = 0.0
        japanese_mapping_quality = 1.0

        for result in search_results:
            # Calculate Japanese mapping quality if available
            if result.confidence_score and service.japanese_mapper:
                if service._is_japanese_query(request.query):
                    japanese_mapping_quality = service._assess_japanese_mapping_quality(request.query)

            total_confidence += result.confidence_score

            api_guide = RepairGuide(
                id=str(result.guide.guideid),
                title=result.guide.title,
                device_type=_map_device_name_to_enum(result.guide.device),
                device_model=getattr(result.guide, "device_model", None),
                difficulty=_map_difficulty_to_enum(result.guide.difficulty),
                time_estimate=result.guide.time_required or "Unknown",
                cost_estimate=result.estimated_cost,
                success_rate=f"{result.success_rate:.0%}" if result.success_rate else None,
                summary=result.guide.summary,
                tools_required=result.guide.tools or [],
                parts_required=result.guide.parts or [],
                warnings=getattr(result.guide, "warnings", []),
                steps=[],  # Detailed steps would be populated in get_guide_details
                tips=getattr(result.guide, "tips", []),
                source=result.source,
                confidence_score=result.confidence_score,
                last_updated=result.last_updated.isoformat() if result.last_updated else None,
            )
            api_results.append(api_guide)

        # Calculate average confidence
        avg_confidence = total_confidence / len(search_results) if search_results else 0.0

        # Detect language and get processed query
        language_detected = "ja" if service._is_japanese_query(request.query) else "en"
        query_processed = service._preprocess_japanese_query(request.query)

        # Create metadata
        processing_time_ms = int((time.time() - start_time) * 1000)
        metadata = SearchMetadata(
            total_found=len(search_results),
            language_detected=language_detected,
            query_processed=query_processed,
            japanese_mapping_quality=japanese_mapping_quality if language_detected == "ja" else None,
            search_confidence=avg_confidence,
            cache_hit=False,  # Would be set by cache check
            processing_time_ms=processing_time_ms,
        )

        logger.info(f"Search completed: found {len(search_results)} results in {processing_time_ms}ms")

        return RepairGuideSearchResponse(
            results=api_results,
            metadata=metadata,
        )

    except ValueError as e:
        logger.error(f"Invalid search parameters: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid search parameters: {str(e)}",
        )
    except UnicodeDecodeError as e:
        logger.error(f"Japanese character encoding error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid character encoding. Please ensure Japanese text is properly UTF-8 encoded.",
        )
    except ConnectionError as e:
        logger.error(f"External service connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Repair guide service temporarily unavailable. Please try again later.",
        )
    except Exception as e:
        logger.error(f"Unexpected error in repair guide search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while searching repair guides.",
        )


@router.get(
    "/search",
    response_model=RepairGuideSearchResponse,
    summary="Search repair guides (GET method)",
    description="Alternative GET endpoint for repair guide search with query parameters",
)
async def search_repair_guides_get(
    query: str = Query(..., description="Search query (Japanese or English)"),
    language: SearchLanguage = Query(default=SearchLanguage.ENGLISH, description="Search language"),
    device_type: Optional[str] = Query(None, description="Device type filter"),
    difficulty_level: Optional[str] = Query(None, description="Difficulty level filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum results"),
    use_cache: bool = Query(default=True, description="Use cached results"),
) -> RepairGuideSearchResponse:
    """
    GET endpoint for repair guide search with query parameters.

    Supports the same Japanese functionality as the POST endpoint but via query parameters.
    """
    # Convert query parameters to request model
    from models import RepairGuideSearchFilters

    filters = RepairGuideSearchFilters(
        device_type=device_type,
        difficulty_level=difficulty_level,
        category=category,
    )

    request = RepairGuideSearchRequest(
        query=query,
        language=language,
        filters=filters,
        limit=limit,
        use_cache=use_cache,
    )

    return await search_repair_guides(request)


@router.get(
    "/{guide_id}",
    response_model=RepairGuide,
    summary="Get detailed repair guide",
    description="Retrieve detailed information for a specific repair guide",
)
async def get_repair_guide_details(
    guide_id: str,
    source: str = Query(default="ifixit", description="Guide source (ifixit, offline)"),
) -> RepairGuide:
    """
    Get detailed information for a specific repair guide.

    Args:
        guide_id: Unique identifier for the repair guide
        source: Source of the guide (ifixit, offline)

    Returns:
        Detailed repair guide information

    Raises:
        HTTPException: If guide not found or error occurs
    """
    try:
        logger.info(f"Fetching repair guide details: id={guide_id}, source={source}")

        service = get_repair_guide_service()

        # Convert guide_id to integer for iFixit API
        try:
            guide_id_int = int(guide_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid guide ID format",
            )

        result = await service.get_guide_details(
            guide_id=guide_id_int,
            source=source,
            use_cache=True,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repair guide {guide_id} not found",
            )

        # Convert to API model with detailed steps
        steps = []
        if hasattr(result.guide, "steps") and result.guide.steps:
            from ..models import RepairGuideStep

            for i, step in enumerate(result.guide.steps, 1):
                api_step = RepairGuideStep(
                    step_number=i,
                    title=getattr(step, "title", f"Step {i}"),
                    description=getattr(step, "text", step) if isinstance(step, str) else str(step),
                    image_url=getattr(step, "image_url", None),
                    video_url=getattr(step, "video_url", None),
                    tools_needed=getattr(step, "tools", []),
                    warnings=getattr(step, "warnings", []),
                    tips=getattr(step, "tips", []),
                )
                steps.append(api_step)

        api_guide = RepairGuide(
            id=str(result.guide.guideid),
            title=result.guide.title,
            device_type=_map_device_name_to_enum(result.guide.device),
            device_model=getattr(result.guide, "device_model", None),
            difficulty=_map_difficulty_to_enum(result.guide.difficulty),
            time_estimate=result.guide.time_estimate or "Unknown",
            cost_estimate=result.estimated_cost,
            success_rate=f"{result.success_rate:.0%}" if result.success_rate else None,
            summary=result.guide.summary,
            tools_required=result.guide.tools or [],
            parts_required=result.guide.parts or [],
            warnings=getattr(result.guide, "warnings", []),
            steps=steps,
            tips=getattr(result.guide, "tips", []),
            source=result.source,
            confidence_score=result.confidence_score,
            last_updated=result.last_updated.isoformat() if result.last_updated else None,
        )

        logger.info(f"Successfully retrieved guide details for {guide_id}")
        return api_guide

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid guide ID: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid guide ID: {str(e)}",
        )
    except ConnectionError as e:
        logger.error(f"External service connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Repair guide service temporarily unavailable.",
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching guide {guide_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the repair guide.",
        )


@router.get(
    "/device/{device_type}",
    response_model=RepairGuideSearchResponse,
    summary="Get guides for specific device",
    description="Get repair guides for a specific device type with Japanese device name support",
)
async def get_guides_by_device(
    device_type: str,
    device_model: Optional[str] = Query(None, description="Specific device model"),
    issue_type: Optional[str] = Query(None, description="Type of issue"),
    language: SearchLanguage = Query(default=SearchLanguage.ENGLISH, description="Response language"),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum results"),
) -> RepairGuideSearchResponse:
    """
    Get repair guides for a specific device type.

    Supports Japanese device names (e.g., "スイッチ", "アイフォン").
    """
    try:
        logger.info(f"Fetching guides for device: {device_type}, model: {device_model}")

        # Build search filters
        from ..models import RepairGuideSearchFilters

        filters = RepairGuideSearchFilters(device_type=device_type)

        # Build query
        query_parts = [device_type]
        if device_model:
            query_parts.append(device_model)
        if issue_type:
            query_parts.append(issue_type)
        query = " ".join(query_parts)

        # Create search request
        request = RepairGuideSearchRequest(
            query=query,
            language=language,
            filters=filters,
            limit=limit,
        )

        return await search_repair_guides(request)

    except Exception as e:
        logger.error(f"Error fetching guides for device {device_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching guides for device {device_type}",
        )


@router.get(
    "/trending",
    response_model=RepairGuideSearchResponse,
    summary="Get trending repair guides",
    description="Get currently trending repair guides",
)
async def get_trending_guides(
    limit: int = Query(default=10, ge=1, le=50, description="Maximum results"),
) -> RepairGuideSearchResponse:
    """Get trending repair guides."""
    try:
        logger.info(f"Fetching trending guides: limit={limit}")

        service = get_repair_guide_service()
        results = await service.get_trending_guides(limit=limit)

        # Convert to API models
        api_results = []
        for result in results:
            api_guide = RepairGuide(
                id=str(result.guide.guideid),
                title=result.guide.title,
                device_type=_map_device_name_to_enum(result.guide.device),
                device_model=getattr(result.guide, "device_model", None),
                difficulty=_map_difficulty_to_enum(result.guide.difficulty),
                time_estimate=result.guide.time_required or "Unknown",
                cost_estimate=result.estimated_cost,
                success_rate=f"{result.success_rate:.0%}" if result.success_rate else None,
                summary=result.guide.summary,
                tools_required=result.guide.tools or [],
                parts_required=result.guide.parts or [],
                warnings=getattr(result.guide, "warnings", []),
                steps=[],
                tips=getattr(result.guide, "tips", []),
                source=result.source,
                confidence_score=result.confidence_score,
                last_updated=result.last_updated.isoformat() if result.last_updated else None,
            )
            api_results.append(api_guide)

        metadata = SearchMetadata(
            total_found=len(results),
            language_detected="en",
            query_processed="trending",
            search_confidence=0.9,
            cache_hit=False,
        )

        return RepairGuideSearchResponse(
            results=api_results,
            metadata=metadata,
        )

    except Exception as e:
        logger.error(f"Error fetching trending guides: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching trending guides",
        )


# Helper functions
def _map_device_name_to_enum(device_name: str) -> str:
    """Map device name to DeviceType enum value."""
    device_mapping = {
        "nintendo switch": "nintendo_switch",
        "switch": "nintendo_switch",
        "iphone": "iphone",
        "ipad": "ipad",
        "macbook": "macbook",
        "imac": "imac",
        "playstation 5": "playstation_5",
        "ps5": "playstation_5",
        "playstation 4": "playstation_4",
        "ps4": "playstation_4",
        "xbox series": "xbox_series",
        "xbox one": "xbox_one",
        "samsung galaxy": "samsung_galaxy",
        "google pixel": "google_pixel",
        "laptop": "laptop",
        "desktop": "desktop_pc",
    }

    device_lower = device_name.lower()
    for key, value in device_mapping.items():
        if key in device_lower:
            return value

    return "other"


def _map_difficulty_to_enum(difficulty: str) -> str:
    """Map difficulty string to RepairDifficulty enum value."""
    difficulty_mapping = {
        "easy": "easy",
        "moderate": "medium",
        "difficult": "hard",
        "very difficult": "expert",
        "beginner": "easy",
        "intermediate": "medium",
        "expert": "expert",
    }

    difficulty_lower = difficulty.lower()
    return difficulty_mapping.get(difficulty_lower, "medium")
