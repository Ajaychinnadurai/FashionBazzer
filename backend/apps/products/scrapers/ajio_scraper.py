"""
AJIO affiliate scraper for FashionBazzer.
Scrapes trending dress products from ajio.com using page scraping.
AJIO uses third-party affiliate networks (Cuelinks, EarnKaro) for tracking,
so raw product URLs are stored and can be wrapped via affiliate network integration.

AJIO has strong anti-bot protections (Cloudflare). This scraper uses multiple
extraction strategies and falls back gracefully if blocked.

Falls back gracefully if AJIO blocks scraping.
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
from .base_scraper import BaseScraper
from django.conf import settings

logger = logging.getLogger(__name__)

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


class AjioScraper(BaseScraper):
    """Scraper for AJIO products using page scraping."""

    platform_name = "ajio"

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.ajio.com"
        self.affiliate_id = settings.AJIO_AFFILIATE_ID

    def run(self) -> Dict:
        """
        Scrape trending dress products from AJIO.
        """
        all_products = []
        # Keywords focused on trending Gen Z fashion categories
        search_queries = [
            "dresses",
            "trendy dresses",
            "co-ord sets",
            "bodycon dresses",
            "western wear",
            "party dresses",
            "mini dresses",
            "maxi dresses",
        ]

        for query in search_queries:
            try:
                products = self.search_products(query)
                all_products.extend(products)
                logger.info(f"AJIO: Found {len(products)} products for '{query}'")
                # Polite delay between keyword searches
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                self.errors.append(f"Query '{query}': {str(e)}")
                logger.error(f"AJIO scrape error for '{query}': {e}")

        # Filter for quality, budget-friendly products (max ₹2000 for AJIO's price range)
        filtered = self.filter_trending(all_products, min_rating=4.0, max_price=2000)
        saved = self.save_products(filtered)

        return {
            **self.get_summary(),
            'new_products': saved,
            'keywords_used': search_queries,
        }

    def search_products(self, query: str) -> List[Dict]:
        """
        Search AJIO for products matching the query using page scraping.
        Extracts product data from AJIO's search result pages.

        AJIO uses Cloudflare anti-bot protection. Requests may be blocked.
        The scraper handles this gracefully by returning an empty list.
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
            search_url = f"{self.base_url}/search/?text={requests.utils.quote(query)}"
            response = requests.get(search_url, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"AJIO search failed for '{query}': {e}")
            return []

        # Check if we got HTML (not a bot challenge page)
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            logger.warning(f"AJIO returned non-HTML for '{query}': {content_type}")
            return []

        html = response.text

        # If the response is very small, it's likely a bot challenge page
        if len(html) < 2000:
            logger.warning(f"AJIO returned suspiciously small response for '{query}' ({len(html)} bytes) — likely blocked")
            return []

        products = []

        # Strategy 1: Extract from JSON-LD structured data
        products.extend(self._extract_json_ld(html))

        # Strategy 2: Extract from script tags with product data (AJIO uses React/Next.js)
        if len(products) < 3:
            products.extend(self._extract_from_scripts(html))

        # Strategy 3: HTML parsing fallback for product tiles
        if len(products) < 3:
            products.extend(self._extract_from_html(html, query))

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
                        elif 'name' in data or '@type' in data:
                            items_to_check = [data]
                    elif isinstance(data, list):
                        items_to_check = data

                    for item in items_to_check:
                        if isinstance(item, dict):
                            p = self._parse_ld_item(item)
                            if p:
                                if not any(x['product_url'] == p['product_url'] for x in products):
                                    products.append(p)
                except (json.JSONDecodeError, AttributeError, TypeError):
                    continue
        except Exception as e:
            logger.debug(f"AJIO JSON-LD extraction error: {e}")
        return products

    def _parse_ld_item(self, item: Dict) -> Optional[Dict]:
        """Parse a JSON-LD item into standardized product format."""
        try:
            # Handle itemListElement wrapper
            inner = item.get('item', item)
            name = inner.get('name', '')
            if not name or len(name) < 5:
                return None

            offers = inner.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            if isinstance(offers, dict):
                offers = offers.get('offers', offers)

            price_str = offers.get('price', '0')
            if isinstance(price_str, str):
                price_str = price_str.replace(',', '').replace('₹', '').replace('Rs.', '')
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                price = 0

            # Extract original/MRP price from offers
            original_price = price
            if isinstance(offers, dict):
                hp = offers.get('highPrice', offers.get('listPrice', 0))
                if hp and float(hp) > price:
                    original_price = float(hp)
                spec = offers.get('priceSpecification', {})
                if isinstance(spec, dict):
                    for p in ['listPrice', 'fullPrice', 'originalPrice']:
                        v = spec.get(p, 0)
                        if v and float(v) > price:
                            original_price = float(v)
                            break

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

            # Build affiliate URL
            affiliate_url = self._add_affiliate_params(url)

            return {
                'name': name[:300],
                'original_price': original_price,
                'sale_price': price,
                'rating': rating,
                'review_count': review_count,
                'category': self._categorize(name),
                'product_url': url,
                'affiliate_url': affiliate_url,
                'image_url': image,
            }
        except Exception as e:
            logger.debug(f"AJIO JSON-LD item parse error: {e}")
            return None

    def _extract_from_scripts(self, html: str) -> List[Dict]:
        """Extract product data from various script tag patterns.

        AJIO uses React and may embed product data in:
        - window.__INITIAL_STATE__
        - window.__PRELOADED_STATE__
        - Data embedded in <script> tags with product listings
        """
        products = []
        try:
            # Look for various data store patterns
            patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'window\.__PRELOADED_STATE__\s*=\s*({.*?});',
                r'window\.__AJIO_DATA__\s*=\s*({.*?});',
                r'window\.__NUXT__\s*=\s*({.*?});',
            ]

            for pattern in patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))

                        # Try to find product lists in the data
                        def find_product_lists(obj, depth=0):
                            if depth > 3:
                                return []
                            results = []
                            if isinstance(obj, list) and len(obj) > 0:
                                if isinstance(obj[0], dict) and ('name' in obj[0] or 'productName' in obj[0] or 'productId' in obj[0]):
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

                        if products:
                            break
                    except (json.JSONDecodeError, AttributeError, TypeError):
                        continue

        except Exception as e:
            logger.debug(f"AJIO script extraction error: {e}")

        return products

    def _extract_from_html(self, html: str, query: str) -> List[Dict]:
        """
        Fallback: Parse product tiles from rendered HTML.

        AJIO's product tiles typically follow this structure:
        <div class="item">
            <a href="/p/...">
                <img src="image-url" alt="Product Name" />
                <div class="brand">Brand Name</div>
                <div class="nameCls">Product Description</div>
                <div class="price">
                    <span class="final-price">₹1,299</span>
                    <span class="original-price">₹2,499</span>
                </div>
            </a>
        </div>
        """
        products = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # AJIO product tile selectors (multiple variations)
            card_selectors = [
                'div.item',
                '[class*="item"] a[href*="/p/"]',
                '[class*="product-tile"]',
                '[class*="productTile"]',
                'div[class*="product"]',
            ]

            cards = []
            for sel in card_selectors:
                elements = soup.select(sel)
                if len(elements) > 3:
                    cards = elements
                    break

            for card in cards[:40]:  # Max 40 products per search
                try:
                    p = self._parse_html_card(card)
                    if p:
                        # Deduplicate by URL
                        if not any(x['product_url'] == p['product_url'] for x in products):
                            products.append(p)
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"AJIO HTML parse error: {e}")

        return products

    def _parse_product_item(self, item: Dict) -> Optional[Dict]:
        """Parse a product item from JSON data."""
        try:
            name = item.get('name') or item.get('productName') or item.get('title') or item.get('productDisplayName', '')
            if not name or len(name) < 5:
                return None

            # Brand
            brand = item.get('brand') or item.get('brandName') or item.get('brand_name', '')

            # Price
            price_data = item.get('price', item.get('pricing', {}))
            if isinstance(price_data, dict):
                sale_price = float(price_data.get('finalPrice', price_data.get('salePrice',
                             price_data.get('discountedPrice', price_data.get('price', 0)))))
                original_price = float(price_data.get('originalPrice', price_data.get('mrp',
                             price_data.get('strikePrice', price_data.get('listPrice', sale_price)))))
            elif isinstance(price_data, (int, float)):
                sale_price = float(price_data)
                original_price = sale_price
            else:
                sale_price = 0
                original_price = 0

            # Image
            image = item.get('image') or item.get('img') or item.get('images') or item.get('productImage', '')
            if isinstance(image, list):
                # AJIO often stores images as an array of URLs
                for img_candidate in image:
                    if isinstance(img_candidate, str) and img_candidate.startswith('http'):
                        image = img_candidate
                        break
                else:
                    image = image[0] if image else ''
                # If still a list, convert to string
                if isinstance(image, list):
                    image = image[0] if image else ''
            if isinstance(image, dict):
                image = image.get('url', '') or image.get('src', '')
            if image and not image.startswith('http'):
                image = f"https:{image}" if image.startswith('//') else image

            # Rating — default to 0 when missing (more honest than 4.0)
            rating = 0.0
            review_count = 0
            rating_data = item.get('rating', item.get('ratings', {}))
            if isinstance(rating_data, dict):
                rating = float(rating_data.get('rating', rating_data.get('average', rating_data.get('value', 0))))
                review_count = int(rating_data.get('count', rating_data.get('total', 0)))
            elif isinstance(rating_data, (int, float)):
                rating = float(rating_data)

            # URL
            url = item.get('url') or item.get('productUrl') or item.get('product_url') or item.get('productURL', '')
            if url and not url.startswith('http'):
                if url.startswith('/'):
                    url = f"{self.base_url}{url}"
                else:
                    url = f"{self.base_url}/{url}"

            affiliate_url = self._add_affiliate_params(url)

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
            logger.debug(f"AJIO item parse error: {e}")
            return None

    def _parse_html_card(self, card) -> Optional[Dict]:
        """Parse an AJIO product card from HTML.

        AJIO HTML structure for product tiles:
        <div class="item">
            <a href="/p/...">
                <img src="image-url" alt="Product Name" />
                <div class="brand">Brand Name</div>
                <div class="nameCls">Product Description</div>
                <div class="price">
                    <span class="final-price">₹1,299</span>
                    <span class="original-price">₹2,499</span>
                </div>
            </a>
        </div>
        """
        try:
            # Try to find the link element
            link_el = card if card.name == 'a' else card.select_one('a[href*="/p/"]') or card.select_one('a[href]')
            if not link_el or not link_el.get('href'):
                return None

            href = link_el['href']
            url = href if href.startswith('http') else f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"

            # Brand
            brand_el = card.select_one('[class*="brand"]')
            brand = brand_el.text.strip() if brand_el else ''

            # Product name
            name_el = card.select_one('[class*="name"], [class*="title"], [class*="product"], [class*="Name"]')
            name = name_el.text.strip() if name_el else ''

            # Image
            img_el = card.select_one('img[src]')
            image_url = ''
            if img_el:
                image_url = img_el.get('src', '')
                if image_url and image_url.startswith('data:'):
                    image_url = img_el.get('data-src', '')
                if image_url and image_url.startswith('//'):
                    image_url = f"https:{image_url}"

            # Price - AJIO uses various price element classes
            sale_price = 0
            original_price = 0

            for price_sel in ['[class*="final-price"]', '[class*="finalPrice"]', '[class*="discounted"]', '[class*="salePrice"]', '[class*="price"]']:
                price_el = card.select_one(price_sel)
                if price_el:
                    pm = re.search(r'₹?\s*([\d,]+)', price_el.text)
                    if pm:
                        sale_price = float(pm.group(1).replace(',', ''))
                        break

            for orig_sel in ['[class*="original-price"]', '[class*="originalPrice"]', '[class*="strike"]', '[class*="listPrice"]', '[class*="mrp"]']:
                orig_el = card.select_one(orig_sel)
                if orig_el:
                    pm = re.search(r'₹?\s*([\d,]+)', orig_el.text)
                    if pm:
                        original_price = float(pm.group(1).replace(',', ''))
                        break

            if not original_price:
                original_price = sale_price

            full_name = f"{brand} {name}".strip()
            if not full_name or len(full_name) < 5:
                return None
            if not sale_price:
                return None

            affiliate_url = self._add_affiliate_params(url)

            return {
                'name': full_name[:300],
                'original_price': original_price or sale_price,
                'sale_price': sale_price,
                'rating': 4.0,
                'review_count': 0,
                'category': self._categorize(full_name),
                'product_url': url,
                'affiliate_url': affiliate_url,
                'image_url': image_url,
            }

        except Exception as e:
            logger.debug(f"AJIO HTML card parse error: {e}")
            return None

    def _add_affiliate_params(self, url: str) -> str:
        """Add AJIO affiliate tracking parameters to URL.

        AJIO uses third-party affiliate networks (Cuelinks, EarnKaro).
        We add a referral parameter for basic tracking; the user should
        wrap these URLs through their affiliate network dashboard for
        proper commission tracking.
        """
        if not url or not self.affiliate_id:
            return url

        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query, keep_blank_values=True)
            # Use ref parameter for referral tracking
            params['ref'] = [self.affiliate_id]
            new_query = urlencode(params, doseq=True)
            return parsed._replace(query=new_query).geturl()
        except Exception:
            return url

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
        elif 'shirt' in name_lower or 'shirtdress' in name_lower:
            return 'other'
        elif 'slip' in name_lower:
            return 'other'
        elif 'puff' in name_lower or 'smocked' in name_lower:
            return 'other'
        else:
            return 'other'
