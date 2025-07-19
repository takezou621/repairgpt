"""
iFixit API Client for RepairGPT
Implements Issue #8: iFixit APIクライアントの基本実装
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from urllib.parse import quote, urljoin

import requests

from utils.logger import (LoggerMixin, get_logger, log_api_call, log_api_error,
                          log_performance)

# Get logger instance
logger = get_logger(__name__)


@dataclass
class Guide:
    """iFixit repair guide data structure"""

    guideid: int
    title: str
    url: str
    summary: str
    difficulty: str
    tools: List[str]
    parts: List[str]
    category: str
    device: str
    time_required: Optional[str] = None
    image_url: Optional[str] = None


class IFixitClient(LoggerMixin):
    """Client for accessing iFixit API"""

    BASE_URL = "https://www.ifixit.com/api/2.0"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize iFixit API client

        Args:
            api_key: Optional API key for authenticated requests
        """
        self.log_info("Initializing iFixit API client", has_api_key=bool(api_key))

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "RepairGPT/1.0 (AI-powered repair assistant)",
                "Accept": "application/json",
            }
        )

        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
            self.log_info("API key configured for authenticated requests")

        self.log_info("iFixit API client initialized successfully")

    def get_guide(self, guide_id: int) -> Optional[Guide]:
        """
        Get a specific repair guide by ID

        Args:
            guide_id: The iFixit guide ID

        Returns:
            Guide object or None if not found
        """
        start_time = time.time()

        # Log API call
        log_api_call(self.logger, f"guides/{guide_id}", "GET", guide_id=guide_id)

        try:
            url = f"{self.BASE_URL}/guides/{guide_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            guide = self._parse_guide(data)

            # Log successful completion
            duration = time.time() - start_time
            log_performance(
                self.logger,
                "get_guide",
                duration,
                guide_id=guide_id,
                found=guide is not None,
            )

            self.log_info(
                "Successfully retrieved guide",
                guide_id=guide_id,
                title=guide.title if guide else None,
            )

            return guide

        except requests.RequestException as e:
            # Log API error
            log_api_error(self.logger, f"guides/{guide_id}", e, guide_id=guide_id)
            return None
        except Exception as e:
            # Log unexpected error
            self.log_error(e, "get_guide_parsing_error", guide_id=guide_id)
            return None

    def search_guides(self, query: str, limit: int = 10) -> List[Guide]:
        """
        Search for guides by query

        Args:
            query: Search query (device name, issue, etc.)
            limit: Maximum number of results to return

        Returns:
            List of Guide objects
        """
        start_time = time.time()

        # Log search request
        log_api_call(self.logger, "guides/search", "GET", query=query, limit=limit)

        try:
            # Try the guides endpoint with search parameters first
            params = {"q": query, "limit": limit}
            url = f"{self.BASE_URL}/guides"

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            guides = []

            # Handle both list and dict responses
            guides_data = data if isinstance(data, list) else data.get("results", data)

            for guide_data in guides_data:
                guide = self._parse_guide(guide_data)
                if guide and query.lower() in guide.title.lower():
                    guides.append(guide)

            result_guides = guides[:limit]

            # Log successful search
            duration = time.time() - start_time
            log_performance(
                self.logger,
                "search_guides",
                duration,
                query=query,
                results_found=len(result_guides),
                limit=limit,
            )

            self.log_info(
                "Guide search completed", query=query, results_count=len(result_guides)
            )

            return result_guides

        except requests.RequestException as e:
            # Log API error and try fallback
            log_api_error(self.logger, "guides/search", e, query=query, limit=limit)
            self.log_warning(
                "Primary search failed, trying fallback method", query=query
            )
            return self._fallback_search(query, limit)
        except Exception as e:
            # Log unexpected error and try fallback
            self.log_error(e, "search_guides_error", query=query, limit=limit)
            return self._fallback_search(query, limit)

    def _fallback_search(self, query: str, limit: int = 10) -> List[Guide]:
        """Fallback search method when API search fails"""
        start_time = time.time()

        self.log_info("Starting fallback search", query=query, limit=limit)

        try:
            # Get recent guides and filter locally
            url = f"{self.BASE_URL}/guides"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            guides = []

            guides_data = data if isinstance(data, list) else data.get("results", data)

            for guide_data in guides_data:
                guide = self._parse_guide(guide_data)
                if guide and query.lower() in guide.title.lower():
                    guides.append(guide)
                    if len(guides) >= limit:
                        break

            # Log fallback completion
            duration = time.time() - start_time
            log_performance(
                self.logger,
                "fallback_search",
                duration,
                query=query,
                results_found=len(guides),
            )

            self.log_info(
                "Fallback search completed", query=query, results_count=len(guides)
            )

            return guides

        except Exception as e:
            self.log_error(e, "fallback_search_failed", query=query, limit=limit)
            return []

    def get_categories(self) -> List[Dict]:
        """
        Get available device categories

        Returns:
            List of category dictionaries
        """
        start_time = time.time()

        # Log API call
        log_api_call(self.logger, "categories", "GET")

        try:
            url = f"{self.BASE_URL}/categories"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            categories = response.json()

            # Log successful completion
            duration = time.time() - start_time
            log_performance(
                self.logger,
                "get_categories",
                duration,
                categories_count=len(categories),
            )

            self.log_info("Successfully retrieved categories", count=len(categories))

            return categories

        except requests.RequestException as e:
            log_api_error(self.logger, "categories", e)
            return []

    def get_guides_by_device(self, device_name: str, limit: int = 10) -> List[Guide]:
        """
        Get repair guides for a specific device

        Args:
            device_name: Name of the device (e.g., "iPhone 12", "Nintendo Switch")
            limit: Maximum number of guides to return

        Returns:
            List of Guide objects for the device
        """
        return self.search_guides(f"device:{device_name}", limit)

    def get_trending_guides(self, limit: int = 10) -> List[Guide]:
        """
        Get trending/popular repair guides

        Args:
            limit: Maximum number of guides to return

        Returns:
            List of trending Guide objects
        """
        start_time = time.time()

        # Log API call
        log_api_call(self.logger, "guides/trending", "GET", limit=limit)

        try:
            url = f"{self.BASE_URL}/guides/trending"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            guides = []

            for guide_data in data.get("guides", []):
                guide = self._parse_guide(guide_data)
                if guide:
                    guides.append(guide)

            result_guides = guides[:limit]

            # Log successful completion
            duration = time.time() - start_time
            log_performance(
                self.logger,
                "get_trending_guides",
                duration,
                guides_found=len(result_guides),
                limit=limit,
            )

            self.log_info(
                "Successfully retrieved trending guides", count=len(result_guides)
            )

            return result_guides

        except requests.RequestException as e:
            log_api_error(self.logger, "guides/trending", e, limit=limit)
            self.log_warning("Trending guides failed, falling back to popular search")
            # Fallback to popular searches
            return self.search_guides("popular repair", limit)

    def _parse_guide(self, data: Dict) -> Optional[Guide]:
        """Parse raw guide data into Guide object"""
        try:
            guide = Guide(
                guideid=data.get("guideid", 0),
                title=data.get("title", ""),
                url=data.get("url", ""),
                summary=data.get("summary", ""),
                difficulty=data.get("difficulty", "Unknown"),
                tools=[tool.get("text", "") for tool in data.get("tools", [])],
                parts=[part.get("text", "") for part in data.get("parts", [])],
                category=data.get("category", ""),
                device=data.get("subject", ""),
                time_required=data.get("time_required"),
                image_url=(
                    data.get("image", {}).get("standard") if data.get("image") else None
                ),
            )

            self.logger.debug(
                "Successfully parsed guide",
                extra={
                    "extra_data": {
                        "guide_id": guide.guideid,
                        "title": guide.title,
                        "difficulty": guide.difficulty,
                        "tools_count": len(guide.tools),
                        "parts_count": len(guide.parts),
                    }
                },
            )

            return guide

        except Exception as e:
            self.log_error(
                e,
                "guide_parsing_error",
                guide_id=data.get("guideid", "unknown"),
                title=data.get("title", "unknown"),
            )
            return None

    def _parse_search_result(self, result: Dict) -> Optional[Guide]:
        """Parse search result into Guide object"""
        try:
            guide = Guide(
                guideid=result.get("guideid", 0),
                title=result.get("title", ""),
                url=result.get("url", ""),
                summary=result.get("summary", ""),
                difficulty=result.get("difficulty", "Unknown"),
                tools=[],  # Tools not available in search results
                parts=[],  # Parts not available in search results
                category=result.get("category", ""),
                device=result.get("subject", ""),
                image_url=(
                    result.get("image", {}).get("thumbnail")
                    if result.get("image")
                    else None
                ),
            )

            self.logger.debug(
                "Successfully parsed search result",
                extra={
                    "extra_data": {
                        "guide_id": guide.guideid,
                        "title": guide.title,
                        "difficulty": guide.difficulty,
                    }
                },
            )

            return guide

        except Exception as e:
            self.log_error(
                e,
                "search_result_parsing_error",
                guide_id=result.get("guideid", "unknown"),
                title=result.get("title", "unknown"),
            )
            return None


# Example usage and testing
if __name__ == "__main__":
    # Initialize client
    client = IFixitClient()

    # Test search functionality
    print("Testing iFixit API Client...")

    # Search for Nintendo Switch repairs
    print("\n1. Searching for Nintendo Switch repairs...")
    switch_guides = client.search_guides("Nintendo Switch", limit=3)
    for guide in switch_guides:
        print(f"  - {guide.title} ({guide.difficulty})")

    # Search for iPhone repairs
    print("\n2. Searching for iPhone repairs...")
    iphone_guides = client.search_guides("iPhone screen replacement", limit=3)
    for guide in iphone_guides:
        print(f"  - {guide.title} ({guide.difficulty})")

    # Get categories
    print("\n3. Getting device categories...")
    categories = client.get_categories()
    print(f"  Found {len(categories)} categories")

    print("\niFixit API Client test completed!")
