"""
Meesho product scraper for FashionBazzer.
Scrapes trending dress products from meesho.com using page scraping,
since Meesho does not provide a public affiliate API.

Falls back gracefully if Meesho blocks scraping.
Uses affiliate linking via meesho.com product URLs.
"""
import json
import logging
import random
import re
import time
import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse, urlencode, parse_qs

from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, TRENDING_KEYWORDS
from django.conf import settings

logger = logging.getLogger(__name__)

# User-agent rotation to avoid blocks
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


class MeeshoScraper(BaseScraper):
    """Scraper for Meesho products using page scraping."""

    platform_name = "meesho"

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.meesho.com"

    def run(self) -> Dict:
        """
        Scrape trending dress products from Meesho.
        """
        all_products = []
        keywords = TRENDING_KEYWORDS[:4]  # Top 4 keywords per run

        for keyword in keywords:
            try:
                products = self.search_products(keyword)
                all_products.extend(products)
                logger.info(f"Meesho: Found {len(products)} products for '{keyword}'")
                # Polite delay between keyword searches
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                self.errors.append(f"Keyword '{keyword}': {str(e)}")
                logger.error(f"Meesho scrape error for '{keyword}': {e}")

        filtered = self.filter_trending(all_products, min_rating=4.0, max_price=1500)
        saved = self.save_products(filtered)

        return {
            **self.get_summary(),
            'new_products': saved,
            'keywords_used': keywords,
        }

    def search_products(self, query: str) -> List[Dict]:
        """
        Search Meesho for products matching the query using page scraping.
        Extracts product data from Meesho search result pages.
        """
        headers = {
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

        try:
            search_url = f"{self.base_url}/search/{requests.utils.quote(query)}"
            response = requests.get(search_url, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Meesho search failed for '{query}': {e}")
            return []

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            logger.warning(f"Meesho returned non-HTML for '{query}': {content_type}")
            return []

        html = response.text
        products = []

        # Strategy 1: Extract from JSON data in script tags (Next.js __NEXT_DATA__)
        products.extend(self._extract_from_nextjs(html, query))

        # Strategy 2: Extract from HTML product cards
        if len(products) < 5:
            products.extend(self._extract_from_html(html, query))

        return products

    def _extract_from_nextjs(self, html: str, query: str) -> List[Dict]:
        """Extract product data from Next.js __NEXT_DATA__."""
        products = []
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not match:
            # Try other data store patterns
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
        if not match:
            match = re.search(r'<script[^>]*>window\.__PRELOADED_STATE__\s*=\s*({.*?});?</script>', html, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(1))

                # Navigate various possible paths to find products
                paths_to_try = [
                    ['props', 'pageProps', 'products'],
                    ['props', 'pageProps', 'searchResult', 'products'],
                    ['props', 'pageProps', 'data', 'products'],
                    ['searchResult', 'products'],
                    ['products', 'data'],
                    ['data', 'products'],
                ]

                items = []
                for path in paths_to_try:
                    current = data
                    found = True
                    for key in path:
                        if isinstance(current, dict) and key in current:
                            current = current[key]
                        else:
                            found = False
                            break
                    if found and isinstance(current, list):
                        items = current
                        break

                if not items and isinstance(data, dict):
                    # Try to find any list in the data structure that looks like products
                    def find_product_lists(obj, depth=0):
                        if depth > 3:
                            return []
                        results = []
                        if isinstance(obj, list) and len(obj) > 0:
                            if isinstance(obj[0], dict) and 'name' in obj[0]:
                                results.append(obj)
                        elif isinstance(obj, dict):
                            for val in obj.values():
                                results.extend(find_product_lists(val, depth + 1))
                        return results

                    for product_list in find_product_lists(data):
                        items.extend(product_list)

                for item in items:
                    p = self._parse_product_item(item)
                    if p:
                        products.append(p)

            except (json.JSONDecodeError, AttributeError, TypeError) as e:
                logger.debug(f"Meesho Next.js data parse error: {e}")

        return products

    def _extract_from_html(self, html: str, query: str) -> List[Dict]:
        """Fallback: Parse product data from rendered HTML."""
        products = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Try multiple selectors for product cards
            card_selectors = [
                '[class*="ProductCard"]',
                '[class*="productCard"]',
                '[class*="sc-"][class*="product"]',
                'a[href*="/product/"]',
                '[class*="card"]',
            ]

            cards = []
            for sel in card_selectors:
                cards = soup.select(sel)
                if len(cards) > 3:
                    break

            for card in cards:
                try:
                    p = self._parse_html_card(card)
                    if p:
                        products.append(p)
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"Meesho HTML parse error: {e}")

        return products

    def _parse_product_item(self, item: Dict) -> Optional[Dict]:
        """Parse a product item from JSON data."""
        try:
            name = item.get('name') or item.get('productName') or item.get('title', '')
            if not name or len(name) < 5:
                return None

            # Price
            price_data = item.get('price', item.get('pricing', {}))
            if isinstance(price_data, dict):
                sale_price = float(price_data.get('currentPrice', price_data.get('salePrice',
                             price_data.get('finalPrice', price_data.get('price', 0)))))
                original_price = float(price_data.get('originalPrice', price_data.get('mrp',
                             price_data.get('strikePrice', sale_price))))
            elif isinstance(price_data, (int, float)):
                sale_price = float(price_data)
                original_price = sale_price
            else:
                sale_price = 0
                original_price = 0

            # Image
            image = item.get('image') or item.get('img') or item.get('images', '')
            if isinstance(image, list):
                image = image[0] if image else ''
            if isinstance(image, dict):
                image = image.get('url', '') or image.get('src', '')

            # Rating — default to 0 when missing (more honest than 4.0)
            rating = 0.0
            review_count = 0
            rating_data = item.get('rating', item.get('ratings', {}))
            if isinstance(rating_data, dict):
                rating = float(rating_data.get('rating', rating_data.get('average', 0)))
                review_count = int(rating_data.get('count', rating_data.get('total', 0)))
            elif isinstance(rating_data, (int, float)):
                rating = float(rating_data)

            # URL
            url = item.get('url') or item.get('productUrl') or item.get('product_url', '')
            if not url or url.startswith('http://localhost'):
                url = item.get('link', '')
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}" if url.startswith('/') else f"{self.base_url}/{url}"

            # Affiliate URL - Meesho uses share links
            affiliate_url = item.get('affiliateLink') or item.get('affiliateUrl', '')
            if not affiliate_url:
                affiliate_url = url

            return {
                'name': name[:300],
                'original_price': original_price,
                'sale_price': sale_price,
                'rating': rating,
                'review_count': review_count,
                'category': self._categorize(name),
                'product_url': url,
                'affiliate_url': affiliate_url,
                'image_url': image,
            }

        except Exception as e:
            logger.debug(f"Meesho item parse error: {e}")
            return None

    def _parse_html_card(self, card) -> Optional[Dict]:
        """Parse a product card from HTML."""
        try:
            # Name
            name_el = card.select_one('[class*="name"], [class*="title"], [class*="Name"], [class*="Title"], img[alt]')
            if not name_el:
                return None
            name = name_el.get('alt') or name_el.get('title') or name_el.text.strip()
            if not name or len(name) < 5:
                return None

            # Price
            price_el = card.select_one('[class*="price"], [class*="Price"], [class*="cost"]')
            price = 0
            if price_el:
                pm = re.search(r'₹?\s*([\d,]+)', price_el.text)
                if pm:
                    price = float(pm.group(1).replace(',', ''))

            # Image
            img = card.select_one('img[src]')
            image_url = img.get('src', '') if img else ''
            if image_url and image_url.startswith('data:'):
                image_url = img.get('data-src', '') if img else ''

            # URL
            link = card if card.name == 'a' else card.select_one('a[href]')
            url = ''
            if link and link.get('href'):
                href = link['href']
                url = href if href.startswith('http') else f"{self.base_url}{href}"

            if not url or not price:
                return None

            return {
                'name': name[:300],
                'original_price': price,
                'sale_price': price,
                'rating': 0.0,
                'review_count': 0,
                'category': self._categorize(name),
                'product_url': url,
                'affiliate_url': url,
                'image_url': image_url,
            }

        except Exception as e:
            logger.debug(f"Meesho HTML card parse error: {e}")
            return None

    def _categorize(self, name: str) -> str:
        """Categorize product based on name."""
        name_lower = name.lower()
        if 'co-ord' in name_lower or 'coord' in name_lower or 'set' in name_lower:
            return 'co-ord'
        elif 'y2k' in name_lower:
            return 'y2k'
        elif 'bodycon' in name_lower:
            return 'bodycon'
        elif 'maxi' in name_lower or 'cottage' in name_lower:
            return 'cottagecore'
        elif 'western' in name_lower or 'fusion' in name_lower:
            return 'indo-western'
        elif 'mini' in name_lower:
            return 'bodycon'
        elif 'party' in name_lower:
            return 'cut-out'
        elif 'wrap' in name_lower or 'printed' in name_lower:
            return 'wrap'
        elif 'athleisure' in name_lower or 'sport' in name_lower:
            return 'athleisure'
        else:
            return 'other'
