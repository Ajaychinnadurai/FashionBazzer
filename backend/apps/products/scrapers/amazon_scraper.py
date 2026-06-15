"""
Amazon affiliate scraper for FashionBazzer.
Uses Amazon Product Advertising API 5.0 via the PAAPI SDK.
"""
import logging
from typing import Dict, List
from .base_scraper import BaseScraper, TRENDING_KEYWORDS
from django.conf import settings

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    """Scraper for Amazon.in affiliate products."""

    platform_name = "amazon"

    def __init__(self):
        super().__init__()
        self.associate_tag = settings.AMAZON_ASSOCIATE_ID

    def run(self) -> Dict:
        """
        Scrape trending dress products from Amazon.
        """
        all_products = []
        keywords = ["dress under 500", "trendy dresses women", "party dress"]

        for keyword in keywords:
            try:
                products = self.search_products(keyword)
                all_products.extend(products)
            except Exception as e:
                self.errors.append(f"Keyword '{keyword}': {str(e)}")
                logger.error(f"Amazon scrape error: {e}")

        filtered = self.filter_trending(all_products, min_rating=4.0, max_price=1500)
        saved = self.save_products(filtered)

        return {
            **self.get_summary(),
            'new_products': saved,
        }

    def search_products(self, query: str) -> List[Dict]:
        """
        Search Amazon for products matching query.
        Uses Product Advertising API 5.0 (PAAPI).

        Returns empty list until PAAPI SDK is installed and configured —
        no fake/mock data is ever injected. Real data only.
        """
        logger.warning(
            "Amazon PAAPI SDK not installed/configured. "
            "Install paapi5-python-sdk and set AMAZON_ASSOCIATE_ID to scrape."
        )
        return []
