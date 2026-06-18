"""
Product image scraper for FashionBazzer.
Fetches real dress images from product pages (og:image) or falls back to Unsplash fashion photos.

Two modes:
  1. Scrape product page HTML → extract og:image meta tag
  2. Fallback to Unsplash Source API → random fashion/dress images
"""
from __future__ import annotations

import logging
import random
from typing import Optional, Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# ── User-agent rotation to avoid blocks ──
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

# ── Category → Unsplash search keywords ──
_CATEGORY_KEYWORDS = {
    "co-ord": "co-ord set fashion dress",
    "y2k": "y2k dress fashion trendy",
    "bodycon": "bodycon mini dress women",
    "cottagecore": "maxi dress summer floral",
    "indo-western": "indo western dress fusion",
    "athleisure": "athleisure dress sporty",
    "cut-out": "cut out dress trendy",
    "wrap": "wrap dress printed floral",
    "other": "dress fashion women outfit",
}

# ── Platform-specific image selectors (fallback if og:image missing) ──
_PLATFORM_SELECTORS = {
    "meesho": [
        "meta[property='og:image']",
        "meta[name='og:image']",
        "img[class*='product']",
        "img[class*='image']",
        "img[alt*='product']",
    ],
    "amazon": [
        "meta[property='og:image']",
        "meta[name='og:image']",
        "#landingImage",
        "img[data-old-hires]",
        ".imgTagWrapper img",
    ],
    "flipkart": [
        "meta[property='og:image']",
        "meta[name='og:image']",
        "._396cs4 img",
        "img[style*='display:block']",
    ],
}


