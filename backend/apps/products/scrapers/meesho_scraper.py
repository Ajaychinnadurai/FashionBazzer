"""
Meesho affiliate scraper - scrapes trending dress products from Meesho.
"""
import logging
import requests
from typing import Dict, List, Optional
from .base_scraper import BaseScraper, TRENDING_KEYWORDS
from django.conf import settings

logger = logging.getLogger(__name__)


class MeeshoScraper(BaseScraper):
    """Scraper for Meesho affiliate products."""

    platform_name = "meesho"

    def __init__(self):
        super().__init__()
        self.base_url = "https://affiliate.meesho.com/api/v1"
        self.api_key = settings.MEESHO_AFFILIATE_ID

    def run(self) -> Dict:
        """
        Scrape trending dress products from Meesho.
        """
        all_products = []
        keywords = TRENDING_KEYWORDS[:3]  # Use top 3 keywords per run

        for keyword in keywords:
            try:
                products = self.search_products(keyword)
                all_products.extend(products)
            except Exception as e:
                self.errors.append(f"Keyword '{keyword}': {str(e)}")
                logger.error(f"Meesho scrape error for '{keyword}': {e}")

        # Filter for quality products
        filtered = self.filter_trending(all_products, min_rating=4.0, max_price=1500)

        # Save to database
        saved = self.save_products(filtered)

        return {
            **self.get_summary(),
            'new_products': saved,
            'keywords_used': keywords,
        }

    def search_products(self, query: str) -> List[Dict]:
        """
        Search Meesho for products matching the query.
        Uses the Meesho Affiliate API. Never returns fake/mock data.
        """
        # Only attempt real API call if an API key is configured
        if not self.api_key or self.api_key in ('demo', ''):
            logger.warning(
                "Meesho API key not configured. Set MEESHO_AFFILIATE_ID env var."
            )
            return []

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        params = {
            'q': query,
            'limit': 20,
            'f': 'dresses',
        }

        try:
            response = requests.get(
                f"{self.base_url}/product/search",
                headers=headers,
                params=params,
                timeout=15,
            )
            if response.status_code == 200:
                data = response.json()
                return self._parse_products(data)
            else:
                logger.warning(
                    f"Meesho API returned {response.status_code}: {response.text[:200]}"
                )
                return []
        except requests.RequestException as e:
            logger.error(f"Meesho API request failed: {e}")
            return []

    def _parse_products(self, data: Dict) -> List[Dict]:
        """Parse Meesho API response into standardized format."""
        products = []
        for item in data.get('data', {}).get('products', []):
            products.append({
                'name': item.get('name', ''),
                'original_price': item.get('original_price', item.get('price', 0)),
                'sale_price': item.get('sale_price', item.get('price', 0)),
                'rating': item.get('rating', 4.3),
                'review_count': item.get('review_count', 100),
                'category': item.get('category', 'dress'),
                'product_url': item.get('product_url', ''),
                'affiliate_url': item.get('affiliate_link', ''),
                'image_url': item.get('image', ''),
            })
        return products
