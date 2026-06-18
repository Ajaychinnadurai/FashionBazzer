"""
Telegram automated poster for FashionBazzer.
Posts product images with captions to Telegram channel.
Using direct HTTP API for synchronous operation.
"""
import logging
import requests
from django.conf import settings
from apps.poster.models import PostLog

logger = logging.getLogger(__name__)


class TelegramPoster:
    """Posts product content to Telegram channel."""

    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.channel_id = settings.TELEGRAM_CHANNEL_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send(self, post_obj) -> bool:
        """
        Send a post to the Telegram channel.
        Returns True if successful, False otherwise.
        """
        if not self.bot_token:
            logger.error("Telegram bot token not configured")
            return False

        if not self.channel_id:
            logger.error("Telegram channel ID not configured")
            return False

        try:
            # Upload photo with caption
            with open(post_obj.image_path, 'rb') as photo:
                response = requests.post(
                    f"{self.api_url}/sendPhoto",
                    files={'photo': photo},
                    data={
                        'chat_id': self.channel_id,
                        'caption': post_obj.telegram_caption[:4096],
                        'parse_mode': 'HTML',
                    },
                    timeout=30,
                )

            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    message_id = result['result']['message_id']
                    PostLog.objects.create(
                        post=post_obj,
                        platform='telegram',
                        platform_post_id=str(message_id),
                        status='success',
                    )
                    logger.info(f"Posted to Telegram: {message_id}")
                    return True

            error_msg = response.json().get('description', 'Unknown error')
            logger.error(f"Telegram API error: {error_msg}")
            PostLog.objects.create(
                post=post_obj,
                platform='telegram',
                status='failed',
                error_message=error_msg,
            )
            return False

        except FileNotFoundError:
            logger.error(f"Image not found: {post_obj.image_path}")
            PostLog.objects.create(
                post=post_obj,
                platform='telegram',
                status='failed',
                error_message=f"Image not found: {post_obj.image_path}",
            )
            return False

        except requests.RequestException as e:
            logger.error(f"Telegram request failed: {e}")
            PostLog.objects.create(
                post=post_obj,
                platform='telegram',
                status='failed',
                error_message=str(e),
            )
            return False

    def test_connection(self) -> dict:
        """Test if the Telegram bot is properly configured."""
        if not self.bot_token:
            return {'connected': False, 'error': 'Bot token not configured'}

        try:
            response = requests.get(
                f"{self.api_url}/getMe",
                timeout=15,
            )
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    bot_info = result['result']
                    return {
                        'connected': True,
                        'bot_name': bot_info.get('username', ''),
                        'bot_id': bot_info.get('id', ''),
                    }
            return {'connected': False, 'error': 'Invalid token'}
        except requests.RequestException as e:
            return {'connected': False, 'error': str(e)}
