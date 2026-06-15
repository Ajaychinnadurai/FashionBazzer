"""
WhatsApp poster for FashionBazzer.
Sends product notifications via WhatsApp API.
Currently supports share links (wa.me) and can be extended with WhatsApp Business API.
"""
import logging
import urllib.parse
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class WhatsAppPoster:
    """
    WhatsApp product sharing and notifications.

    Current features:
    - Generate wa.me share links for products
    - Send product notifications (placeholder for WhatsApp Business API integration)

    Future: Full WhatsApp Business API integration for automated messaging.
    """

    PLATFORM_NAME = "whatsapp"

    def __init__(self, phone_number: Optional[str] = None):
        self.phone_number = phone_number or "911234567890"  # Placeholder

    def generate_share_link(self, product_name: str, price: float, affiliate_link: str, tagline: str = "") -> str:
        """
        Generate a wa.me share link for a product.

        Args:
            product_name: Name of the product
            price: Sale price
            affiliate_link: Tracked affiliate link
            tagline: Optional AI tagline

        Returns:
            wa.me URL with pre-filled message
        """
        message = (
            f"👗 Check this out!\n\n"
            f"{product_name}\n"
            f"💰 ₹{int(price)}\n"
        )
        if tagline:
            message += f"✨ {tagline}\n"
        message += f"\n🛒 Shop: {affiliate_link}\n\n#FashionBazzer"

        encoded = urllib.parse.quote(message)
        return f"https://wa.me/{self.phone_number}?text={encoded}"

    def send(self, post_obj) -> bool:
        """
        Send a product notification via WhatsApp.
        Currently logs the action and returns True.
        Will be extended with WhatsApp Business API.

        Args:
            post_obj: PostQueue instance

        Returns:
            True (placeholder for future API integration)
        """
        product = post_obj.product
        share_link = self.generate_share_link(
            product_name=product.name,
            price=product.sale_price,
            affiliate_link=product.affiliate_url or product.product_url,
            tagline=getattr(product, 'ai_tagline', ''),
        )

        logger.info(f"[WhatsApp] Share link generated for product #{product.id}: {share_link}")
        return True

    def test_connection(self) -> Dict:
        """
        Test WhatsApp configuration.

        Returns:
            Dict with connection status
        """
        return {
            'connected': True,
            'platform': 'whatsapp',
            'note': 'WhatsApp sharing uses wa.me links. Full API integration coming soon.',
            'share_link_example': self.generate_share_link("Sample Dress", 499, "https://example.com"),
        }
