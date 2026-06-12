"""
Flipkart affiliate scraper for FashionBazzer.
"""
import logging
import random
from typing import Dict, List
from .base_scraper import BaseScraper
from django.conf import settings

logger = logging.getLogger(__name__)


class FlipkartScraper(BaseScraper):
    """Scraper for Flipkart affiliate products."""

    platform_name = "flipkart"

    def __init__(self):
        super().__init__()
        self.affiliate_id = getattr(settings, 'FLIPKART_AFFILIATE_ID', 'demo')

    def run(self) -> Dict:
        """
        Scrape trending dress products from Flipkart.
        """
        all_products = []
        keywords = ["trendy dress", "women fashion", "party wear"]

        for keyword in keywords:
            try:
                products = self.search_products(keyword)
                all_products.extend(products)
            except Exception as e:
                self.errors.append(f"Keyword '{keyword}': {str(e)}")
                logger.error(f"Flipkart scrape error: {e}")

        filtered = self.filter_trending(all_products, min_rating=4.0, max_price=1500)
        saved = self.save_products(filtered)

        return {
            **self.get_summary(),
            'new_products': saved,
        }

    def search_products(self, query: str) -> List[Dict]:
        """
        Search Flipkart for products matching query.
        Uses Flipkart Affiliate API.
        """
        # For development, return mock products
        return self._get_mock_products(query)

    def _get_mock_products(self, query: str) -> List[Dict]:
        """Mock Flipkart product data."""
        mock_products = [
            {
                'name': f'{query.title()} - Stylish Printed Dress',
                'original_price': 1299,
                'sale_price': 349,
                'rating': round(random.uniform(4.0, 4.7), 1),
                'review_count': random.randint(100, 3000),
                'category': 'wrap',
                'product_url': f'https://flipkart.com/dress/FLPK{random.randint(1000,9999)}',
                'affiliate_url': f'https://flipkart.com/dress/FLPK{random.randint(1000,9999)}?affid={self.affiliate_id}',
                'image_url': f'https://source.unsplash.com/600x750/?printed,dress,stylish&sig={random.randint(1,999)}',
                'is_trending': True,
            },
            {
                'name': f'Women {query.title()} Solid Mini Dress',
                'original_price': 999,
                'sale_price': 299,
                'rating': round(random.uniform(4.1, 4.8), 1),
                'review_count': random.randint(200, 6000),
                'category': 'bodycon',
                'product_url': f'https://flipkart.com/dress/FLPK{random.randint(1000,9999)}',
                'affiliate_url': f'https://flipkart.com/dress/FLPK{random.randint(1000,9999)}?affid={self.affiliate_id}',
                'image_url': f'https://source.unsplash.com/600x750/?mini,dress,party&sig={random.randint(1,999)}',
                'is_trending': True,
            },
        ]
        return mock_products
