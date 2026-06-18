"""
Flipkart affiliate scraper for FashionBazzer.
Scrapes trending dress products from Flipkart using page scraping.
Falls back gracefully if Flipkart blocks scraping.
"""
import json
import logging
import re
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


class FlipkartScraper(BaseScraper):
    """Scraper for Flipkart affiliate products using page scraping."""

    platform_name = "flipkart"

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.flipkart.com"
        self.affiliate_id = settings.FLIPKART_AFFILIATE_ID

    def run(self) -> Dict:
        """
        Scrape trending dress products from Flipkart.
        """
        all_products = []
        # Search queries focused on trending dress categories for 15-30 age group
        search_queries = [
            "dresses under 500",
            "trendy dresses women",
            "party dresses",
            "western wear dresses",
            "co-ord sets",
        ]

        for query in search_queries:
            try:
                products = self.search_products(query)
                all_products.extend(products)
                logger.info(f"Flipkart: Found {len(products)} products for '{query}'")
            except Exception as e:
                self.errors.append(f"Query '{query}': {str(e)}")
                logger.error(f"Flipkart scrape error for '{query}': {e}")

        # Filter for quality, budget-friendly products (max ₹1500 for 15-30 age group)
        filtered = self.filter_trending(all_products, min_rating=4.0, max_price=1500)
        saved = self.save_products(filtered)

        return {
            **self.get_summary(),
            'new_products': saved,
            'keywords_used': search_queries,
        }

    def search_products(self, query: str) -> List[Dict]:
        """
        Search Flipkart for products matching query using page scraping.
        Extracts product data from Flipkart's search result pages.
        """
        headers = {
            "User-Agent": _USER_AGENTS[hash(query) % len(_USER_AGENTS)],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        try:
            search_url = f"{self.base_url}/search?q={requests.utils.quote(query)}&sort=popularity"
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Flipkart search failed for '{query}': {e}")
            return []

        # Check if we got HTML (not a bot challenge)
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            logger.warning(f"Flipkart returned non-HTML for '{query}': {content_type}")
            return []

        html = response.text

        # Try multiple extraction strategies
        products = []

        # Strategy 1: Look for JSON-LD structured data (most reliable)
        products.extend(self._extract_json_ld(html))

        # Strategy 2: Look for __NEXT_DATA__ or __INITIAL_STATE__ (Next.js apps)
        if not products:
            products.extend(self._extract_nextjs_data(html))

        # Strategy 3: Regex-based extraction from script tags
        if not products:
            products.extend(self._extract_from_scripts(html))

        # Strategy 4: HTML parsing fallback
        if not products:
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
                    if isinstance(data, dict):
                        items = data.get('itemListElement', [data])
                        for item in items:
                            if isinstance(item, dict):
                                product_data = self._parse_ld_item(item)
                                if product_data:
                                    products.append(product_data)
                    elif isinstance(data, list):
                        for item in data:
                            product_data = self._parse_ld_item(item)
                            if product_data:
                                products.append(product_data)
                except (json.JSONDecodeError, AttributeError):
                    continue
        except Exception as e:
            logger.debug(f"JSON-LD extraction error: {e}")
        return products

    def _parse_ld_item(self, item: Dict) -> Optional[Dict]:
        """Parse a single JSON-LD item into standardized product format."""
        try:
            # Handle itemListElement wrapper
            if 'item' in item:
                item = item['item']

            name = item.get('name', '')
            if not name or 'dress' not in name.lower():
                return None

            offers = item.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}

            price = offers.get('price', 0)
            if isinstance(price, str):
                price = float(price.replace(',', ''))

            # Extract original/MRP price from Flipkart's offers
            # Flipkart LD often has: offers.price (sale), offers.highPrice (MRP)
            # Also check priceSpecification sub-object
            original_price = price
            if isinstance(offers, dict):
                hp = offers.get('highPrice', 0)
                if hp and float(hp) > price:
                    original_price = float(hp)
                spec = offers.get('priceSpecification', {})
                if isinstance(spec, dict):
                    for p in ['listPrice', 'originalPrice', 'fullPrice', 'maxPrice']:
                        v = spec.get(p, 0)
                        if v and float(v) > price:
                            original_price = float(v)
                            break
                # Check itemOffers nested structure
                item_offers = offers.get('itemOffered', {}).get('offers', {})
                if isinstance(item_offers, dict):
                    hp2 = item_offers.get('highPrice', 0)
                    if hp2 and float(hp2) > price:
                        original_price = float(hp2)

            # Extract image
            image = item.get('image', '')
            if isinstance(image, list):
                image = image[0] if image else ''
            if isinstance(image, dict):
                image = image.get('url', '')

            # Extract rating
            review_data = item.get('aggregateRating', {})
            rating = float(review_data.get('ratingValue', 4.0))
            review_count = int(review_data.get('reviewCount', 0))

            # Build product URL
            url = item.get('url', '')
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Add affiliate parameter
            if url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                params['affid'] = [self.affiliate_id]
                new_query = urlencode(params, doseq=True)
                affiliate_url = parsed._replace(query=new_query).geturl()
            else:
                affiliate_url = ''

            return {
                'name': name[:300],
                'original_price': original_price,
                'sale_price': price,
                'rating': rating,
                'review_count': review_count,
                'category': self._categorize_product(name),
                'product_url': url,
                'affiliate_url': affiliate_url,
                'image_url': image,
            }
        except Exception as e:
            logger.debug(f"JSON-LD parse error: {e}")
            return None

    def _extract_nextjs_data(self, html: str) -> List[Dict]:
        """Extract product data from Next.js __NEXT_DATA__ or __INITIAL_STATE__."""
        products = []

        # Try __NEXT_DATA__
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                # Navigate through Next.js data structure
                props = data.get('props', {}).get('pageProps', {})
                initial_state = props.get('initialState', {})
                search_results = initial_state.get('searchResult', {}).get('productList', [])
                for item in search_results:
                    product_data = self._parse_search_item(item)
                    if product_data:
                        products.append(product_data)
            except (json.JSONDecodeError, AttributeError) as e:
                logger.debug(f"__NEXT_DATA__ parse error: {e}")

        return products

    def _extract_from_scripts(self, html: str) -> List[Dict]:
        """Extract product data from various script tag patterns."""
        products = []
        try:
            # Look for window.__INITIAL_STATE__
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
            if match:
                import json
                data = json.loads(match.group(1))
                # Navigate to find products
                widgets = data.get('widgets', {})
                for widget_key, widget_data in widgets.items():
                    items = widget_data.get('data', {}).get('items', [])
                    for item in items:
                        product_data = self._parse_search_item(item)
                        if product_data and product_data not in products:
                            products.append(product_data)

            # Look for FLK_DATA or similar Flipkart-specific data stores
            for pattern in [
                r'FLK_DATA\s*=\s*({.*?});',
                r'flkData\s*=\s*({.*?});',
                r'window\.__flk__\s*=\s*({.*?});',
            ]:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    # Try to extract product list from various paths
                    for path in [
                        ['data', 'products'],
                        ['products'],
                        ['searchResults', 'products'],
                        ['data', 'searchResults', 'products'],
                    ]:
                        current = data
                        for key in path:
                            if isinstance(current, dict):
                                current = current.get(key, {})
                        if isinstance(current, list):
                            for item in current:
                                product_data = self._parse_search_item(item)
                                if product_data and product_data not in products:
                                    products.append(product_data)
                            if products:
                                break
        except Exception as e:
            logger.debug(f"Script extraction error: {e}")

        return products

    def _extract_from_html(self, html: str, query: str) -> List[Dict]:
        """
        Fallback: Parse product cards from rendered HTML.
        This is a best-effort extraction and may break if Flipkart changes their markup.
        """
        products = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Flipkart uses various class names for product tiles
            product_containers = soup.select('[class*="product"], [class*="Product"], [class*="tile"], [class*="Tile"], [class*="card"], [class*="Card"], ._1xHGtK, ._2kHMtA')

            for container in product_containers[:30]:
                try:
                    # Try to extract from various HTML structures
                    name_el = (
                        container.select_one('[class*="name"], [class*="Name"], [class*="title"], [class*="Title"], a[href*="product"]')
                        or container.select_one('img[alt]')
                    )
                    if not name_el:
                        continue

                    name = name_el.get('alt') or name_el.get('title') or name_el.text.strip()
                    if not name or len(name) < 5:
                        continue

                    # Extract price
                    price_el = container.select_one('[class*="price"], [class*="Price"], ._30jeq3, ._1_WHN1')
                    price = 0
                    if price_el:
                        price_text = price_el.text.strip()
                        price_match = re.search(r'₹?([\d,]+)', price_text)
                        if price_match:
                            price = float(price_match.group(1).replace(',', ''))

                    # Extract image
                    img_el = container.select_one('img[src]')
                    image_url = img_el.get('src', '') if img_el else ''

                    # Extract product URL
                    link_el = container.select_one('a[href*="product"]') or name_el
                    product_url = ''
                    if link_el and link_el.name == 'a' and link_el.get('href'):
                        href = link_el['href']
                        product_url = href if href.startswith('http') else f"{self.base_url}{href}"
                    elif img_el and img_el.parent and img_el.parent.name == 'a' and img_el.parent.get('href'):
                        href = img_el.parent['href']
                        product_url = href if href.startswith('http') else f"{self.base_url}{href}"

                    if not product_url or not price:
                        continue

                    # Add affiliate parameter
                    parsed = urlparse(product_url)
                    params = parse_qs(parsed.query)
                    params['affid'] = [self.affiliate_id]
                    new_query = urlencode(params, doseq=True)
                    affiliate_url = parsed._replace(query=new_query).geturl()

                    # Try to also extract original/MRP from Flipkart HTML
                    # Check for strike-through price (original price)
                    orig_price = price
                    strike_el = container.select_one('[class*="strike"], [class*="Strike"], [class*="mrp"], ._3I9_wc, [class*="original"]')
                    if strike_el:
                        sm = re.search(r'₹?\s*([\d,]+)', strike_el.text)
                        if sm:
                            orig_price = float(sm.group(1).replace(',', ''))

                    products.append({
                        'name': name[:300],
                        'original_price': orig_price if orig_price > price else price,
                        'sale_price': price,
                        'rating': 4.0,
                        'review_count': 0,
                        'category': self._categorize_product(name),
                        'product_url': product_url,
                        'affiliate_url': affiliate_url,
                        'image_url': image_url,
                    })

                except Exception as e:
                    logger.debug(f"HTML item parse error: {e}")
                    continue

        except Exception as e:
            logger.debug(f"HTML extraction error: {e}")

        return products

    def _parse_search_item(self, item: Dict) -> Optional[Dict]:
        """Parse a search result item into standardized format."""
        try:
            name = item.get('name') or item.get('title') or item.get('productName') or item.get('product_name', '')
            if not name or 'dress' not in name.lower() and 'co-ord' not in name.lower() and 'set' not in name.lower():
                return None

            # Get price
            price_data = item.get('price', {}) or item.get('pricing', {})
            if isinstance(price_data, dict):
                sale_price = float(price_data.get('finalPrice', price_data.get('salePrice', price_data.get('price', 0))))
                original_price = float(price_data.get('originalPrice', price_data.get('mrp',
                             price_data.get('strikePrice', price_data.get('listPrice', sale_price)))))
            else:
                sale_price = float(price_data) if price_data else 0
                original_price = sale_price

            # Get rating
            rating = item.get('rating', {})
            if isinstance(rating, dict):
                rating_value = float(rating.get('rating', rating.get('value', 0)))
                review_count = int(rating.get('count', rating.get('reviewCount', 0)))
            else:
                rating_value = float(rating) if rating else 0
                review_count = 0

            # Get image
            image = item.get('image') or item.get('img') or item.get('imageUrl') or item.get('image_url', '')
            if isinstance(image, dict):
                image = image.get('url', '')

            # Get URL
            url = item.get('url') or item.get('productUrl') or item.get('product_url', '')
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Add affiliate parameter
            affiliate_url = ''
            if url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                params['affid'] = [self.affiliate_id]
                new_query = urlencode(params, doseq=True)
                affiliate_url = parsed._replace(query=new_query).geturl()

            return {
                'name': name[:300],
                'original_price': original_price,
                'sale_price': sale_price,
                'rating': rating_value,
                'review_count': review_count,
                'category': self._categorize_product(name),
                'product_url': url,
                'affiliate_url': affiliate_url,
                'image_url': image,
            }
        except Exception as e:
            logger.debug(f"Search item parse error: {e}")
            return None

    def _categorize_product(self, name: str) -> str:
        """Categorize a product based on its name."""
        name_lower = name.lower()
        if 'co-ord' in name_lower or 'coord' in name_lower:
            return 'co-ord'
        elif 'y2k' in name_lower:
            return 'y2k'
        elif 'bodycon' in name_lower:
            return 'bodycon'
        elif 'maxi' in name_lower or 'cottagecore' in name_lower:
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
        else:
            return 'other'
