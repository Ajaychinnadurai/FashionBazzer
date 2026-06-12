"""
Instagram automated poster using Meta Graph API.
Requires a Facebook Business account and Instagram Business profile.
"""
import logging
import requests
from django.conf import settings
from apps.poster.models import PostLog

logger = logging.getLogger(__name__)


class InstagramPoster:
    """Posts product content to Instagram using the Meta Graph API."""

    GRAPH_API_URL = "https://graph.facebook.com/v19.0"

    def __init__(self):
        self.access_token = settings.META_ACCESS_TOKEN
        self.ig_user_id = settings.INSTAGRAM_USER_ID

    def send(self, post_obj) -> bool:
        """
        Send a post to Instagram feed.
        Uses the Meta Content Publishing API (2-step process).
        """
        if not self.access_token or not self.ig_user_id:
            logger.error("Instagram API credentials not configured")
            return False

        if not post_obj.public_image_url:
            logger.error("No public image URL for Instagram post")
            return False

        try:
            # Step 1: Create media container
            container_url = (
                f"{self.GRAPH_API_URL}/{self.ig_user_id}/media"
            )

            container_response = requests.post(
                container_url,
                data={
                    'image_url': post_obj.public_image_url,
                    'caption': post_obj.instagram_caption[:2200],
                    'access_token': self.access_token,
                },
                timeout=30,
            )

            if container_response.status_code != 200:
                error_data = container_response.json()
                PostLog.objects.create(
                    post=post_obj,
                    platform='instagram',
                    status='failed',
                    error_message=error_data.get('error', {}).get('message', 'Unknown error'),
                )
                return False

            container_id = container_response.json().get('id')
            if not container_id:
                return False

            # Step 2: Publish the container
            publish_url = (
                f"{self.GRAPH_API_URL}/{self.ig_user_id}/media_publish"
            )
            publish_response = requests.post(
                publish_url,
                data={
                    'creation_id': container_id,
                    'access_token': self.access_token,
                },
                timeout=30,
            )

            if publish_response.status_code == 200:
                media_id = publish_response.json().get('id', '')
                PostLog.objects.create(
                    post=post_obj,
                    platform='instagram',
                    platform_post_id=media_id,
                    status='success',
                )
                logger.info(f"Posted to Instagram: {media_id}")
                return True
            else:
                error_data = publish_response.json()
                PostLog.objects.create(
                    post=post_obj,
                    platform='instagram',
                    status='failed',
                    error_message=error_data.get('error', {}).get('message', 'Publish failed'),
                )
                return False

        except requests.RequestException as e:
            logger.error(f"Instagram API request failed: {e}")
            PostLog.objects.create(
                post=post_obj,
                platform='instagram',
                status='failed',
                error_message=str(e),
            )
            return False

    def test_connection(self) -> dict:
        """Test Instagram API connection."""
        if not self.access_token or not self.ig_user_id:
            return {'connected': False, 'error': 'Credentials not configured'}

        try:
            response = requests.get(
                f"{self.GRAPH_API_URL}/{self.ig_user_id}",
                params={
                    'fields': 'id,username,name',
                    'access_token': self.access_token,
                },
                timeout=15,
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'connected': True,
                    'username': data.get('username', ''),
                    'name': data.get('name', ''),
                }
            else:
                return {'connected': False, 'error': 'Invalid token'}
        except requests.RequestException as e:
            return {'connected': False, 'error': str(e)}
