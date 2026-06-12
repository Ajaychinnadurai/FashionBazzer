"""
Pinterest automated pin poster for FashionBazzer.
Uses Pinterest API v5 to create pins.
Auto-resolves board name to board ID at runtime.
"""
import logging
import requests
from django.conf import settings
from apps.poster.models import PostLog

logger = logging.getLogger(__name__)


class PinterestPoster:
    """Creates Pinterest pins for product content."""

    API_URL = "https://api.pinterest.com/v5"

    def __init__(self):
        self.access_token = settings.PINTEREST_ACCESS_TOKEN
        self._board_name = settings.PINTEREST_BOARD_NAME
        self._board_id = settings.PINTEREST_BOARD_ID
        # Cache the resolved board ID so we only look it up once per session
        self._resolved_board_id = None

    @staticmethod
    def _is_url(value: str) -> bool:
        """Check if a string looks like a URL (not a Pinterest board ID)."""
        return value.startswith(('http://', 'https://', 'www.'))

    @property
    def board_id(self) -> str | None:
        """
        Returns the board ID.
        - If PINTEREST_BOARD_ID is set AND is not a URL, uses it directly.
        - Otherwise, looks up the board by name (PINTEREST_BOARD_NAME).
        Result is cached after first successful resolution.
        """
        if self._resolved_board_id:
            return self._resolved_board_id

        if self._board_id and not self._is_url(self._board_id):
            # Direct numeric ID provided — use as-is
            self._resolved_board_id = self._board_id
            return self._board_id

        if self._board_id and self._is_url(self._board_id):
            logger.warning(f"PINTEREST_BOARD_ID looks like a URL, ignoring. Will resolve by name.")

        if not self._board_name:
            logger.error("Neither valid PINTEREST_BOARD_ID nor PINTEREST_BOARD_NAME is configured")
            return None

        # Look up board by name
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            url = f"{self.API_URL}/boards?page_size=100"
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                boards = response.json().get('items', [])
                # Normalize name for comparison (case-insensitive, dash/space tolerant)
                search_name = self._board_name.lower().replace('-', ' ').replace('_', ' ')
                for board in boards:
                    board_name = board.get('name', '').lower().strip()
                    if search_name == board_name:
                        self._resolved_board_id = board['id']
                        logger.info(f"Resolved board '{board_name}' -> ID: {board['id']}")
                        return self._resolved_board_id

                # Fallback: partial match
                for board in boards:
                    board_name = board.get('name', '').lower().strip()
                    if search_name in board_name or board_name in search_name:
                        self._resolved_board_id = board['id']
                        logger.info(f"Resolved board (partial match) '{board_name}' -> ID: {board['id']}")
                        return self._resolved_board_id

                logger.error(f"No Pinterest board found matching '{self._board_name}'. Available: {[b['name'] for b in boards]}")
            else:
                logger.error(f"Failed to fetch Pinterest boards: {response.status_code} {response.text[:200]}")
        except requests.RequestException as e:
            logger.error(f"Error resolving Pinterest board ID: {e}")

        return None

    def send(self, post_obj) -> bool:
        """
        Create a pin on Pinterest with the product image and link.
        """
        if not self.access_token:
            logger.error("Pinterest access token not configured")
            return False

        bid = self.board_id
        if not bid:
            logger.error("Pinterest board ID could not be resolved")
            return False

        try:
            url = f"{self.API_URL}/pins"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            payload = {
                "board_id": bid,
                "media_source": {
                    "source_type": "image_url",
                    "url": post_obj.public_image_url,
                },
                "title": post_obj.product.name[:100],
                "description": post_obj.pinterest_caption[:500],
                "link": post_obj.product.affiliate_url or post_obj.product.product_url,
                "alt_text": f"{post_obj.product.name[:50]} - FashionBazzer",
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code in (200, 201):
                pin_data = response.json()
                PostLog.objects.create(
                    post=post_obj,
                    platform='pinterest',
                    platform_post_id=pin_data.get('id', ''),
                    status='success',
                )
                logger.info(f"Pinned to Pinterest: {pin_data.get('id', '')}")
                return True
            else:
                error_body = response.json()
                error_msg = error_body.get('message', error_body.get('error', 'Unknown error'))
                PostLog.objects.create(
                    post=post_obj,
                    platform='pinterest',
                    status='failed',
                    error_message=error_msg,
                )
                logger.error(f"Pinterest API error: {error_msg}")
                return False

        except requests.RequestException as e:
            logger.error(f"Pinterest API error: {e}")
            PostLog.objects.create(
                post=post_obj,
                platform='pinterest',
                status='failed',
                error_message=str(e),
            )
            return False

    def test_connection(self) -> dict:
        """Test Pinterest API connection and resolve board."""
        if not self.access_token:
            return {'connected': False, 'error': 'Access token not configured'}

        try:
            # Delegate to the property — it fetches boards, caches result
            bid = self.board_id

            if self._resolved_board_id:
                # Property already fetched boards and resolved the ID
                return {
                    'connected': True,
                    'resolved_board_id': bid,
                    'board_name': self._board_name,
                    'note': 'Board resolved successfully',
                }

            # If resolution failed, try a basic token check
            response = requests.get(
                f"{self.API_URL}/boards?page_size=5",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=15,
            )
            if response.status_code == 200:
                boards = response.json().get('items', [])
                return {
                    'connected': True,
                    'boards_found': len(boards),
                    'board_names': [b['name'] for b in boards],
                    'warning': f"Board '{self._board_name}' not found among your boards",
                }
            elif response.status_code == 401:
                return {'connected': False, 'error': 'Token expired or invalid. Regenerate at https://developers.pinterest.com/'}
            return {'connected': False, 'error': response.text[:300]}
        except requests.RequestException as e:
            return {'connected': False, 'error': str(e)}
