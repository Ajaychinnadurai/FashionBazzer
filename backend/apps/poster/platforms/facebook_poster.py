"""
Facebook automated poster for FashionBazzer.
Posts to a Facebook Page using the Meta Graph API.
"""
import logging
import requests
from django.conf import settings
from apps.poster.models import PostLog

logger = logging.getLogger(__name__)


class FacebookPoster:
    """Posts product content to a Facebook Page."""

    GRAPH_API_URL = "https://graph.facebook.com/v19.0"

    def __init__(self):
        self.access_token = settings.FB_PAGE_ACCESS_TOKEN or settings.META_ACCESS_TOKEN
        self.page_id = settings.FB_PAGE_ID

    def send(self, post_obj) -> bool:
        """
        Send a post to the Facebook Page feed.
        """
        if not self.access_token or not self.page_id:
            logger.error("Facebook API credentials not configured")
            return False

        try:
            url = f"{self.GRAPH_API_URL}/{self.page_id}/photos"

            response = requests.post(
                url,
                data={
                    'url': post_obj.public_image_url or '',
                    'message': post_obj.facebook_caption[:63206],
                    'access_token': self.access_token,
                },
                timeout=30,
            )

            if response.status_code == 200:
                post_id = response.json().get('id', '')
                PostLog.objects.create(
                    post=post_obj,
                    platform='facebook',
                    platform_post_id=post_id,
                    status='success',
                )
                logger.info(f"Posted to Facebook: {post_id}")
                return True
            else:
                error_data = response.json()
                PostLog.objects.create(
                    post=post_obj,
                    platform='facebook',
                    status='failed',
                    error_message=error_data.get('error', {}).get('message', 'Unknown'),
                )
                return False

        except requests.RequestException as e:
            logger.error(f"Facebook API error: {e}")
            PostLog.objects.create(
                post=post_obj,
                platform='facebook',
                status='failed',
                error_message=str(e),
            )
            return False

    def test_connection(self) -> dict:
        """Test Facebook Page API connection."""
        if not self.access_token or not self.page_id:
            return {'connected': False, 'error': 'Credentials not configured'}

        try:
            response = requests.get(
                f"{self.GRAPH_API_URL}/{self.page_id}",
                params={
                    'fields': 'id,name,fan_count',
                    'access_token': self.access_token,
                },
                timeout=15,
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'connected': True,
                    'page_name': data.get('name', ''),
                    'followers': data.get('fan_count', 0),
                }
            return {'connected': False, 'error': response.text[:200]}
        except requests.RequestException as e:
            return {'connected': False, 'error': str(e)}
