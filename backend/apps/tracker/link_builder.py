"""
Affiliate link builder for FashionBazzer.
Creates short, trackable links with UTM parameters for each platform.
"""
import hashlib
import logging
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qs
from django.conf import settings

logger = logging.getLogger(__name__)

# Base URL for redirects (points to this Django backend)
REDIRECT_BASE_URL = settings.REDIRECT_BASE_URL if hasattr(settings, 'REDIRECT_BASE_URL') else "https://fashionbazzer-backend.onrender.com/r/"


class LinkBuilder:
    """
    Builds trackable affiliate links with:
    - Short codes for click tracking
    - UTM parameters for each social platform
    - Affiliate IDs for each platform
    """

    AFFILIATE_PARAMS = {
        'meesho': {'aff_id': settings.MEESHO_AFFILIATE_ID},
        'amazon': {'tag': settings.AMAZON_ASSOCIATE_ID},
        'flipkart': {'affid': 'fashionbazzer'},
        'cuelinks': {'id': settings.CUELINKS_ID},
    }

    PLATFORM_UTM = {
        'telegram': {'utm_source': 'telegram', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'instagram': {'utm_source': 'instagram', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'facebook': {'utm_source': 'facebook', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'pinterest': {'utm_source': 'pinterest', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'twitter': {'utm_source': 'twitter', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
        'threads': {'utm_source': 'threads', 'utm_medium': 'social', 'utm_campaign': 'fashionbazzer'},
    }

    def build(self, affiliate_url: str, product_id: int, platform: str) -> str:
        """
        Build a tracked affiliate link.

        Args:
            affiliate_url: Original affiliate URL
            product_id: Product ID in the database
            platform: Target social platform

        Returns:
            Short tracked URL (e.g., https://fashionbazzer-backend.onrender.com/r/abc123)
        """
        # Create short code
        short_code = self._generate_short_code(affiliate_url, product_id, platform)

        # Save to database
        self._save_tracked_link(short_code, affiliate_url, product_id, platform)

        return f"{REDIRECT_BASE_URL}{short_code}"

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
        """Add UTM parameters to an affiliate URL."""
        utm_params = LinkBuilder.PLATFORM_UTM.get(platform, {})
        if not utm_params:
            return url

        parsed = urlparse(url)
        existing_params = parse_qs(parsed.query)
        existing_params.update(utm_params)

        new_query = urlencode(existing_params, doseq=True)
        return parsed._replace(query=new_query).geturl()
