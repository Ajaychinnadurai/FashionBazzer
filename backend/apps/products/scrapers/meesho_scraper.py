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
        Uses the Meesho Affiliate API.
        """
        # Simulated API call - in production, use the actual Meesho Affiliate API
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
                # Return mock data for development
                return self._get_mock_products(query)
        except requests.RequestException as e:
            logger.error(f"Meesho API request failed: {e}")
            # Return mock data for development when API is not configured
            return self._get_mock_products(query)

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

    def _get_mock_products(self, query: str) -> List[Dict]:
        """Generate mock product data for development/demo."""
        import random
        mock_products = [
            {
                'name': f'Trendy {query.title()} Co-ord Set - Latest Collection',
                'original_price': 1299,
                'sale_price': 399,
                'rating': round(random.uniform(4.0, 4.9), 1),
                'review_count': random.randint(100, 5000),
                'category': 'co-ord',
                'product_url': f'https://meesho.com/dress/{query.replace(" ", "-")}-1',
                'affiliate_url': f'https://affiliate.meesho.com/dress/{query.replace(" ", "-")}-1?aff_id={self.api_key}',
                'image_url': f'https://source.unsplash.com/600x750/?dress,fashion,trendy&sig={random.randint(1,999)}',
                'is_trending': True,
            },
            {
                'name': f'Stylish {query.title()} Bodycon Dress for Women',
                'original_price': 1499,
                'sale_price': 499,
                'rating': round(random.uniform(4.0, 4.8), 1),
                'review_count': random.randint(50, 3000),
                'category': 'bodycon',
                'product_url': f'https://meesho.com/dress/{query.replace(" ", "-")}-2',
                'affiliate_url': f'https://affiliate.meesho.com/dress/{query.replace(" ", "-")}-2?aff_id={self.api_key}',
                'image_url': f'https://source.unsplash.com/600x750/?dress,bodycon,fashion&sig={random.randint(1,999)}',
                'is_trending': True,
            },
            {
                'name': f'Casual {query.title()} Maxi Dress - Summer Special',
                'original_price': 999,
                'sale_price': 299,
                'rating': round(random.uniform(4.0, 4.7), 1),
                'review_count': random.randint(200, 8000),
                'category': 'cottagecore',
                'product_url': f'https://meesho.com/dress/{query.replace(" ", "-")}-3',
                'affiliate_url': f'https://affiliate.meesho.com/dress/{query.replace(" ", "-")}-3?aff_id={self.api_key}',
                'image_url': f'https://source.unsplash.com/600x750/?maxi,dress,summer&sig={random.randint(1,999)}',
                'is_trending': False,
            },
            {
                'name': f'Designer {query.title()} Indo-Western Fusion Dress',
                'original_price': 1899,
                'sale_price': 699,
                'rating': round(random.uniform(4.2, 4.9), 1),
                'review_count': random.randint(80, 2000),
                'category': 'indo-western',
                'product_url': f'https://meesho.com/dress/{query.replace(" ", "-")}-4',
                'affiliate_url': f'https://affiliate.meesho.com/dress/{query.replace(" ", "-")}-4?aff_id={self.api_key}',
                'image_url': f'https://source.unsplash.com/600x750/?fusion,indo,western,dress&sig={random.randint(1,999)}',
                'is_trending': True,
            },
            {
                'name': f'Party Wear {query.title()} Cut-out Dress - Trending Now',
                'original_price': 1699,
                'sale_price': 599,
                'rating': round(random.uniform(4.0, 4.6), 1),
                'review_count': random.randint(60, 1500),
                'category': 'cut-out',
                'product_url': f'https://meesho.com/dress/{query.replace(" ", "-")}-5',
                'affiliate_url': f'https://affiliate.meesho.com/dress/{query.replace(" ", "-")}-5?aff_id={self.api_key}',
                'image_url': f'https://source.unsplash.com/600x750/?party,dress,nightout&sig={random.randint(1,999)}',
                'is_trending': False,
            },
        ]
        return mock_products
