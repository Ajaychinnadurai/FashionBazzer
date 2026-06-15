"""
Affiliate link builder for FashionBazzer.
Creates short, trackable links with UTM parameters for each platform.
Injects your affiliate IDs (tags) directly into the final URL.
"""
import hashlib
import logging
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from django.conf import settings

logger = logging.getLogger(__name__)

# Base URL for redirects (points to this Django backend)
REDIRECT_BASE_URL = getattr(settings, 'REDIRECT_BASE_URL', 'https://fashionbazzer-backend.onrender.com/r/')


def _ensure_trailing_slash(url: str) -> str:
    """Ensure the base URL ends with a slash."""
    return url.rstrip('/') + '/'


class LinkBuilder:
    """
    Builds trackable affiliate links with:
    - Short codes for click tracking via this Django backend
    - UTM parameters for each social platform
    - Your affiliate IDs injected into the final redirect URL
    """

    # Affiliate ID parameters to inject by platform
    AFFILIATE_PARAMS = {
        'meesho': {'aff_id': settings.MEESHO_AFFILIATE_ID if hasattr(settings, 'MEESHO_AFFILIATE_ID') else ''},
        'amazon': {'tag': settings.AMAZON_ASSOCIATE_ID if hasattr(settings, 'AMAZON_ASSOCIATE_ID') else ''},
        'flipkart': {'affid': settings.FLIPKART_AFFILIATE_ID if hasattr(settings, 'FLIPKART_AFFILIATE_ID') else 'fashionbazzer'},
    }

    PLATFORM_UTM = {
        'telegram': {'utm_source': 'telegram', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'instagram': {'utm_source': 'instagram', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'facebook': {'utm_source': 'facebook', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'pinterest': {'utm_source': 'pinterest', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'twitter': {'utm_source': 'twitter', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'threads': {'utm_source': 'threads', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
    }

    def __init__(self):
        # Resolve affiliate IDs from settings at init time
        self.amazon_tag = getattr(settings, 'AMAZON_ASSOCIATE_ID', '')
        self.meesho_id = getattr(settings, 'MEESHO_AFFILIATE_ID', '')
        self.flipkart_id = getattr(settings, 'FLIPKART_AFFILIATE_ID', 'fashionbazzer')

    def build(self, affiliate_url: str, product_id: int, platform: str) -> str:
        """
        Build a tracked affiliate link with your tag injected.

        The link goes through this backend first (/r/<short_code>)
        which records the click, then redirects to the final affiliate URL
        WITH your tag/ID embedded.

        Args:
            affiliate_url: Original product or affiliate URL from the scraper
            product_id: Product ID in the database
            platform: Target social platform (telegram, instagram, etc.)

        Returns:
            Short tracked URL (e.g., https://yourdomain.com/r/abc123)
        """
        # Step 1: Inject your affiliate ID into the URL
        final_url = self._inject_affiliate_id(affiliate_url)

        # Step 2: Add UTM parameters for the platform
        final_url = self.add_utm(final_url, platform)

        # Step 3: Create short code pointing to the enriched URL
        short_code = self._generate_short_code(final_url, product_id, platform)

        # Step 4: Save to database
        self._save_tracked_link(short_code, final_url, product_id, platform)

        base = _ensure_trailing_slash(REDIRECT_BASE_URL)
        return f"{base}{short_code}"

    def _inject_affiliate_id(self, url: str) -> str:
        """
        Inject your affiliate ID/tag into the URL.
        Works with Amazon, Flipkart, Meesho, and generic URLs.
        """
        if not url:
            return url

        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        params = parse_qs(parsed.query, keep_blank_values=True)

        # Amazon: use ?tag=your-id-21
        if domain.endswith('.amazon.in') or domain.endswith('.amazon.com') or domain == 'amzn.in':
            if self.amazon_tag:
                params['tag'] = [self.amazon_tag]
                logger.info(f"Injected Amazon tag: {self.amazon_tag}")

        # Flipkart: use ?affid=your-id
        elif domain.endswith('.flipkart.com'):
            params['affid'] = [self.flipkart_id]
            logger.info(f"Injected Flipkart affid: {self.flipkart_id}")

        # Meesho: use ?aff_id=your-id
        elif domain.endswith('.meesho.com'):
            if self.meesho_id:
                params['aff_id'] = [self.meesho_id]
                logger.info(f"Injected Meesho aff_id: {self.meesho_id}")

        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    def _generate_short_code(self, url: str, product_id: int, platform: str) -> str:
        """Generate a unique 8-character short code."""
        raw = f"{product_id}{platform}{url}{hashlib.sha256(url.encode()).hexdigest()}"
        return hashlib.md5(raw.encode()).hexdigest()[:8]

    def _save_tracked_link(self, short_code: str, affiliate_url: str, product_id: int, platform: str):
        """Save tracked link to database."""
        from .models import TrackedLink

        try:
            TrackedLink.objects.get_or_create(
                short_code=short_code,
                defaults={
                    'affiliate_url': affiliate_url,
                    'product_id': product_id,
                    'platform': platform,
                }
            )
        except Exception as e:
            logger.error(f"Failed to save tracked link: {e}")

    @staticmethod
    def add_utm(url: str, platform: str) -> str:
        """Add UTM parameters to a URL for a specific platform."""
        utm_params = LinkBuilder.PLATFORM_UTM.get(platform, {})
        if not utm_params:
            return url

        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)

        # Only add UTM params that aren't already present
        for key, value in utm_params.items():
            if key not in params:
                params[key] = [value]

        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))
