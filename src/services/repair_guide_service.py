"""Repair Guide Service - Integrates iFixit API with RepairGPT"""

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

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
    from ..utils.japanese_device_mapper import JapaneseDeviceMapper, get_mapper
except ImportError:
    # Fallback for direct execution
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from clients.ifixit_client import Guide, IFixitClient
    from data.offline_repair_database import OfflineRepairDatabase
    from utils.logger import get_logger
    from utils.japanese_device_mapper import JapaneseDeviceMapper, get_mapper

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


# Japanese difficulty level mappings (moved outside dataclass)
JAPANESE_DIFFICULTY_MAPPINGS: Dict[str, str] = {
    "初心者": "beginner",
    "しょしんしゃ": "beginner",
    "はじめて": "beginner",
    "簡単": "easy",
    "かんたん": "easy",
    "やさしい": "easy",
    "易しい": "easy",
    "中級者": "intermediate",
    "ちゅうきゅうしゃ": "intermediate",
    "中級": "intermediate",
    "ちゅうきゅう": "intermediate",
    "普通": "moderate",
    "ふつう": "moderate",
    "上級者": "expert",
    "じょうきゅうしゃ": "expert",
    "上級": "expert",
    "じょうきゅう": "expert",
    "難しい": "difficult",
    "むずかしい": "difficult",
    "困難": "difficult",
    "こんなん": "difficult",
    "高度": "very difficult",
    "こうど": "very difficult",
    "専門": "very difficult",
    "せんもん": "very difficult",
    "プロ": "very difficult",
    "ぷろ": "very difficult",
}

# Japanese category mappings (moved outside dataclass)
JAPANESE_CATEGORY_MAPPINGS: Dict[str, str] = {
    "画面修理": "screen repair",
    "がめんしゅうり": "screen repair",
    "液晶修理": "screen repair",
    "えきしょうしゅうり": "screen repair",
    "タッチパネル": "touchscreen repair",
    "たっちぱねる": "touchscreen repair",
    "バッテリー交換": "battery replacement",
    "ばってりーこうかん": "battery replacement",
    "電池交換": "battery replacement",
    "でんちこうかん": "battery replacement",
    "基板修理": "motherboard repair",
    "きばんしゅうり": "motherboard repair",
    "マザーボード": "motherboard repair",
    "まざーぼーど": "motherboard repair",
    "充電器修理": "charger repair",
    "じゅうでんきしゅうり": "charger repair",
    "充電ポート": "charging port repair",
    "じゅうでんぽーと": "charging port repair",
    "ボタン修理": "button repair",
    "ぼたんしゅうり": "button repair",
    "スピーカー修理": "speaker repair",
    "すぴーかーしゅうり": "speaker repair",
    "カメラ修理": "camera repair",
    "かめらしゅうり": "camera repair",
    "キーボード修理": "keyboard repair",
    "きーぼーどしゅうり": "keyboard repair",
    "トラックパッド": "trackpad repair",
    "とらっくぱっど": "trackpad repair",
    "冷却ファン": "cooling fan repair",
    "れいきゃくふぁん": "cooling fan repair",
    "排熱": "thermal management",
    "はいねつ": "thermal management",
    "水没修理": "water damage repair",
    "すいぼつしゅうり": "water damage repair",
    "コネクタ修理": "connector repair",
    "こねくたしゅうり": "connector repair",
}


