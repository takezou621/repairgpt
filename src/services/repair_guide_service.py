"""Repair Guide Service - Integrates iFixit API with RepairGPT"""

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    from ..clients.ifixit_client import Guide, IFixitClient
    from ..data.offline_repair_database import OfflineRepairDatabase
    from ..utils.logger import get_logger
except ImportError:
    # Fallback for direct execution
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from clients.ifixit_client import Guide, IFixitClient
    from data.offline_repair_database import OfflineRepairDatabase
    from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RepairGuideResult:
    """Enhanced repair guide result with metadata"""

    guide: Guide
    source: str  # 'ifixit', 'offline', 'cached'
    confidence_score: float  # 0.0-1.0
    last_updated: datetime
    related_guides: List[Guide] = None
    difficulty_explanation: str = ""
    estimated_cost: Optional[str] = None
    success_rate: Optional[float] = None


@dataclass
class SearchFilters:
    """Search filters for repair guides"""

    device_type: Optional[str] = None
    difficulty_level: Optional[str] = None  # Easy, Moderate, Difficult
    max_time: Optional[str] = None  # "30 minutes", "1 hour", etc.
    required_tools: Optional[List[str]] = None
    exclude_tools: Optional[List[str]] = None
    category: Optional[str] = None
    language: str = "en"
    include_community_guides: bool = True
    min_rating: Optional[float] = None


class RateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, max_calls: int = 100, time_window: int = 3600):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def can_make_request(self) -> bool:
        """Check if we can make a request within rate limits"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)

        # Remove old calls
        self.calls = [call_time for call_time in self.calls if call_time > cutoff]

        return len(self.calls) < self.max_calls

    def record_request(self):
        """Record a new API request"""
        self.calls.append(datetime.now())

    def time_until_next_request(self) -> int:
        """Get seconds until next request is allowed"""
        if self.can_make_request():
            return 0

        oldest_call = min(self.calls)
        next_allowed = oldest_call + timedelta(seconds=self.time_window)
        return int((next_allowed - datetime.now()).total_seconds())


class CacheManager:
    """Manages caching of repair guide data"""

    def __init__(self, redis_url: Optional[str] = None, ttl: int = 86400):
        self.ttl = ttl  # 24 hours default
        self.redis_client = None
        self.memory_cache = {}  # Fallback to memory cache

        if REDIS_AVAILABLE and (redis_url or os.getenv("REDIS_URL")):
            try:
                self.redis_client = redis.from_url(
                    redis_url or os.getenv("REDIS_URL"), decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed, using memory cache: {e}")
                self.redis_client = None

    def _make_key(self, prefix: str, identifier: str) -> str:
        """Create a cache key"""
        # Hash long identifiers
        if len(identifier) > 100:
            identifier = hashlib.md5(identifier.encode()).hexdigest()
        return f"repairgpt:{prefix}:{identifier}"

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        cache_key = self._make_key("guide", key)

        if self.redis_client:
            try:
                data = self.redis_client.get(cache_key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        # Fallback to memory cache
        cached_item = self.memory_cache.get(cache_key)
        if cached_item:
            if datetime.now() - cached_item["timestamp"] < timedelta(seconds=self.ttl):
                return cached_item["data"]
            else:
                del self.memory_cache[cache_key]

        return None

    def set(self, key: str, value: Any):
        """Set item in cache"""
        cache_key = self._make_key("guide", key)
        serialized_value = json.dumps(value, default=str)

        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, self.ttl, serialized_value)
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

        # Fallback to memory cache
        self.memory_cache[cache_key] = {"data": value, "timestamp": datetime.now()}

        # Simple memory cache cleanup
        if len(self.memory_cache) > 1000:
            # Remove oldest 100 items
            sorted_items = sorted(
                self.memory_cache.items(), key=lambda x: x[1]["timestamp"]
            )
            for key, _ in sorted_items[:100]:
                del self.memory_cache[key]

    def delete(self, key: str):
        """Delete item from cache"""
        cache_key = self._make_key("guide", key)

        if self.redis_client:
            try:
                self.redis_client.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")

        self.memory_cache.pop(cache_key, None)


class RepairGuideService:
    """Service for finding and managing repair guides"""

    def __init__(
        self,
        ifixit_api_key: Optional[str] = None,
        redis_url: Optional[str] = None,
        enable_offline_fallback: bool = True,
    ):
        self.ifixit_client = IFixitClient(api_key=ifixit_api_key)
        self.cache_manager = CacheManager(redis_url)
        self.rate_limiter = RateLimiter(
            max_calls=100, time_window=3600
        )  # 100 calls/hour
        self.offline_db = OfflineRepairDatabase() if enable_offline_fallback else None

        logger.info(
            "RepairGuideService initialized",
            has_ifixit_key=bool(ifixit_api_key),
            has_cache=bool(self.cache_manager.redis_client),
            has_offline_db=bool(self.offline_db),
        )

    async def search_guides(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 10,
        use_cache: bool = True,
    ) -> List[RepairGuideResult]:
        """Search for repair guides with enhanced features"""
        if not filters:
            filters = SearchFilters()

        # Create cache key
        cache_key = self._create_search_cache_key(query, filters, limit)

        # Check cache first
        if use_cache:
            cached_results = self.cache_manager.get(cache_key)
            if cached_results:
                logger.info(f"Retrieved {len(cached_results)} guides from cache")
                return [RepairGuideResult(**result) for result in cached_results]

        # Perform search
        results = []

        # Try iFixit API first
        if self.rate_limiter.can_make_request():
            try:
                ifixit_guides = await self._search_ifixit_guides(query, filters, limit)
                self.rate_limiter.record_request()

                for guide in ifixit_guides:
                    result = RepairGuideResult(
                        guide=guide,
                        source="ifixit",
                        confidence_score=self._calculate_confidence_score(
                            guide, query, filters
                        ),
                        last_updated=datetime.now(),
                        difficulty_explanation=self._explain_difficulty(
                            guide.difficulty
                        ),
                        estimated_cost=self._estimate_repair_cost(guide),
                    )
                    results.append(result)

                logger.info(f"Retrieved {len(ifixit_guides)} guides from iFixit API")

            except Exception as e:
                logger.error(f"iFixit API search failed: {e}")
        else:
            wait_time = self.rate_limiter.time_until_next_request()
            logger.warning(f"Rate limit exceeded, need to wait {wait_time} seconds")

        # If we don't have enough results, try offline database
        if len(results) < limit and self.offline_db:
            try:
                offline_guides = await self._search_offline_guides(
                    query, filters, limit - len(results)
                )

                for guide in offline_guides:
                    result = RepairGuideResult(
                        guide=guide,
                        source="offline",
                        confidence_score=self._calculate_confidence_score(
                            guide, query, filters
                        )
                        * 0.8,  # Lower confidence for offline
                        last_updated=datetime.now()
                        - timedelta(days=30),  # Assume offline data is older
                        difficulty_explanation=self._explain_difficulty(
                            guide.difficulty
                        ),
                    )
                    results.append(result)

                logger.info(
                    f"Retrieved {len(offline_guides)} guides from offline database"
                )

            except Exception as e:
                logger.error(f"Offline database search failed: {e}")

        # Sort by confidence score
        results.sort(key=lambda x: x.confidence_score, reverse=True)
        results = results[:limit]

        # Cache results
        if use_cache and results:
            cache_data = [asdict(result) for result in results]
            self.cache_manager.set(cache_key, cache_data)

        # Enhance results with related guides
        if results:
            await self._enhance_with_related_guides(results[:3])  # Only for top 3

        logger.info(f"Returning {len(results)} total repair guides")
        return results

    async def get_guide_details(
        self, guide_id: int, source: str = "ifixit", use_cache: bool = True
    ) -> Optional[RepairGuideResult]:
        """Get detailed information for a specific guide"""
        cache_key = f"guide_details_{source}_{guide_id}"

        # Check cache
        if use_cache:
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"Retrieved guide {guide_id} details from cache")
                return RepairGuideResult(**cached_result)

        # Fetch from source
        guide = None
        if source == "ifixit" and self.rate_limiter.can_make_request():
            try:
                guide = self.ifixit_client.get_guide(guide_id)
                self.rate_limiter.record_request()
            except Exception as e:
                logger.error(f"Failed to get guide {guide_id} from iFixit: {e}")

        if not guide and self.offline_db:
            try:
                guide = await self._get_offline_guide(guide_id)
                source = "offline"
            except Exception as e:
                logger.error(f"Failed to get guide {guide_id} from offline db: {e}")

        if not guide:
            logger.warning(f"Guide {guide_id} not found in any source")
            return None

        # Create enhanced result
        result = RepairGuideResult(
            guide=guide,
            source=source,
            confidence_score=1.0,  # Full confidence for direct fetch
            last_updated=datetime.now(),
            difficulty_explanation=self._explain_difficulty(guide.difficulty),
            estimated_cost=self._estimate_repair_cost(guide),
            success_rate=self._estimate_success_rate(guide),
        )

        # Get related guides
        await self._enhance_with_related_guides([result])

        # Cache result
        if use_cache:
            self.cache_manager.set(cache_key, asdict(result))

        logger.info(f"Retrieved detailed information for guide {guide_id}")
        return result

    async def get_guides_by_device(
        self,
        device_type: str,
        device_model: Optional[str] = None,
        issue_type: Optional[str] = None,
        filters: Optional[SearchFilters] = None,
        limit: int = 20,
    ) -> List[RepairGuideResult]:
        """Get guides specifically for a device"""
        query_parts = [device_type]
        if device_model:
            query_parts.append(device_model)
        if issue_type:
            query_parts.append(issue_type)

        query = " ".join(query_parts)

        if not filters:
            filters = SearchFilters()
        filters.device_type = device_type

        return await self.search_guides(query, filters, limit)

    async def get_trending_guides(self, limit: int = 10) -> List[RepairGuideResult]:
        """Get trending repair guides"""
        cache_key = f"trending_guides_{limit}"

        # Check cache (shorter TTL for trending)
        cached_results = self.cache_manager.get(cache_key)
        if cached_results:
            return [RepairGuideResult(**result) for result in cached_results]

        results = []

        # Try iFixit trending
        if self.rate_limiter.can_make_request():
            try:
                trending_guides = self.ifixit_client.get_trending_guides(limit)
                self.rate_limiter.record_request()

                for guide in trending_guides:
                    result = RepairGuideResult(
                        guide=guide,
                        source="ifixit",
                        confidence_score=0.9,  # High confidence for trending
                        last_updated=datetime.now(),
                        difficulty_explanation=self._explain_difficulty(
                            guide.difficulty
                        ),
                    )
                    results.append(result)

            except Exception as e:
                logger.error(f"Failed to get trending guides: {e}")

        # Fallback to popular searches if needed
        if len(results) < limit:
            popular_queries = [
                "iPhone screen",
                "Nintendo Switch",
                "laptop battery",
                "headphones",
            ]
            for query in popular_queries:
                if len(results) >= limit:
                    break
                try:
                    search_results = await self.search_guides(
                        query, limit=2, use_cache=True
                    )
                    results.extend(search_results[:2])
                except Exception as e:
                    logger.error(f"Failed popular search for {query}: {e}")

        results = results[:limit]

        # Cache with shorter TTL (1 hour)
        if results:
            cache_data = [asdict(result) for result in results]
            # Temporary cache with 1 hour TTL
            original_ttl = self.cache_manager.ttl
            self.cache_manager.ttl = 3600
            self.cache_manager.set(cache_key, cache_data)
            self.cache_manager.ttl = original_ttl

        return results

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "redis_available": bool(self.cache_manager.redis_client),
            "memory_cache_size": len(self.cache_manager.memory_cache),
            "rate_limit_calls_remaining": self.rate_limiter.max_calls
            - len(self.rate_limiter.calls),
            "rate_limit_reset_in": self.rate_limiter.time_until_next_request(),
        }

        if self.cache_manager.redis_client:
            try:
                info = self.cache_manager.redis_client.info("memory")
                stats["redis_memory_usage"] = info.get("used_memory_human", "unknown")
            except Exception:
                pass

        return stats

    async def _search_ifixit_guides(
        self, query: str, filters: SearchFilters, limit: int
    ) -> List[Guide]:
        """Search iFixit API with filters"""
        # For now, use basic search - can be enhanced with filter application
        guides = self.ifixit_client.search_guides(
            query, limit * 2
        )  # Get more to filter

        # Apply filters
        filtered_guides = []
        for guide in guides:
            if self._guide_matches_filters(guide, filters):
                filtered_guides.append(guide)
                if len(filtered_guides) >= limit:
                    break

        return filtered_guides

    async def _search_offline_guides(
        self, query: str, filters: SearchFilters, limit: int
    ) -> List[Guide]:
        """Search offline database"""
        if not self.offline_db:
            return []

        # This would integrate with the offline database
        # For now, return empty list
        return []

    async def _get_offline_guide(self, guide_id: int) -> Optional[Guide]:
        """Get guide from offline database"""
        if not self.offline_db:
            return None

        # This would get from offline database
        return None

    def _guide_matches_filters(self, guide: Guide, filters: SearchFilters) -> bool:
        """Check if guide matches search filters"""
        if (
            filters.difficulty_level
            and guide.difficulty.lower() != filters.difficulty_level.lower()
        ):
            return False

        if (
            filters.device_type
            and filters.device_type.lower() not in guide.device.lower()
        ):
            return False

        if filters.category and filters.category.lower() not in guide.category.lower():
            return False

        if filters.required_tools:
            guide_tools_lower = [tool.lower() for tool in guide.tools]
            for required_tool in filters.required_tools:
                if not any(required_tool.lower() in tool for tool in guide_tools_lower):
                    return False

        if filters.exclude_tools:
            guide_tools_lower = [tool.lower() for tool in guide.tools]
            for excluded_tool in filters.exclude_tools:
                if any(excluded_tool.lower() in tool for tool in guide_tools_lower):
                    return False

        return True

    def _calculate_confidence_score(
        self, guide: Guide, query: str, filters: SearchFilters
    ) -> float:
        """Calculate confidence score for guide relevance"""
        score = 0.5  # Base score

        query_lower = query.lower()
        title_lower = guide.title.lower()
        device_lower = guide.device.lower()

        # Exact matches boost score
        if query_lower in title_lower:
            score += 0.3

        if filters.device_type and filters.device_type.lower() in device_lower:
            score += 0.2

        # Difficulty match
        if (
            filters.difficulty_level
            and guide.difficulty.lower() == filters.difficulty_level.lower()
        ):
            score += 0.1

        # Popular devices get slight boost
        popular_devices = [
            "iphone",
            "android",
            "switch",
            "macbook",
            "xbox",
            "playstation",
        ]
        if any(device in device_lower for device in popular_devices):
            score += 0.05

        # Quality indicators
        if guide.tools:  # Has tool list
            score += 0.05
        if guide.parts:  # Has parts list
            score += 0.05
        if guide.image_url:  # Has images
            score += 0.05

        return min(score, 1.0)  # Cap at 1.0

    def _explain_difficulty(self, difficulty: str) -> str:
        """Provide explanation for difficulty level"""
        explanations = {
            "easy": "Can be completed by beginners with basic tools. Low risk of damage.",
            "moderate": "Requires some technical knowledge and specialized tools. Moderate risk.",
            "difficult": "Advanced repair requiring significant expertise and specialized equipment. High risk of damage if done incorrectly.",
            "very difficult": "Expert-level repair. Consider professional service unless you have extensive experience.",
        }

        return explanations.get(difficulty.lower(), f"Difficulty level: {difficulty}")

    def _estimate_repair_cost(self, guide: Guide) -> str:
        """Estimate repair cost range"""
        # Simple heuristic based on parts and difficulty
        base_cost = 10

        if guide.difficulty.lower() == "easy":
            base_cost += 20
        elif guide.difficulty.lower() == "moderate":
            base_cost += 50
        elif guide.difficulty.lower() == "difficult":
            base_cost += 100
        else:
            base_cost += 200

        # Add cost for parts (rough estimate)
        parts_cost = len(guide.parts) * 15

        total = base_cost + parts_cost
        return f"${total//2}-${total*2}"  # Range estimate

    def _estimate_success_rate(self, guide: Guide) -> float:
        """Estimate success rate based on difficulty and completeness"""
        base_rate = 0.7

        # Adjust for difficulty
        if guide.difficulty.lower() == "easy":
            base_rate = 0.9
        elif guide.difficulty.lower() == "moderate":
            base_rate = 0.75
        elif guide.difficulty.lower() == "difficult":
            base_rate = 0.6
        else:
            base_rate = 0.4

        # Adjust for completeness
        if guide.tools and guide.parts:
            base_rate += 0.1
        if guide.image_url:
            base_rate += 0.05

        return min(base_rate, 0.95)

    async def _enhance_with_related_guides(self, results: List[RepairGuideResult]):
        """Enhance results with related guides"""
        for result in results:
            try:
                # Find related guides based on device
                if result.guide.device:
                    related_guides = await self.search_guides(
                        result.guide.device, limit=3, use_cache=True
                    )
                    # Filter out the current guide and get top 2
                    related = [
                        r.guide
                        for r in related_guides
                        if r.guide.guideid != result.guide.guideid
                    ][:2]
                    result.related_guides = related
            except Exception as e:
                logger.warning(f"Failed to get related guides: {e}")

    def _create_search_cache_key(
        self, query: str, filters: SearchFilters, limit: int
    ) -> str:
        """Create cache key for search results"""
        filter_str = (
            f"{filters.device_type}_{filters.difficulty_level}_{filters.category}"
        )
        key = f"search_{query}_{filter_str}_{limit}"
        return hashlib.md5(key.encode()).hexdigest()


# Global service instance
_repair_guide_service: Optional[RepairGuideService] = None


def get_repair_guide_service() -> RepairGuideService:
    """Get global repair guide service instance"""
    global _repair_guide_service
    if _repair_guide_service is None:
        _repair_guide_service = RepairGuideService(
            ifixit_api_key=os.getenv("IFIXIT_API_KEY"), redis_url=os.getenv("REDIS_URL")
        )
    return _repair_guide_service


def reset_repair_guide_service():
    """Reset global service instance (for testing)"""
    global _repair_guide_service
    _repair_guide_service = None
