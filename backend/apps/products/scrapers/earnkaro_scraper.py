"""
EarnKaro affiliate scraper for FashionBazzer.

EarnKaro is an Indian affiliate marketing platform that aggregates products
from Meesho, Myntra, AJIO, Amazon, Flipkart and other retailers with
commissions of 5-25% (highest among all platforms in plan.md).

EarnKaro does NOT provide a public API for searching products or generating
links programmatically. Instead, users paste retailer product URLs into
EarnKaro's "Make Links" tool to get tracked "Profit Links."

This scraper has two modes:
  1. BROWSABLE DEALS: Scrapes earnkaro.in for publicly listed products/deals
  2. LINK ENRICHMENT: Batch-enriches existing products in the database with
     EarnKaro affiliate links (requires EARNKARO_USER_ID and manual setup)

The scraper falls back gracefully if EarnKaro blocks scraping.
"""
import json
import logging
import random
import re
import time
import requests
from typing import Dict, List, Optional
from urllib.parse import urlparse, urlencode, parse_qs, quote

from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from django.conf import settings

logger = logging.getLogger(__name__)

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

# EarnKaro search/filterable category pages
EARNKARO_CATEGORY_URLS = {
    'fashion': 'https://www.earnkaro.in/category/fashion',
    'women-ethnic': 'https://www.earnkaro.in/category/women-ethnic',
    'women-western': 'https://www.earnkaro.in/category/women-western',
    'dresses': 'https://www.earnkaro.in/category/dresses',
    'top-offers': 'https://www.earnkaro.in/top-offers',
    'trending': 'https://www.earnkaro.in/trending',
}