@dataclass
class SearchFilters:
    """Search filters for repair guides with Japanese support"""

    device_type: Optional[str] = None
    difficulty_level: Optional[str] = None  # Easy, Moderate, Difficult
    max_time: Optional[str] = None  # "30 minutes", "1 hour", etc.
    required_tools: Optional[List[str]] = None
    exclude_tools: Optional[List[str]] = None
    category: Optional[str] = None
    language: str = "en"
    include_community_guides: bool = True
    min_rating: Optional[float] = None
    
    def normalize_japanese_difficulty(self, difficulty: str) -> str:
        """
        Normalize Japanese difficulty level to English equivalent.
        
        Args:
            difficulty: Japanese difficulty level string
            
        Returns:
            English difficulty level string or original if no mapping found
        """
        if not difficulty:
            return difficulty
            
        # Normalize input for matching
        normalized = difficulty.lower().strip()
        
        # Direct mapping lookup
        if normalized in JAPANESE_DIFFICULTY_MAPPINGS:
            return JAPANESE_DIFFICULTY_MAPPINGS[normalized]
            
        # If no mapping found, return original
        return difficulty
    
    def normalize_japanese_category(self, category: str) -> str:
        """
        Normalize Japanese category name to English equivalent.
        
        Args:
            category: Japanese category name string
            
        Returns:
            English category name string or original if no mapping found
        """
        if not category:
            return category
            
        # Normalize input for matching
        normalized = category.lower().strip()
        
        # Direct mapping lookup
        if normalized in JAPANESE_CATEGORY_MAPPINGS:
            return JAPANESE_CATEGORY_MAPPINGS[normalized]
            
        # Check for partial matches in category names
        for japanese_term, english_term in JAPANESE_CATEGORY_MAPPINGS.items():
            # Direct containment check
            if japanese_term in normalized:
                return english_term
            
            # More flexible matching: check if key components are present
            # Split the mapping term into key components
            if len(japanese_term) >= 3:
                # For terms like "画面修理", check if both "画面" and "修理" are present
                # This handles cases like "画面の修理" -> "画面修理"
                key_parts = []
                if "修理" in japanese_term:
                    key_parts.append("修理")
                    remaining = japanese_term.replace("修理", "")
                    if remaining:
                        key_parts.append(remaining)
                elif "交換" in japanese_term:
                    key_parts.append("交換")
                    remaining = japanese_term.replace("交換", "")
                    if remaining:
                        key_parts.append(remaining)
                
                # Check if all key parts are present
                if key_parts and all(part in normalized for part in key_parts if part):
                    return english_term
                
        # If no mapping found, return original
        return category


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
                self.redis_client = redis.from_url(redis_url or os.getenv("REDIS_URL"), decode_responses=True)
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
            sorted_items = sorted(self.memory_cache.items(), key=lambda x: x[1]["timestamp"])
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
        enable_japanese_support: bool = True,
    ):
        self.ifixit_client = IFixitClient(api_key=ifixit_api_key)
        self.cache_manager = CacheManager(redis_url)
        self.rate_limiter = RateLimiter(max_calls=100, time_window=3600)  # 100 calls/hour
        self.offline_db = OfflineRepairDatabase() if enable_offline_fallback else None
        self.japanese_mapper = get_mapper() if enable_japanese_support else None

        logger.info(
            "RepairGuideService initialized",
            has_ifixit_key=bool(ifixit_api_key),
            has_cache=bool(self.cache_manager.redis_client),
            has_offline_db=bool(self.offline_db),
            has_japanese_support=bool(self.japanese_mapper),
        )

    async def search_guides(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 10,
        use_cache: bool = True,
    ) -> List[RepairGuideResult]:
        """Search for repair guides with enhanced features and Japanese support"""
        if not filters:
            filters = SearchFilters()

        # Preprocess Japanese query if Japanese support is enabled
        original_query = query
        query = self._preprocess_japanese_query(query)

        # Create cache key using preprocessed query
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
                        confidence_score=self._calculate_confidence_score(guide, query, filters),
                        last_updated=datetime.now(),
                        difficulty_explanation=self._explain_difficulty(guide.difficulty),
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
                offline_guides = await self._search_offline_guides(query, filters, limit - len(results))

                for guide in offline_guides:
                    result = RepairGuideResult(
                        guide=guide,
                        source="offline",
                        confidence_score=self._calculate_confidence_score(guide, query, filters)
                        * 0.8,  # Lower confidence for offline
                        last_updated=datetime.now() - timedelta(days=30),  # Assume offline data is older
                        difficulty_explanation=self._explain_difficulty(guide.difficulty),
                    )
                    results.append(result)

                logger.info(f"Retrieved {len(offline_guides)} guides from offline database")

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
                        difficulty_explanation=self._explain_difficulty(guide.difficulty),
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
                    search_results = await self.search_guides(query, limit=2, use_cache=True)
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
            "rate_limit_calls_remaining": self.rate_limiter.max_calls - len(self.rate_limiter.calls),
            "rate_limit_reset_in": self.rate_limiter.time_until_next_request(),
        }

        if self.cache_manager.redis_client:
            try:
                info = self.cache_manager.redis_client.info("memory")
                stats["redis_memory_usage"] = info.get("used_memory_human", "unknown")
            except Exception:
                pass

        return stats

    async def _search_ifixit_guides(self, query: str, filters: SearchFilters, limit: int) -> List[Guide]:
        """Search iFixit API with filters"""
        # For now, use basic search - can be enhanced with filter application
        guides = self.ifixit_client.search_guides(query, limit * 2)  # Get more to filter

        # Apply filters
        filtered_guides = []
        for guide in guides:
            if self._guide_matches_filters(guide, filters):
                filtered_guides.append(guide)
                if len(filtered_guides) >= limit:
                    break

        return filtered_guides

    async def _search_offline_guides(self, query: str, filters: SearchFilters, limit: int) -> List[Guide]:
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
        """Check if guide matches search filters with Japanese support"""
        # Enhanced difficulty matching with Japanese normalization
        if filters.difficulty_level:
            normalized_difficulty = filters.normalize_japanese_difficulty(filters.difficulty_level)
            
            # Check for exact match first
            if guide.difficulty.lower() == normalized_difficulty.lower():
                pass  # Match found
            # Check for similar difficulty levels
            elif not self._is_similar_difficulty(guide.difficulty, normalized_difficulty):
                return False

        # Enhanced device type matching
        if filters.device_type:
            device_lower = guide.device.lower()
            filter_device_lower = filters.device_type.lower()
            
            # Direct match
            if filter_device_lower not in device_lower:
                # Try Japanese device mapping if available
                if self.japanese_mapper:
                    try:
                        # Check if filter device type is Japanese and can be mapped
                        mapped_device = self.japanese_mapper.map_device_name(filters.device_type)
                        if mapped_device and mapped_device.lower() in device_lower:
                            pass  # Match found through Japanese mapping
                        else:
                            return False
                    except Exception as e:
                        logger.debug(f"Error in Japanese device matching: {e}")
                        return False
                else:
                    return False

        # Enhanced category matching with Japanese normalization
        if filters.category:
            normalized_category = filters.normalize_japanese_category(filters.category)
            guide_category_lower = guide.category.lower()
            
            # Check if normalized category matches
            if normalized_category.lower() not in guide_category_lower:
                # Also check original category in case normalization wasn't needed
                if filters.category.lower() not in guide_category_lower:
                    return False

        # Tool filtering (unchanged but enhanced error handling)
        if filters.required_tools:
            guide_tools_lower = [tool.lower() for tool in guide.tools] if guide.tools else []
            for required_tool in filters.required_tools:
                # Normalize Japanese tool names if needed
                normalized_tool = self._normalize_japanese_tool_name(required_tool)
                
                if not any(normalized_tool.lower() in tool for tool in guide_tools_lower):
                    # Also try original tool name
                    if not any(required_tool.lower() in tool for tool in guide_tools_lower):
                        return False

        if filters.exclude_tools:
            guide_tools_lower = [tool.lower() for tool in guide.tools] if guide.tools else []
            for excluded_tool in filters.exclude_tools:
                # Normalize Japanese tool names if needed
                normalized_tool = self._normalize_japanese_tool_name(excluded_tool)
                
                if any(normalized_tool.lower() in tool for tool in guide_tools_lower):
                    return False
                # Also check original tool name
                if any(excluded_tool.lower() in tool for tool in guide_tools_lower):
                    return False

        return True
    
    def _normalize_japanese_tool_name(self, tool_name: str) -> str:
        """
        Normalize Japanese tool names to English equivalents.
        
        Args:
            tool_name: Tool name that may be in Japanese
            
        Returns:
            Normalized tool name
        """
        if not tool_name:
            return tool_name
            
        # Basic Japanese tool mappings
        tool_mappings = {
            "ドライバー": "screwdriver",
            "どらいばー": "screwdriver",
            "ネジ回し": "screwdriver",
            "ねじまわし": "screwdriver",
            "プラスドライバー": "phillips screwdriver",
            "ぷらすどらいばー": "phillips screwdriver",
            "ピンセット": "tweezers",
            "ぴんせっと": "tweezers",
            "スパチュラ": "spudger",
            "すぱちゅら": "spudger",
            "オープニングツール": "opening tool",
            "おーぷにんぐつーる": "opening tool",
            "サクションカップ": "suction cup",
            "さくしょんかっぷ": "suction cup",
            "ヒートガン": "heat gun",
            "ひーとがん": "heat gun",
            "はんだこて": "soldering iron",
            "ハンダゴテ": "soldering iron",
        }
        
        normalized = tool_name.lower().strip()
        return tool_mappings.get(normalized, tool_name)

    def _calculate_confidence_score(self, guide: Guide, query: str, filters: SearchFilters) -> float:
        """Calculate confidence score for guide relevance with Japanese optimization"""
        score = 0.5  # Base score

        query_lower = query.lower()
        title_lower = guide.title.lower()
        device_lower = guide.device.lower()
        
        # Track if this was a Japanese search for special scoring
        is_japanese_search = self._is_japanese_query(query)
        japanese_mapping_quality = 1.0  # Default quality

        # Exact matches boost score
        if query_lower in title_lower:
            score += 0.3
            if is_japanese_search:
                # Slightly higher boost for exact matches in Japanese searches
                score += 0.05

        if filters.device_type and filters.device_type.lower() in device_lower:
            score += 0.2

        # Enhanced difficulty matching with Japanese support
        if filters.difficulty_level:
            # Normalize Japanese difficulty if needed
            normalized_difficulty = filters.normalize_japanese_difficulty(filters.difficulty_level)
            
            # Check for exact match
            if guide.difficulty.lower() == normalized_difficulty.lower():
                score += 0.1
                if is_japanese_search:
                    # Bonus for successful Japanese difficulty mapping
                    score += 0.05
            
            # Check for approximate difficulty matches
            elif self._is_similar_difficulty(guide.difficulty, normalized_difficulty):
                score += 0.05

        # Enhanced category matching with Japanese support
        if filters.category:
            # Normalize Japanese category if needed
            normalized_category = filters.normalize_japanese_category(filters.category)
            
            # Check if guide category matches normalized category
            if normalized_category.lower() in guide.category.lower():
                score += 0.15
                if is_japanese_search:
                    # Bonus for successful Japanese category mapping
                    score += 0.05

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

        # Japanese device mapping quality adjustment
        if is_japanese_search and self.japanese_mapper:
            try:
                # Check if original query contained devices that were mapped
                original_words = query.split()
                mapped_count = 0
                total_device_words = 0
                
                for word in original_words:
                    if self.japanese_mapper.is_device_name(word):
                        total_device_words += 1
                        if self.japanese_mapper.map_device_name(word):
                            mapped_count += 1
                
                if total_device_words > 0:
                    japanese_mapping_quality = mapped_count / total_device_words
                    # Adjust score based on mapping quality
                    score += 0.1 * japanese_mapping_quality
                    
            except Exception as e:
                logger.debug(f"Error calculating Japanese mapping quality: {e}")

        # Quality indicators
        if guide.tools:  # Has tool list
            score += 0.05
        if guide.parts:  # Has parts list
            score += 0.05
        if guide.image_url:  # Has images
            score += 0.05

        # Japanese search confidence adjustment
        if is_japanese_search:
            # Apply mapping quality factor to final score
            score = score * (0.8 + 0.2 * japanese_mapping_quality)
            
            # Ensure Japanese searches don't get unfairly penalized
            score = max(score, 0.4)  # Minimum score for Japanese searches

        return min(score, 1.0)  # Cap at 1.0
    
    def _is_japanese_query(self, query: str) -> bool:
        """
        Check if query contains Japanese characters.
        
        Args:
            query: Search query to check
            
        Returns:
            True if query contains Japanese characters
        """
        if not query:
            return False
            
        # Check for Japanese character ranges
        japanese_ranges = [
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x4E00, 0x9FAF),  # CJK Unified Ideographs (Kanji)
            (0xFF66, 0xFF9D),  # Half-width Katakana
        ]
        
        for char in query:
            char_code = ord(char)
            for start, end in japanese_ranges:
                if start <= char_code <= end:
                    return True
                    
        return False
    
    def _is_similar_difficulty(self, guide_difficulty: str, target_difficulty: str) -> bool:
        """
        Check if two difficulty levels are similar.
        
        Args:
            guide_difficulty: Guide's difficulty level
            target_difficulty: Target difficulty level
            
        Returns:
            True if difficulty levels are similar
        """
        # Define difficulty similarity groups
        difficulty_groups = [
            ["easy", "beginner"],
            ["moderate", "intermediate"],
            ["difficult", "expert", "very difficult"],
        ]
        
        guide_lower = guide_difficulty.lower()
        target_lower = target_difficulty.lower()
        
        # Check if both difficulties are in the same group
        for group in difficulty_groups:
            if guide_lower in group and target_lower in group:
                return True
                
        return False

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
                    related_guides = await self.search_guides(result.guide.device, limit=3, use_cache=True)
                    # Filter out the current guide and get top 2
                    related = [r.guide for r in related_guides if r.guide.guideid != result.guide.guideid][:2]
                    result.related_guides = related
            except Exception as e:
                logger.warning(f"Failed to get related guides: {e}")

    def _preprocess_japanese_query(self, query: str) -> str:
        """
        Preprocess Japanese query to improve search results.
        
        This method analyzes the query for Japanese device names and converts them
        to their English equivalents for better iFixit API compatibility.
        
        Args:
            query: Search query that may contain Japanese text
            
        Returns:
            Preprocessed query with Japanese device names converted to English
            
        Raises:
            Exception: If Japanese processing fails, returns original query
        """
        if not self.japanese_mapper or not query:
            return query
            
        logger.debug(f"Preprocessing Japanese query: {query}")
        
        try:
            # Split query into words for processing
            import re
            words = re.split(r'[\s\u3000]+', query.strip())  # Split on spaces and full-width spaces
            processed_words = []
            
            for word in words:
                if not word:
                    continue
                    
                # Try direct device mapping first
                english_device = self.japanese_mapper.map_device_name(word)
                if english_device:
                    processed_words.append(english_device)
                    logger.debug(f"Direct mapping: '{word}' -> '{english_device}'")
                    continue
                
                # Try fuzzy matching for partial matches
                fuzzy_result = self.japanese_mapper.find_best_match(word, threshold=0.7)
                if fuzzy_result:
                    device_name, confidence = fuzzy_result
                    processed_words.append(device_name)
                    logger.debug(f"Fuzzy mapping: '{word}' -> '{device_name}' (confidence: {confidence:.3f})")
                    continue
                
                # If no device mapping found, keep original word
                processed_words.append(word)
            
            # Join processed words back into query
            processed_query = " ".join(processed_words)
            
            if processed_query != query:
                logger.info(f"Japanese query preprocessed: '{query}' -> '{processed_query}'")
            
            return processed_query
            
        except Exception as e:
            logger.warning(f"Japanese query preprocessing failed: {e}")
            # Return original query if preprocessing fails
            return query
    
    def _create_search_cache_key(self, query: str, filters: SearchFilters, limit: int) -> str:
        """Create cache key for search results"""
        filter_str = f"{filters.device_type}_{filters.difficulty_level}_{filters.category}"
        key = f"search_{query}_{filter_str}_{limit}"
        return hashlib.md5(key.encode()).hexdigest()


# Global service instance
_repair_guide_service: Optional[RepairGuideService] = None


def get_repair_guide_service() -> RepairGuideService:
    """Get global repair guide service instance"""
    global _repair_guide_service
    if _repair_guide_service is None:
        _repair_guide_service = RepairGuideService(
            ifixit_api_key=os.getenv("IFIXIT_API_KEY"), 
            redis_url=os.getenv("REDIS_URL"),
            enable_japanese_support=True,
        )
    return _repair_guide_service


def reset_repair_guide_service():
    """Reset global service instance (for testing)"""
    global _repair_guide_service
    _repair_guide_service = None