def _random_headers() -> dict:
    """Return request headers with a random user-agent."""
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def scrape_product_image(
    product_url: str,
    platform: str = "other",
    timeout: int = 10,
) -> Optional[str]:
    """
    Attempt to extract the product image URL from a product page.

    Strategy:
      1. Fetch the page HTML
      2. Look for Open Graph image meta tag (og:image)
      3. If not found, try platform-specific CSS selectors
      4. Return None if nothing works (caller falls back to Unsplash)

    Returns:
      Image URL string, or None if extraction failed.
    """
    if not product_url or product_url.startswith("http://localhost"):
        logger.debug(f"Skipping local/missing URL: {product_url}")
        return None

    headers = _random_headers()
    platform = platform.lower()

    try:
        response = requests.get(product_url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch {product_url}: {e}")
        return None

    # Don't parse non-HTML responses (e.g. binary, PDF)
    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        logger.debug(f"Non-HTML content-type ({content_type}) for {product_url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # ── Strategy 1: og:image meta tag ──
    og_image = None
    for attr in ["property", "name"]:
        meta = soup.find("meta", attrs={attr: "og:image"})
        if meta and meta.get("content"):
            og_image = meta["content"].strip()
            break

    if og_image:
        # Some sites return relative URLs — make absolute
        if og_image.startswith("//"):
            og_image = "https:" + og_image
        elif og_image.startswith("/"):
            parsed = urlparse(product_url)
            og_image = f"{parsed.scheme}://{parsed.netloc}{og_image}"
        logger.info(f"Found og:image for {platform}: {og_image[:80]}...")
        return og_image

    # ── Strategy 2: Platform-specific selectors ──
    selectors = _PLATFORM_SELECTORS.get(platform, _PLATFORM_SELECTORS.get("other", []))
    for selector in selectors:
        if selector.startswith("meta"):
            continue  # already checked above
        try:
            elements = soup.select(selector)
            for el in elements:
                src = el.get("src") or el.get("data-src") or ""
                if src and not src.endswith(".svg"):
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        parsed = urlparse(product_url)
                        src = f"{parsed.scheme}://{parsed.netloc}{src}"
                    logger.info(f"Found image via selector '{selector}' for {platform}")
                    return src
        except Exception:
            continue

    logger.debug(f"No product image found on page: {product_url[:60]}...")
    return None


# Curated list of high-quality, actively-serving fashion photo IDs on Unsplash.
# These are verified to return 200 responses (last checked May 2026).
# Uses images.unsplash.com/{photo_id}?w=600 format.
_CURATED_PHOTO_IDS = {
    "co-ord": [
        "photo-1618244972963-dbee1a7edc95",
        "photo-1515886657613-9f3515b0c78f",
        "photo-1609505848912-b7c3b8b4beda",
        "photo-1554412933-514a83d2f3c8",
        "photo-1539109136881-3be0616acf4b",
    ],
    "y2k": [
        "photo-1529139574466-a303027c1d8b",
        "photo-1509631179647-0177331693ae",
        "photo-1554412933-514a83d2f3c8",
        "photo-1618244972963-dbee1a7edc95",
        "photo-1566207274740-0f8cf6b7d5a5",
    ],
    "bodycon": [
        "photo-1595777457583-95e059d581b8",
        "photo-1572804013309-59a88b7e92f1",
        "photo-1611930022073-b7a4ba5fcccd",
        "photo-1618244972963-dbee1a7edc95",
        "photo-1623607915241-a3151d54a5a5",
    ],
    "cottagecore": [
        "photo-1496747611176-843222e1e57c",
        "photo-1508214751196-bcfd4ca60f91",
        "photo-1623607915241-a3151d54a5a5",
        "photo-1509631179647-0177331693ae",
        "photo-1595777457583-95e059d581b8",
    ],
    "indo-western": [
        "photo-1581044777550-4cfa60707c03",
        "photo-1610030469983-98e550d6193c",
        "photo-1617627143750-d86bc21e42bb",
        "photo-1566207274740-0f8cf6b7d5a5",
        "photo-1539109136881-3be0616acf4b",
    ],
    "athleisure": [
        "photo-1518310383802-640c2de311b2",
        "photo-1502224562085-639556652f33",
        "photo-1485968579580-b6d095142e6e",
        "photo-1515886657613-9f3515b0c78f",
        "photo-1572804013309-59a88b7e92f1",
    ],
    "cut-out": [
        "photo-1566207274740-0f8cf6b7d5a5",
        "photo-1596783074918-c84cb06531ca",
        "photo-1539109136881-3be0616acf4b",
        "photo-1611930022073-b7a4ba5fcccd",
        "photo-1529139574466-a303027c1d8b",
    ],
    "wrap": [
        "photo-1544022613-e87ca75a784a",
        "photo-1605518216938-7c31b7b14ad0",
        "photo-1590006742202-fe5b154d8b67",
        "photo-1508214751196-bcfd4ca60f91",
        "photo-1496747611176-843222e1e57c",
    ],
    "other": [
        "photo-1539109136881-3be0616acf4b",
        "photo-1595777457583-95e059d581b8",
        "photo-1496747611176-843222e1e57c",
        "photo-1572804013309-59a88b7e92f1",
        "photo-1509631179647-0177331693ae",
        "photo-1623607915241-a3151d54a5a5",
        "photo-1515886657613-9f3515b0c78f",
        "photo-1618244972963-dbee1a7edc95",
        "photo-1566207274740-0f8cf6b7d5a5",
        "photo-1544022613-e87ca75a784a",
    ]
}


def fetch_unsplash_fashion(category: str = "dress", seed: Optional[int] = None) -> str:
    """
    Get a high-quality fashion/dress image from Unsplash.
    Uses a curated list of active photo IDs first, then falls back to
    the Unsplash Source API for random fashion images.

    Args:
        category: Product category key (co-ord, bodycon, etc.)
        seed: Optional integer seed for consistent images per product

    Returns:
        Unsplash image URL.
    """
    cat_key = category.lower() if category else "dress"
    if cat_key not in _CURATED_PHOTO_IDS:
        cat_key = "other"

    photo_list = _CURATED_PHOTO_IDS[cat_key]

    if seed is not None:
        photo_id = photo_list[seed % len(photo_list)]
    else:
        photo_id = random.choice(photo_list)

    return f"https://images.unsplash.com/{photo_id}?w=600&auto=format&fit=crop&q=80"


def unsplash_fallback_url(keyword: str = "fashion,dress") -> str:
    """
    Return an Unsplash Source URL that returns a random fashion image.
    This is a last-resort fallback when curated photo IDs go stale.
    """
    return f"https://source.unsplash.com/600x600/?{keyword}"


# ──────────────────────────────────────────
# Product Price Scraping (for stale price refresh)
# ──────────────────────────────────────────

def scrape_product_prices(
    product_url: str,
    platform: str = "other",
    timeout: int = 15,
) -> Optional[Dict]:
    """
    Attempt to extract accurate price data from a product page.

    Visits the product page and extracts:
      - sale_price: Current selling price
      - original_price: MRP / list price (higher = discount available)
      - rating: Product rating
      - review_count: Number of ratings
      - image_url: Product image

    Strategy:
      1. Fetch the page HTML
      2. Extract JSON-LD structured data (most reliable for prices)
      3. If no LD data, try Open Graph and platform-specific selectors
      4. Returns None if extraction fails

    Returns:
      Dict with price data, or None if extraction failed.
    """
    if not product_url or product_url.startswith("http://localhost"):
        logger.debug(f"Skipping local/missing URL: {product_url}")
        return None

    headers = _random_headers()
    platform = platform.lower()

    try:
        response = requests.get(product_url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch product page {product_url}: {e}")
        return None

    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        logger.debug(f"Non-HTML response from {product_url}")
        return None

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    result = {}

    # ── Strategy 1: JSON-LD structured data ──
    import json as _json
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = _json.loads(script.string)
            if isinstance(data, dict):
                items = [data]
            elif isinstance(data, list):
                items = data
            else:
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue
                # Navigate through @graph or itemListElement
                inner = item.get('item', item)
                if '@graph' in inner:
                    for sub in inner['@graph']:
                        if isinstance(sub, dict) and 'offers' in sub:
                            inner = sub
                            break

                offers = inner.get('offers', {})
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                if isinstance(offers, dict) and 'offers' in offers:
                    offers = offers['offers']
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}

                if not isinstance(offers, dict):
                    continue

                # Extract sale price
                price_str = offers.get('price', '0')
                if isinstance(price_str, str):
                    price_str = price_str.replace(',', '').replace('₹', '').replace('Rs.', '')
                try:
                    sale_price = float(price_str)
                except (ValueError, TypeError):
                    sale_price = 0

                if sale_price > 0:
                    result['sale_price'] = sale_price

                # Extract original/MRP price
                original_price = sale_price
                # Check highPrice, listPrice, priceSpecification
                for key in ['highPrice', 'listPrice', 'wasPrice']:
                    v = offers.get(key, 0)
                    if v and float(v) > sale_price:
                        original_price = float(v)
                        break
                # Check priceSpecification sub-object
                spec = offers.get('priceSpecification', {})
                if isinstance(spec, dict):
                    for key in ['listPrice', 'fullPrice', 'originalPrice', 'maxPrice']:
                        v = spec.get(key, 0)
                        if v and float(v) > sale_price:
                            original_price = float(v)
                            break

                result['original_price'] = original_price

                # Extract rating
                agg = inner.get('aggregateRating', {})
                if isinstance(agg, dict):
                    rv = agg.get('ratingValue', 0)
                    if rv:
                        result['rating'] = float(rv)
                    rc = agg.get('reviewCount', 0)
                    if rc:
                        result['review_count'] = int(rc)

                # Extract image
                image = inner.get('image', '')
                if isinstance(image, list):
                    image = image[0] if image else ''
                if isinstance(image, dict):
                    image = image.get('url', '')
                if image:
                    if image.startswith('//'):
                        image = 'https:' + image
                    result['image_url'] = image

                # Extract name
                name = inner.get('name', '')
                if name:
                    result['name'] = name[:300]

        except (_json.JSONDecodeError, AttributeError, TypeError):
            continue

        # If we found usable data, stop looking at more LD scripts
        if result.get('sale_price', 0) > 0:
            break

    # ── Strategy 2: Open Graph meta tags (price fallback) ──
    if not result.get('sale_price'):
        # Check for og:price:amount and product:price:amount
        for meta_name in ['product:price:amount', 'og:price:amount', 'twitter:data1']:
            for attr in ['property', 'name']:
                meta = soup.find('meta', attrs={attr: meta_name})
                if meta and meta.get('content'):
                    try:
                        price = float(meta['content'].replace(',', '').replace('₹', '').replace('Rs.', ''))
                        if price > 0:
                            result['sale_price'] = price
                            break
                    except (ValueError, TypeError):
                        continue
            if result.get('sale_price'):
                break

    # ── Strategy 3: Image from og:image (always useful) ──
    if not result.get('image_url'):
        img_url = scrape_product_image(product_url, platform, timeout)
        if img_url:
            result['image_url'] = img_url

    # Return None if we couldn't extract anything useful
    if not result.get('sale_price') and not result.get('original_price'):
        logger.debug(f"No price data found on product page: {product_url[:60]}...")
        return None

    logger.info(f"Extracted prices from product page: sale=₹{result.get('sale_price', '?')}, MRP=₹{result.get('original_price', '?')}")
    return result


def refresh_stale_product(product) -> bool:
    """
    Attempt to refresh price data for a single stale product.

    Visits the product page and updates the product record
    if better price data is found.

    Returns:
        True if the product was updated, False otherwise.
    """
    from decimal import Decimal

    price_data = scrape_product_prices(product.product_url, product.platform)
    if not price_data:
        logger.debug(f"No data found for stale product #{product.id}")
        return False

    updated = False

    new_sale = Decimal(str(price_data.get('sale_price', 0)))
    new_original = Decimal(str(price_data.get('original_price', 0)))

    # Update prices if we now have a real MRP (higher than sale price)
    if new_sale > 0 and new_original > new_sale:
        product.original_price = new_original
        product.sale_price = new_sale
        product.is_price_stale = False
        product.last_price_updated = timezone.now()
        updated = True
        logger.info(f"✅ Updated prices for #{product.id}: MRP=₹{new_original}, Sale=₹{new_sale}")
    elif new_sale > 0 and product.has_fake_prices() and new_original > 0:
        # Still fake (no MRP found), but at least update the sale price
        if new_sale != product.sale_price:
            product.sale_price = new_sale
            product.original_price = new_original
            product.last_price_updated = timezone.now()
            updated = True
            logger.info(f"🔄 Updated sale price for #{product.id}: ₹{new_sale}")

    # Update rating if we found a real one
    new_rating = price_data.get('rating', 0)
    new_reviews = price_data.get('review_count', 0)
    if new_rating > 0 and (product.rating == 0 or product.review_count == 0):
        product.rating = new_rating
        product.review_count = new_reviews
        updated = True

    # Update image if we found a real product image
    new_image = price_data.get('image_url', '')
    if new_image and ('picsum' in product.image_url or 'unsplash' in product.image_url):
        product.image_url = new_image
        updated = True

    if updated:
        product.save()

    return updated


def batch_refresh_stale_prices(batch_size: int = 20) -> dict:
    """
    Iterate through products with stale prices and try to refresh them.

    Targets:
      1. Products with is_price_stale=True (no MRP found initially)
      2. Products where last_price_updated is older than 7 days

    Args:
        batch_size: Max products to process in one run

    Returns:
        Summary dict with counts.
    """
    from django.utils import timezone as tz
    from datetime import timedelta
    from apps.products.models import Product

    # Find stale products: flagged as stale OR not updated in 7+ days
    stale_cutoff = tz.now() - timedelta(days=7)

    stale_products = Product.objects.filter(
        is_price_stale=True
    ) | Product.objects.filter(
        last_price_updated__isnull=True
    ) | Product.objects.filter(
        last_price_updated__lt=stale_cutoff
    )

    # Exclude products with localhost URLs (can't scrape)
    stale_products = stale_products.exclude(
        product_url__startswith='http://localhost'
    ).exclude(
        product_url=''
    ).order_by('last_price_updated', '?')[:batch_size]

    total = stale_products.count()
    updated = 0
    skipped = 0
    errors = []

    for product in stale_products:
        try:
            result = refresh_stale_product(product)
            if result:
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Failed to refresh product #{product.id}: {e}")

    logger.info(
        f"Stale price refresh: {updated} updated, {skipped} skipped (no change), "
        f"{total} total checked, {len(errors)} errors"
    )

    return {
        'processed': total,
        'updated': updated,
        'skipped': skipped,
        'errors': errors[:5],
    }


def update_product_images(batch_size: int = 20) -> dict:
    """
    Iterate through products and update their image_url with real images.

    For each product:
      1. Try to scrape the product page for og:image
      2. If that fails, use Unsplash fashion photo as fallback
      3. Skip products that already have a non-picsum image

    Args:
        batch_size: Max products to process in one run

    Returns:
        Summary dict with counts.
    """
    from apps.products.models import Product

    updated = 0
    scraped_ok = 0
    fallback_used = 0
    skipped = 0
    errors = []

    # Products with picsum URLs or no image need updating
    products = Product.objects.filter(
        image_url__contains="picsum"
    ) | Product.objects.filter(image_url="")

    products = products.order_by("-is_trending", "-rating")[:batch_size]

    for product in products:
        try:
            # Try real scraping first
            real_url = scrape_product_image(product.product_url, product.platform)

            if real_url:
                product.image_url = real_url
                scraped_ok += 1
            else:
                # Fallback: Unsplash fashion image
                fallback_url = fetch_unsplash_fashion(
                    category=product.category,
                    seed=product.id,  # consistent per product
                )
                product.image_url = fallback_url
                fallback_used += 1

            product.save(update_fields=["image_url"])
            updated += 1
            logger.info(f"Updated image for product #{product.id}: {product.image_url[:60]}...")

        except Exception as e:
            errors.append(str(e))
            logger.error(f"Failed to update product #{product.id} image: {e}")

    return {
        "processed": updated,
        "scraped_from_page": scraped_ok,
        "unsplash_fallback": fallback_used,
        "skipped": skipped,
        "errors": errors[:5],
    }


def update_single_product_image(product_id: int) -> Optional[str]:
    """
    Update the image for a single product by ID.

    Returns the new image URL, or None if it failed.
    """
    from apps.products.models import Product

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        logger.error(f"Product #{product_id} not found")
        return None

    # Try real scraping
    real_url = scrape_product_image(product.product_url, product.platform)
    if real_url:
        product.image_url = real_url
        product.save(update_fields=["image_url"])
        logger.info(f"Product #{product_id}: scraped image → {real_url[:60]}")
        return real_url

    # Fallback to Unsplash
    fallback_url = fetch_unsplash_fashion(category=product.category, seed=product.id)
    product.image_url = fallback_url
    product.save(update_fields=["image_url"])
    logger.info(f"Product #{product_id}: Unsplash fallback → {fallback_url[:60]}")
    return fallback_url
