"""
Twitter/X automated poster for FashionBazzer.
Uses Tweepy library to post tweets with images.
"""
import logging
import tweepy
from django.conf import settings
from apps.poster.models import PostLog

logger = logging.getLogger(__name__)


class TwitterPoster:
    """Posts product content to Twitter/X."""

    def __init__(self):
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        self.access_token = settings.TWITTER_ACCESS_TOKEN
        self.access_secret = settings.TWITTER_ACCESS_SECRET
        self.client = None
        self.api_v1 = None

        if all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            try:
                # v2 API for tweeting
                self.client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_secret,
                )
                # v1.1 API for media upload
                auth = tweepy.OAuth1UserHandler(
                    self.api_key, self.api_secret,
                    self.access_token, self.access_secret,
                )
                self.api_v1 = tweepy.API(auth)
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")

    def send(self, post_obj) -> bool:
        """
        Post a tweet with product image.
        Uses v1.1 API for media upload and v2 API for tweeting.
        """
        if not self.client or not self.api_v1:
            logger.error("Twitter client not initialized")
            return False

        try:
            # Step 1: Upload media using v1.1 API
            media = self.api_v1.media_upload(post_obj.image_path)

            # Step 2: Create tweet with media
            tweet = self.client.create_tweet(
                text=post_obj.twitter_caption[:280],
                media_ids=[media.media_id],
            )

            tweet_id = tweet.data.get('id', '')
            PostLog.objects.create(
                post=post_obj,
                platform='twitter',
                platform_post_id=str(tweet_id),
                status='success',
            )
            logger.info(f"Posted to Twitter/X: {tweet_id}")
            return True

        except FileNotFoundError:
            logger.error(f"Image not found: {post_obj.image_path}")
            PostLog.objects.create(
                post=post_obj,
                platform='twitter',
                status='failed',
                error_message='Image not found',
            )
            return False

        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error: {e}")
            PostLog.objects.create(
                post=post_obj,
                platform='twitter',
                status='failed',
                error_message=str(e),
            )
            return False

    def test_connection(self) -> dict:
        """Test Twitter API connection."""
        if not self.client:
            return {'connected': False, 'error': 'Credentials not configured'}

        try:
            me = self.client.get_me()
            return {
                'connected': True,
                'username': me.data.get('username', ''),
                'name': me.data.get('name', ''),
            }
        except tweepy.TweepyException as e:
            return {'connected': False, 'error': str(e)}
