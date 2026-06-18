"""
Amazon affiliate scraper for FashionBazzer.
Scrapes trending dress products from Amazon.in using page scraping
(via search result HTML parsing) since the PAAPI SDK is not available.

Falls back gracefully if Amazon blocks scraping.
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

# User-agent rotation to avoid blocks
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


class AmazonScraper(BaseScraper):
    """Scraper for Amazon.in affiliate products using page scraping."""

    platform_name = "amazon"

    def __init__(self):
        super().__init__()
        self.associate_tag = settings.AMAZON_ASSOCIATE_ID
        self.base_url = "https://www.amazon.in"

    def run(self) -> Dict:
        """
        Scrape trending dress products from Amazon.
        """
        all_products = []
        # Keywords focused on trending dresses for 15-30 age group, under 1500
        keywords = [
            "dresses under 500",
            "trendy dresses for women",
            "party dresses for women",
            "casual dresses women",
            "western dresses for girls",
        ]

        for keyword in keywords:
            try:
                products = self.search_products(keyword)
                all_products.extend(products)
                logger.info(f"Amazon: Found {len(products)} products for '{keyword}'")
            except Exception as e:
                self.errors.append(f"Keyword '{keyword}': {str(e)}")
                logger.error(f"Amazon scrape error for '{keyword}': {e}")

        filtered = self.filter_trending(all_products, min_rating=4.0, max_price=1500)
        saved = self.save_products(filtered)

        return {
            **self.get_summary(),
            'new_products': saved,
        }

    def search_products(self, query: str) -> List[Dict]:
        """
        Search Amazon.in for products matching query using page scraping.
        Extracts product data from Amazon search result pages.

        Uses BeautifulSoup to parse the HTML and extract product info.
        Adds delays between requests to avoid rate-limiting.
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
            search_url = (
                f"{self.base_url}/s?k={requests.utils.quote(query)}"
                f"&ref=nb_sb_noss&sort=review-rank"
            )
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()

            # Polite delay between requests to avoid being blocked
            time.sleep(random.uniform(1.5, 3.0))

        except requests.RequestException as e:
            logger.warning(f"Amazon search failed for '{query}': {e}")
            return []

        # Check if we got HTML
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            logger.warning(f"Amazon returned non-HTML for '{query}': {content_type}")
            return []

        html = response.text
        products = []

        # Strategy 1: JSON-LD structured data (@graph format)
        products.extend(self._extract_json_ld(html))

        # Strategy 2: Parse search result cards from HTML
        if len(products) < 3:
            products.extend(self._extract_from_html(html, query))

        return products

    def _extract_json_ld(self, html: str) -> List[Dict]:
        """Extract product data from JSON-LD structured data.
        Handles @graph arrays, itemListElement, and direct items.
        """
        products = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    items_to_check = []

                    if isinstance(data, dict):
                        # Amazon wraps in @graph: [{...}, {...}]
                        if '@graph' in data and isinstance(data['@graph'], list):
                            items_to_check = data['@graph']
                        # itemListElement for search result pages
                        elif 'itemListElement' in data and isinstance(data.get('itemListElement'), list):
                            items_to_check = data['itemListElement']
                        # Single product object
                        elif 'name' in data or '@type' in data:
                            items_to_check = [data]
                    elif isinstance(data, list):
                        items_to_check = data

                    for item in items_to_check:
                        if isinstance(item, dict):
                            p = self._parse_ld_item(item)
                            if p:
                                # Deduplicate by URL
                                if p['product_url'] and not any(x['product_url'] == p['product_url'] for x in products):
                                    products.append(p)
                except (json.JSONDecodeError, AttributeError, TypeError) as e:
                    logger.debug(f"JSON-LD parse error: {e}")
                    continue
        except Exception as e:
            logger.debug(f"JSON-LD extraction error: {e}")
        return products

    def _parse_ld_item(self, item: Dict) -> Optional[Dict]:
        """Parse a JSON-LD item into standardized product format."""
        try:
            # Handle itemListElement wrapper
            inner = item.get('item', item)
            name = inner.get('name', '')
            if not name or not any(kw in name.lower() for kw in ['dress', 'fashion', 'wear', 'top', 'kurta']):
                return None

            offers = inner.get('offers', {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            if isinstance(offers, dict):
                offers = offers.get('offers', offers)  # Handle nested offers

            price_str = offers.get('price', '0')
            if isinstance(price_str, str):
                price_str = price_str.replace(',', '').replace('₹', '')
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                price = 0

            # Image
            image = inner.get('image', '')
            if isinstance(image, list):
                image = image[0] if image else ''
            if isinstance(image, dict):
                image = image.get('url', '')

            # Rating
            agg_rating = inner.get('aggregateRating', {})
            rating = float(agg_rating.get('ratingValue', 4.0))
            review_count = int(agg_rating.get('reviewCount', 0))

            # URL
            url = inner.get('url', '')
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Build affiliate URL with tag
            affiliate_url = self._add_affiliate_tag(url)

            # Extract original/MRP price from various Amazon price fields
            # Amazon LD often has: offers.price (sale), offers.highPrice (MRP)
            # Also check priceSpecification for list price vs sale price
            original_price = price
            if isinstance(offers, dict):
                # Check for highPrice (search results list BOTH prices)
                hp = offers.get('highPrice', offers.get('listPrice', offers.get('wasPrice', 0)))
                if isinstance(hp, (int, float)) and float(hp) > price:
                    original_price = float(hp)
                # Check for priceSpecification sub-object
                spec = offers.get('priceSpecification', {})
                if isinstance(spec, dict):
                    for p in ['listPrice', 'originalPrice', 'fullPrice']:
                        v = spec.get(p, 0)
                        if v and float(v) > price:
                            original_price = float(v)
                            break
                # Amazon often has minPrice/maxPrice in search results
                min_p = offers.get('minPrice', 0)
                max_p = offers.get('maxPrice', 0)
                if min_p and max_p and float(max_p) > float(min_p):
                    original_price = float(max_p)

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
            logger.debug(f"JSON-LD item parse error: {e}")
            return None

    def _extract_from_html(self, html: str, query: str) -> List[Dict]:
        """
        Fallback: Parse Amazon search result cards from HTML.
        Handles both old-style and new-style Amazon search result pages.
        """
        products = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Amazon search result containers (multiple possible selectors)
            selectors = [
                '[data-component-type="s-search-result"]',
                '.s-result-item[data-asin]',
                '.sg-col-4-of-24',
                '.s-card-container',
                'div[data-asin]',
            ]

            cards = []
            for sel in selectors:
                cards = soup.select(sel)
                if len(cards) > 3:
                    break

            for card in cards:
                try:
                    product = self._parse_card(card, query)
                    if product:
                        products.append(product)
                except Exception:
                    continue

        except Exception as e:
            logger.debug(f"HTML extraction error: {e}")

        return products

    def _parse_card(self, card_element, query: str) -> Optional[Dict]:
        """Parse a single Amazon search result card."""
        try:
            # Product name
            name_el = (
                card_element.select_one('h2 a span')
                or card_element.select_one('h2 a')
                or card_element.select_one('[class*="title"] span')
                or card_element.select_one('img[alt]')
            )
            if not name_el:
                return None

            name = name_el.get('alt') or name_el.get('aria-label') or name_el.text.strip()
            if not name or len(name) < 10:
                return None

            # Price — extract both sale price AND original/MRP
            sale_price = 0
            original_price = 0

            # Try whole-price + fraction first (.a-price-whole + .a-price-fraction)
            whole_el = card_element.select_one('.a-price-whole')
            fraction_el = card_element.select_one('.a-price-fraction') if whole_el else None
            if whole_el:
                whole = whole_el.text.strip().replace(',', '')
                fraction = fraction_el.text.strip() if fraction_el else '00'
                sale_price = float(f'{whole}.{fraction}')

            # Fallback to .a-offscreen or general price selectors
            if not sale_price:
                for sel in ['[class*="price"]', '.a-offscreen']:
                    price_el = card_element.select_one(sel)
                    if price_el:
                        price_text = price_el.text.strip()
                        pm = re.search(r'(\d[\d,]*)', price_text.replace(',', ''))
                        if pm:
                            sale_price = float(pm.group(1).replace(',', ''))
                            break

            # Extract original/MRP price (strike-through or 'was' price)
            # Amazon shows:  ₹1,299 <strike>₹2,499</strike>
            strike_el = card_element.select_one('.a-text-price span.a-offscreen')
            if strike_el:
                pm = re.search(r'(\d[\d,]*)', strike_el.text.replace(',', ''))
                if pm:
                    original_price = float(pm.group(1).replace(',', ''))

            # Image
            img_el = card_element.select_one('img.s-image')
            image_url = img_el.get('src', '') if img_el else ''
            if image_url and image_url.startswith('data:'):
                image_url = img_el.get('data-src', '')

            # Rating
            rating_el = card_element.select_one('[class*="star-rating"], i.a-icon-star')
            rating = 4.0
            if rating_el:
                text = rating_el.get('aria-label', '') or rating_el.text
                rating_match = re.search(r'([\d.]+)', text)
                if rating_match:
                    rating = float(rating_match.group(1))

            # Review count
            review_el = card_element.select_one('[class*="rating-number"], [class*="review-count"], .a-size-base.s-underline-text')
            review_count = 0
            if review_el:
                rc_match = re.search(r'(\d[\d,]*)', review_el.text)
                if rc_match:
                    review_count = int(rc_match.group(1).replace(',', ''))

            # Product URL
            link_el = card_element.select_one('h2 a') or card_element.select_one('a[href*="/dp/"]')
            url = ''
            if link_el and link_el.get('href'):
                href = link_el['href']
                url = href if href.startswith('http') else f"{self.base_url}{href}"

            if not url or not sale_price:
                return None

            affiliate_url = self._add_affiliate_tag(url)

            return {
                'name': name[:300],
                'original_price': original_price or sale_price,
                'sale_price': sale_price,
                'rating': rating,
                'review_count': review_count,
                'category': self._categorize(name),
                'product_url': url,
                'affiliate_url': affiliate_url,
                'image_url': image_url,
            }

        except Exception as e:
            logger.debug(f"Card parse error: {e}")
            return None

    def _add_affiliate_tag(self, url: str) -> str:
        """Add the Amazon affiliate tag to a URL."""
        if not url or not self.associate_tag:
            return url
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        params['tag'] = [self.associate_tag]
        new_query = urlencode(params, doseq=True)
        return urlparse(parsed._replace(query=new_query).geturl())

    def _categorize(self, name: str) -> str:
        """Categorize product based on name."""
        name_lower = name.lower()
        if 'co-ord' in name_lower or 'coord' in name_lower:
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
        elif 'kurta' in name_lower or 'ethnic' in name_lower:
            return 'indo-western'
        else:
            return 'other'