class EarnKaroScraper(BaseScraper):
    """Scraper for EarnKaro products and affiliate link enrichment."""

    platform_name = "earnkaro"

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.earnkaro.in"
        self.user_id = settings.EARNKARO_USER_ID

    def run(self) -> Dict:
        """
        Scrape trending fashion deals from EarnKaro's browsable categories.

        Also enriches existing products with EarnKaro affiliate links
        when possible (requires EARNKARO_USER_ID to be set).
        """
        all_products = []

        # Try each category URL for browsable deals
        for name, url in EARNKARO_CATEGORY_URLS.items():
            try:
                products = self.scrape_category(url, name)
                all_products.extend(products)
                logger.info(f"EarnKaro: Found {len(products)} products in '{name}'")
                time.sleep(random.uniform(1.5, 3.0))
            except Exception as e:
                self.errors.append(f"Category '{name}': {str(e)}")
                logger.error(f"EarnKaro scrape error for '{name}': {e}")

        # Save any products found
        saved = self.save_products(all_products)

        # Also enrich existing products with EarnKaro affiliate links
        enrichment_result = None
        if self.user_id and not settings.DEBUG:
            try:
                enrichment_result = self.enrich_existing_products(batch_size=30)
                logger.info(f"EarnKaro enrichment: {enrichment_result}")
            except Exception as e:
                logger.error(f"EarnKaro enrichment failed: {e}")
                enrichment_result = {'error': str(e)}

        result = {
            **self.get_summary(),
            'new_products': saved,
            'categories_tried': list(EARNKARO_CATEGORY_URLS.keys()),
        }
        if enrichment_result:
            result['enrichment'] = enrichment_result

        return result

    def scrape_category(self, url: str, category_name: str) -> List[Dict]:
        """
        Try to scrape product listings from an EarnKaro category page.

        EarnKaro may use client-side rendering for their product listings,
        so this is best-effort and may return empty results if the page
        requires JavaScript.
        """
        headers = {
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }

        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"EarnKaro category '{category_name}' fetch failed: {e}")
            return []

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            logger.warning(f"EarnKaro returned non-HTML for '{category_name}': {content_type}")
            return []

        html = response.text

        # Check for bot challenge pages
        if len(html) < 2000 or 'cf-browser-verification' in html.lower() or 'challenge' in html.lower():
            logger.warning(f"EarnKaro likely blocked for '{category_name}' (small/challenge page)")
            return []

        products = []

        # Strategy 1: JSON-LD structured data
        products.extend(self._extract_json_ld(html))

        # Strategy 2: Next.js __NEXT_DATA__ or similar
        if len(products) < 3:
            products.extend(self._extract_from_scripts(html))

        # Strategy 3: HTML product card parsing
        if len(products) < 3:
            products.extend(self._extract_from_html(html, category_name))

        return products

    def _extract_json_ld(self, html: str) -> List[Dict]:
        """Extract product data from JSON-LD structured data."""
        products = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    items_to_check = []

                    if isinstance(data, dict):
                        if '@graph' in data and isinstance(data['@graph'], list):
                            items_to_check = data['@graph']
                        elif 'itemListElement' in data and isinstance(data.get('itemListElement'), list):
                            items_to_check = data['itemListElement']
                        elif 'name' in data:
                            items_to_check = [data]
                    elif isinstance(data, list):
                        items_to_check = data

                    for item in items_to_check:
                        if isinstance(item, dict):
                            p = self._parse_ld_item(item)
                            if p and not any(x['product_url'] == p['product_url'] for x in products):
                                products.append(p)
                except (json.JSONDecodeError, AttributeError, TypeError):
                    continue
        except Exception as e:
            logger.debug(f"EarnKaro JSON-LD extraction error: {e}")
        return products

    def _parse_ld_item(self, item: Dict) -> Optional[Dict]:
        """Parse a JSON-LD item into standard product format."""
        try:
            inner = item.get('item', item)
            name = inner.get('name', '')
            if not name or len(name) < 5:
                return None

            offers = inner.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            if isinstance(offers, dict) and 'offers' in offers:
                offers = offers['offers']
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}

            price_str = offers.get('price', '0')
            if isinstance(price_str, str):
                price_str = price_str.replace(',', '').replace('₹', '').replace('Rs.', '')
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                price = 0

            # Extract original/MRP price
            original_price = price
            if isinstance(offers, dict):
                hp = offers.get('highPrice', offers.get('listPrice', 0))
                if hp and float(hp) > price:
                    original_price = float(hp)

            # Image
            image = inner.get('image', '')
            if isinstance(image, list):
                image = image[0] if image else ''
            if isinstance(image, dict):
                image = image.get('url', '')

            # Rating
            agg_rating = inner.get('aggregateRating', {})
            rating = float(agg_rating.get('ratingValue', 0))
            review_count = int(agg_rating.get('reviewCount', 0))

            # URL
            url = inner.get('url', '')
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Build EarnKaro affiliate URL
            affiliate_url = self._build_earnkaro_url(url)

            return {
                'name': name[:300],
                'original_price': original_price or price,
                'sale_price': price,
                'rating': rating,
                'review_count': review_count,
                'category': self._categorize(name),
                'product_url': url,
                'affiliate_url': affiliate_url,
                'image_url': image,
            }
        except Exception as e:
            logger.debug(f"EarnKaro JSON-LD parse error: {e}")
            return None

    def _extract_from_scripts(self, html: str) -> List[Dict]:
        """Extract product data from __NEXT_DATA__ or embedded JSON.
        
        EarnKaro uses Next.js which embeds product data in __NEXT_DATA__ script tags.
        """
        products = []
        try:
            # __NEXT_DATA__
            match = re.search(
                r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                html, re.DOTALL
            )
            if match:
                data = json.loads(match.group(1))

                # Navigate typical Next.js paths
                paths_to_try = [
                    ['props', 'pageProps', 'products'],
                    ['props', 'pageProps', 'deals'],
                    ['props', 'pageProps', 'listings'],
                    ['props', 'pageProps', 'data', 'products'],
                    ['props', 'pageProps', 'initialState', 'products'],
                    ['pageProps', 'products'],
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

                for item in items:
                    p = self._parse_product_item(item)
                    if p:
                        products.append(p)

            # Also try for window.__INITIAL_STATE__
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
            if match and not products:
                data = json.loads(match.group(1))

                def find_product_lists(obj, depth=0):
                    if depth > 3:
                        return []
                    results = []
                    if isinstance(obj, list) and len(obj) > 0:
                        if isinstance(obj[0], dict) and ('name' in obj[0] or 'productName' in obj[0]):
                            results.append(obj)
                    elif isinstance(obj, dict):
                        for val in obj.values():
                            results.extend(find_product_lists(val, depth + 1))
                    return results

                for product_list in find_product_lists(data):
                    for item in product_list:
                        p = self._parse_product_item(item)
                        if p:
                            products.append(p)

        except Exception as e:
            logger.debug(f"EarnKaro script extraction error: {e}")

        return products

    def _extract_from_html(self, html: str, category: str) -> List[Dict]:
        """Fallback: Parse product cards from rendered HTML."""
        products = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            card_selectors = [
                '[class*="product"]',
                '[class*="deal"]',
                '[class*="card"]',
                '[class*="listing"]',
                'a[href*="/product/"]',
            ]

            cards = []
            for sel in card_selectors:
                cards = soup.select(sel)
                if len(cards) > 2:
                    break

            for card in cards[:30]:
                try:
                    p = self._parse_html_card(card)
                    if p:
                        products.append(p)
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"EarnKaro HTML parse error: {e}")

        return products

    def _parse_product_item(self, item: Dict) -> Optional[Dict]:
        """Parse a product item from JSON data."""
        try:
            name = item.get('name') or item.get('productName') or item.get('title', '')
            if not name or len(name) < 5:
                return None

            # Brand
            brand = item.get('brand') or item.get('brandName', '')

            # Price
            price_data = item.get('price', item.get('pricing', {}))
            if isinstance(price_data, dict):
                sale_price = float(price_data.get('finalPrice', price_data.get('salePrice',
                             price_data.get('price', 0))))
                original_price = float(price_data.get('originalPrice', price_data.get('mrp',
                             price_data.get('listPrice', sale_price))))
            elif isinstance(price_data, (int, float)):
                sale_price = float(price_data)
                original_price = sale_price
            else:
                sale_price = 0
                original_price = 0

            # Image
            image = item.get('image') or item.get('img') or item.get('imageUrl', '')
            if isinstance(image, list):
                image = image[0] if image else ''
            if isinstance(image, dict):
                image = image.get('url', '')

            # Rating
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
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}" if url.startswith('/') else f"{self.base_url}/{url}"

            affiliate_url = self._build_earnkaro_url(url)

            full_name = f"{brand} {name}" if brand else name

            return {
                'name': full_name[:300],
                'original_price': original_price or sale_price,
                'sale_price': sale_price,
                'rating': rating,
                'review_count': review_count,
                'category': self._categorize(full_name),
                'product_url': url,
                'affiliate_url': affiliate_url,
                'image_url': image,
            }
        except Exception as e:
            logger.debug(f"EarnKaro item parse error: {e}")
            return None

    def _parse_html_card(self, card) -> Optional[Dict]:
        """Parse an HTML product card."""
        try:
            # Link
            link_el = card if card.name == 'a' else card.select_one('a[href]')
            if not link_el or not link_el.get('href'):
                return None

            href = link_el['href']
            url = href if href.startswith('http') else f"{self.base_url}{href}"

            # Name
            name_el = card.select_one(
                '[class*="name"], [class*="title"], h2, h3, [class*="product-name"], img[alt]'
            )
            if not name_el:
                return None
            name = name_el.get('alt') or name_el.get('title') or name_el.text.strip()
            if not name or len(name) < 5:
                return None

            # Image
            img_el = card.select_one('img[src]')
            image_url = img_el.get('src', '') if img_el else ''
            if image_url and image_url.startswith('data:'):
                image_url = img_el.get('data-src', '')

            # Price
            price_el = card.select_one(
                '[class*="price"], [class*="amount"], [class*="cost"], [class*="Price"]'
            )
            price = 0
            if price_el:
                pm = re.search(r'₹?\s*([\d,]+)', price_el.text)
                if pm:
                    price = float(pm.group(1).replace(',', ''))

            if not url or not price:
                return None

            affiliate_url = self._build_earnkaro_url(url)

            return {
                'name': name[:300],
                'original_price': price,
                'sale_price': price,
                'rating': 0.0,
                'review_count': 0,
                'category': self._categorize(name),
                'product_url': url,
                'affiliate_url': affiliate_url,
                'image_url': image_url,
            }
        except Exception as e:
            logger.debug(f"EarnKaro HTML card parse error: {e}")
            return None

    def _build_earnkaro_url(self, original_url: str) -> str:
        """
        Build an EarnKaro tracked affiliate URL.

        EarnKaro affiliate links follow the format:
        https://www.earnkaro.in/link/{user_id}?url={encoded_product_url}

        This is a best-effort URL construction. For full commission tracking,
        the user should configure EARNKARO_USER_ID and manually verify links.
        """
        if not original_url or not self.user_id:
            return original_url
        try:
            encoded = quote(original_url, safe='')
            return f"https://www.earnkaro.in/link/{self.user_id}?url={encoded}"
        except Exception:
            return original_url

    def enrich_existing_products(self, batch_size: int = 30) -> dict:
        """
        Batch-enrich existing products with EarnKaro affiliate links.

        Processes products from Meesho, Myntra, and AJIO (EarnKaro's partners)
        and attempts to build EarnKaro tracked links for them.

        Updates the affiliate_url on products to point through EarnKaro
        for higher commission rates (5-25% vs 2-5% direct).

        Returns:
            Summary dict with counts of enriched products.
        """
        from apps.products.models import Product
        from decimal import Decimal

        if not self.user_id:
            logger.warning("EARNKARO_USER_ID not set — skipping enrichment")
            return {'enriched': 0, 'skipped': 0, 'error': 'EARNKARO_USER_ID not configured'}

        # EarnKaro supports these partner platforms
        supported_platforms = ['meesho', 'myntra', 'ajio']

        enriched = 0
        skipped = 0
        errors = []

        for platform in supported_platforms:
            products = Product.objects.filter(
                platform=platform
            ).exclude(
                product_url__startswith='http://localhost'
            ).exclude(
                product_url=''
            ).order_by('?')[:batch_size]

            for product in products:
                try:
                    # Check if already has an EarnKaro link
                    if 'earnkaro' in product.affiliate_url.lower():
                        skipped += 1
                        continue

                    # Build EarnKaro affiliate URL
                    earnkaro_url = self._build_earnkaro_url(product.product_url)

                    if earnkaro_url and earnkaro_url != product.product_url:
                        product.affiliate_url = earnkaro_url
                        product.save(update_fields=['affiliate_url'])
                        enriched += 1
                    else:
                        skipped += 1

                except Exception as e:
                    errors.append(str(e))
                    logger.error(f"Failed to enrich product #{product.id}: {e}")

        logger.info(
            f"EarnKaro enrichment: {enriched} enriched, {skipped} skipped, "
            f"{len(errors)} errors"
        )

        return {
            'enriched': enriched,
            'skipped': skipped,
            'errors': errors[:5],
        }

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
        elif 'indo' in name_lower or 'fusion' in name_lower or 'western' in name_lower:
            return 'indo-western'
        elif 'athleisure' in name_lower or 'sport' in name_lower:
            return 'athleisure'
        elif 'cut' in name_lower or 'party' in name_lower:
            return 'cut-out'
        elif 'wrap' in name_lower or 'printed' in name_lower:
            return 'wrap'
        elif 'mini' in name_lower:
            return 'bodycon'
        elif 'shirt' in name_lower:
            return 'other'
        elif 'slip' in name_lower:
            return 'other'
        elif 'puff' in name_lower or 'smocked' in name_lower:
            return 'other'
        else:
            return 'other'
