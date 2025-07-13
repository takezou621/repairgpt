"""
iFixit API Client for RepairGPT
Implements Issue #8: iFixit APIクライアントの基本実装
"""

import requests
import json
from typing import Dict, List, Optional, Union
import logging
from dataclasses import dataclass
from urllib.parse import urljoin, quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class IFixitClient:
    """Client for accessing iFixit API"""
    
    BASE_URL = "https://www.ifixit.com/api/2.0"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize iFixit API client
        
        Args:
            api_key: Optional API key for authenticated requests
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RepairGPT/1.0 (AI-powered repair assistant)',
            'Accept': 'application/json'
        })
        
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
    
    def get_guide(self, guide_id: int) -> Optional[Guide]:
        """
        Get a specific repair guide by ID
        
        Args:
            guide_id: The iFixit guide ID
            
        Returns:
            Guide object or None if not found
        """
        try:
            url = f"{self.BASE_URL}/guides/{guide_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_guide(data)
            
        except requests.RequestException as e:
            logger.error(f"Error fetching guide {guide_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing guide {guide_id}: {e}")
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
        try:
            # Try the guides endpoint with search parameters first
            params = {'q': query, 'limit': limit}
            url = f"{self.BASE_URL}/guides"
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            guides = []
            
            # Handle both list and dict responses
            guides_data = data if isinstance(data, list) else data.get('results', data)
            
            for guide_data in guides_data:
                guide = self._parse_guide(guide_data)
                if guide and query.lower() in guide.title.lower():
                    guides.append(guide)
            
            return guides[:limit]
            
        except requests.RequestException as e:
            logger.error(f"Error searching guides for '{query}': {e}")
            # Fallback to getting all guides and filtering
            return self._fallback_search(query, limit)
        except Exception as e:
            logger.error(f"Unexpected error searching guides for '{query}': {e}")
            return self._fallback_search(query, limit)
    
    def _fallback_search(self, query: str, limit: int = 10) -> List[Guide]:
        """Fallback search method when API search fails"""
        try:
            # Get recent guides and filter locally
            url = f"{self.BASE_URL}/guides"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            guides = []
            
            guides_data = data if isinstance(data, list) else data.get('results', data)
            
            for guide_data in guides_data:
                guide = self._parse_guide(guide_data)
                if guide and query.lower() in guide.title.lower():
                    guides.append(guide)
                    if len(guides) >= limit:
                        break
            
            return guides
            
        except Exception as e:
            logger.error(f"Fallback search also failed: {e}")
            return []
    
    def get_categories(self) -> List[Dict]:
        """
        Get available device categories
        
        Returns:
            List of category dictionaries
        """
        try:
            url = f"{self.BASE_URL}/categories"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching categories: {e}")
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
        try:
            url = f"{self.BASE_URL}/guides/trending"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            guides = []
            
            for guide_data in data.get('guides', []):
                guide = self._parse_guide(guide_data)
                if guide:
                    guides.append(guide)
            
            return guides[:limit]
            
        except requests.RequestException as e:
            logger.error(f"Error fetching trending guides: {e}")
            # Fallback to popular searches
            return self.search_guides("popular repair", limit)
    
    def _parse_guide(self, data: Dict) -> Optional[Guide]:
        """Parse raw guide data into Guide object"""
        try:
            return Guide(
                guideid=data.get('guideid', 0),
                title=data.get('title', ''),
                url=data.get('url', ''),
                summary=data.get('summary', ''),
                difficulty=data.get('difficulty', 'Unknown'),
                tools=[tool.get('text', '') for tool in data.get('tools', [])],
                parts=[part.get('text', '') for part in data.get('parts', [])],
                category=data.get('category', ''),
                device=data.get('subject', ''),
                time_required=data.get('time_required'),
                image_url=data.get('image', {}).get('standard') if data.get('image') else None
            )
        except Exception as e:
            logger.error(f"Error parsing guide data: {e}")
            return None
    
    def _parse_search_result(self, result: Dict) -> Optional[Guide]:
        """Parse search result into Guide object"""
        try:
            return Guide(
                guideid=result.get('guideid', 0),
                title=result.get('title', ''),
                url=result.get('url', ''),
                summary=result.get('summary', ''),
                difficulty=result.get('difficulty', 'Unknown'),
                tools=[],  # Tools not available in search results
                parts=[],  # Parts not available in search results
                category=result.get('category', ''),
                device=result.get('subject', ''),
                image_url=result.get('image', {}).get('thumbnail') if result.get('image') else None
            )
        except Exception as e:
            logger.error(f"Error parsing search result: {e}")
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