"""
APScheduler automation engine for FashionBazzer.
Handles all scheduled jobs for scraping, content generation, posting, and commission sync.

Posting Schedule (IST):
- Telegram: 6AM, 8AM, 10AM, 12PM, 2PM, 4PM, 6PM, 8PM, 10PM   (9x/day)
- Instagram: 9AM, 1PM, 8PM       (3x/day)
- Facebook: 10AM, 2PM, 7PM       (3x/day)
- Pinterest: 8AM, 12PM, 5PM, 10PM (4x/day)
- Twitter/X: 9AM, 3PM, 9PM        (3x/day)
- Threads: 9:30AM, 6:30PM        (2x/day)
- Content Recycle: Every 4h (auto-refills pipeline)
Total: 24+ posts/day - Zero human work!
"""
import logging
import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# IST timezone for all cron triggers
IST = pytz.timezone('Asia/Kolkata')

# ── Scheduler instance (lazy singleton) ──
_scheduler = None


def get_scheduler() -> BackgroundScheduler:
    """Return the singleton scheduler, creating it if needed."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone=IST)
        _scheduler.add_jobstore(DjangoJobStore(), "default")
    return _scheduler



def get_pending_posts_for_platform(platform_name: str, limit: int):
    """
    Get posts that are 'pending' but have NOT yet been successfully published to the specified platform.
    """
    from django.db.models import Exists, OuterRef
    from .models import PostQueue, PostLog

    # Check if a successful log exists for this post and platform
    already_posted = PostLog.objects.filter(
        post=OuterRef('pk'),
        platform=platform_name,
        status='success'
    )

    # Get pending posts that do not have a successful log for this platform
    return PostQueue.objects.filter(
        status='pending'
    ).annotate(
        already_sent=Exists(already_posted)
    ).filter(
        already_sent=False
    ).order_by('-created_at')[:limit]


def update_post_status(post):
    """
    Check if a post has been processed on all active platforms,
    and update its status accordingly.
    """
    from apps.tracker.models import PlatformConnection
    from .models import PostLog

    active_platforms = set(
        PlatformConnection.objects.filter(is_connected=True).values_list('platform', flat=True)
    )

    # If no platforms are configured/connected, default to telegram to avoid getting stuck
    if not active_platforms:
        active_platforms = {'telegram'}

    successful_platforms = set(
        PostLog.objects.filter(post=post, status='success').values_list('platform', flat=True)
    )

    # If the post has been successfully posted to all active platforms, mark it as published
    if active_platforms.issubset(successful_platforms):
        post.status = 'published'
        post.published_at = timezone.now()
        post.save(update_fields=['status', 'published_at'])


# ──────────────────────────────────────────
# JOB 1: Scrape trending products (every 6h)
# ──────────────────────────────────────────
def scrape_trending_products():
    """Scrape all affiliate platforms for new trending products."""
    logger.info("Starting product scraping cycle...")
    from apps.products.scrapers.meesho_scraper import MeeshoScraper
    from apps.products.scrapers.amazon_scraper import AmazonScraper
    from apps.products.scrapers.flipkart_scraper import FlipkartScraper
    from apps.products.scrapers.myntra_scraper import MyntraScraper
    from apps.products.scrapers.ajio_scraper import AjioScraper
    from apps.products.scrapers.earnkaro_scraper import EarnKaroScraper
    from apps.products.scrapers.image_scraper import update_product_images

    results = {
        'meesho': MeeshoScraper().run(),
        'amazon': AmazonScraper().run(),
        'flipkart': FlipkartScraper().run(),
        'myntra': MyntraScraper().run(),
        'ajio': AjioScraper().run(),
        'earnkaro': EarnKaroScraper().run(),
    }

    # After scraping, update product images (scrape product pages for real images)
    try:
        image_result = update_product_images(batch_size=20)
        results['images_updated'] = image_result
        logger.info(f"Image scraping complete: {image_result}")
    except Exception as e:
        logger.error(f"Image scraping failed: {e}")
        results['images_updated'] = {'error': str(e)}

    logger.info(f"Scraping cycle complete: {results}")
    return results


# ──────────────────────────────────────────
# JOB 2: Check Festival/Sale Event Boost (daily at 6AM)
# ──────────────────────────────────────────
def check_event_boost():
    """Check for active shopping events and log boost status.
    During peak events like Diwali/BBD/Prime Day, this automatically
    increases posting frequency and scraping intensity.
    """
    from apps.content.festival_booster import get_booster
    booster = get_booster()
    info = booster.get_boost_info()
    log_line = booster.get_event_log_line()

    if info['has_active_boost']:
        logger.info(
            f"🚀 EVENT BOOST ACTIVE: {info['multiplier']}x multiplier | "
            f"Events: {', '.join(info['events'])} | "
            f"Theme: {info['theme']} | "
            f"Keywords: {info['extra_keywords'][:5]}"
        )
    else:
        logger.info(f"{log_line}")

    return info


# ──────────────────────────────────────────
# JOB 3: Generate AI content (every 2h)
# ──────────────────────────────────────────
def generate_content():
    """Generate AI captions and compose images for new products.
    Also recycles content for already-processed products if pending queue is low.
    """
    logger.info("Starting AI content generation...")
    from apps.content.ai_generator import ContentGenerator

    generator = ContentGenerator()

    # First try fresh products (no tagline yet)
    result = generator.generate_batch(limit=10)

    # If few posts were generated, recycle existing products to refill pipeline
    if result.get('generated', 0) < 5:
        from apps.poster.models import PostQueue
        from apps.content.festival_booster import get_booster
        booster = get_booster()
        threshold = booster.get_boosted_queue_threshold()
        pending_count = PostQueue.objects.filter(status='pending').count()
        if pending_count < threshold:
            logger.info(f"Low pending queue ({pending_count}), recycling content...")
            recycle_result = generator.generate_batch(limit=8, recycle=True)
            result['recycled'] = recycle_result.get('generated', 0)
            result['total'] = result.get('generated', 0) + result.get('recycled', 0)

    logger.info(f"Content generation complete: {result}")
    return result


# ──────────────────────────────────────────
# JOB 4: Post to Telegram (9x/day — peak hours, boosted during events)
# ──────────────────────────────────────────
def publish_to_telegram():
    """Post pending content to Telegram channel.
    Posts every 2 hours from 6AM to 10PM IST (9 posts/day).
    If queue is low, auto-triggers content generation.
    """
    logger.info("Publishing to Telegram...")
    from .platforms.telegram_poster import TelegramPoster

    from apps.content.festival_booster import get_booster
    booster = get_booster()
    base_limit = 5
    limit = booster.get_boosted_post_limit(base_limit)

    posts = get_pending_posts_for_platform('telegram', limit=limit)
    poster = TelegramPoster()

    published = 0
    for post in posts:
        success = poster.send(post)
        if success:
            published += 1
            update_post_status(post)

    logger.info(f"Published {published}/{len(posts)} posts to Telegram (boost limit: {limit})")

    # Auto-top-up: if queue is running low, trigger content generation
    from .models import PostQueue
    threshold = booster.get_boosted_queue_threshold()
    remaining = PostQueue.objects.filter(status='pending').count()
    if remaining < threshold:
        logger.info(f"Low pending queue ({remaining} < {threshold}), auto-triggering content generation...")
        from apps.content.ai_generator import ContentGenerator
        try:
            generator = ContentGenerator()
            batch_size = booster.get_boosted_post_limit(10)
            gen_result = generator.generate_batch(limit=batch_size, recycle=True)
            logger.info(f"Auto-generated {gen_result.get('generated', 0)} more posts")
        except Exception as e:
            logger.error(f"Auto content generation failed: {e}")


# ──────────────────────────────────────────
# JOB 5: Post to Instagram (3x/day, boosted during events)
# ──────────────────────────────────────────
def publish_to_instagram():
    """Post pending content to Instagram."""
    from .platforms.instagram_poster import InstagramPoster
    from apps.content.festival_booster import get_booster

    limit = get_booster().get_boosted_post_limit(3)
    posts = get_pending_posts_for_platform('instagram', limit=limit)
    poster = InstagramPoster()
    for post in posts:
        success = poster.send(post)
        if success:
            update_post_status(post)


# ──────────────────────────────────────────
# JOB 6: Post to Facebook (3x/day, boosted during events)
# ──────────────────────────────────────────
def publish_to_facebook():
    """Post pending content to Facebook Page."""
    from .platforms.facebook_poster import FacebookPoster
    from apps.content.festival_booster import get_booster

    limit = get_booster().get_boosted_post_limit(3)
    posts = get_pending_posts_for_platform('facebook', limit=limit)
    poster = FacebookPoster()
    for post in posts:
        success = poster.send(post)
        if success:
            update_post_status(post)


# ──────────────────────────────────────────
# JOB 7: Post to Pinterest (4x/day, boosted during events)
# ──────────────────────────────────────────
def publish_to_pinterest():
    """Create Pinterest pins from pending content."""
    from .platforms.pinterest_poster import PinterestPoster
    from apps.content.festival_booster import get_booster

    limit = get_booster().get_boosted_post_limit(4)
    posts = get_pending_posts_for_platform('pinterest', limit=limit)
    poster = PinterestPoster()
    for post in posts:
        success = poster.send(post)
        if success:
            update_post_status(post)


# ──────────────────────────────────────────
# JOB 8: Post to Twitter/X (3x/day, boosted during events)
# ──────────────────────────────────────────
def publish_to_twitter():
    """Post tweets with product images."""
    from .platforms.twitter_poster import TwitterPoster
    from apps.content.festival_booster import get_booster

    limit = get_booster().get_boosted_post_limit(3)
    posts = get_pending_posts_for_platform('twitter', limit=limit)
    poster = TwitterPoster()
    for post in posts:
        success = poster.send(post)
        if success:
            update_post_status(post)


# ──────────────────────────────────────────
# JOB 9: Post to Threads (2x/day, boosted during events)
# ──────────────────────────────────────────
def publish_to_threads():
    """Post content to Threads."""
    from .platforms.threads_poster import ThreadsPoster
    from apps.content.festival_booster import get_booster

    limit = get_booster().get_boosted_post_limit(2)
    posts = get_pending_posts_for_platform('threads', limit=limit)
    poster = ThreadsPoster()
    for post in posts:
        success = poster.send(post)
        if success:
            update_post_status(post)


# ──────────────────────────────────────────
# JOB 10: Content Recycle (6x/day, boosted during events)
# ──────────────────────────────────────────
def recycle_content():
    """
    Recycle content for products that have already been posted.
    This ensures the pipeline never runs dry.
    During events, threshold increases to keep more posts ready.
    """
    logger.info("Starting content recycle cycle...")
    from apps.content.ai_generator import ContentGenerator
    from apps.content.festival_booster import get_booster
    from .models import PostQueue

    booster = get_booster()
    threshold = booster.get_boosted_queue_threshold()
    pending_count = PostQueue.objects.filter(status='pending').count()
    if pending_count >= threshold:
        logger.info(f"Pending queue healthy ({pending_count} >= {threshold}), skipping recycle")
        return

    batch_size = booster.get_boosted_post_limit(12)
    generator = ContentGenerator()
    result = generator.generate_batch(limit=batch_size, recycle=True)
    logger.info(f"Content recycle complete: {result}")


# ──────────────────────────────────────────
# JOB 11: Sync affiliate commissions (daily)
# ──────────────────────────────────────────
def sync_commissions():
    """Sync commission data from all affiliate platforms."""
    logger.info("Syncing affiliate commissions...")
    from apps.tracker.analytics import CommissionSync

    syncer = CommissionSync()
    result = syncer.run_all()
    logger.info(f"Commission sync complete: {result}")


# ──────────────────────────────────────────
# JOB 12: Send daily email report (8AM IST)
# ──────────────────────────────────────────
def send_daily_report():
    """Send the daily analytics email report via SendGrid (at 8AM IST)."""
    logger.info("Sending daily email report...")
    from apps.marketing.email_reports import send_daily_report as _send_report
    result = _send_report()
    logger.info(f"Daily report result: {result}")
    return result


def send_whatsapp_digest():
    """Send the daily WhatsApp digest (at 9AM IST)."""
    logger.info("Sending WhatsApp daily digest...")
    from apps.marketing.whatsapp_notifier import send_daily_digest
    result = send_daily_digest()
    logger.info(f"WhatsApp digest result: {result}")
    return result


# ──────────────────────────────────────────
# JOB 13: Refresh stale product prices (weekly, Sunday 4AM IST)
# ──────────────────────────────────────────
def refresh_stale_prices():
    """
    Refresh price data for products with stale/missing price info.

    Visits product pages of:
    - Products flagged is_price_stale=True (no MRP found initially)
    - Products whose last_price_updated is older than 7 days

    Extracts JSON-LD structured data from product pages to find
    real MRP/original prices, updating records when found.
    Also refreshes product images in the same pass.
    """
    logger.info("Starting stale price refresh cycle...")
    from apps.products.scrapers.image_scraper import batch_refresh_stale_prices

    result = batch_refresh_stale_prices(batch_size=30)

    logger.info(f"Stale price refresh complete: {result}")
    return result


def check_platform_connections():
    """Check and update connection status for all platforms."""
    from apps.tracker.models import PlatformConnection

    platforms_to_check = [
        ('telegram', 'apps.poster.platforms.telegram_poster.TelegramPoster'),
        ('instagram', 'apps.poster.platforms.instagram_poster.InstagramPoster'),
        ('facebook', 'apps.poster.platforms.facebook_poster.FacebookPoster'),
        ('pinterest', 'apps.poster.platforms.pinterest_poster.PinterestPoster'),
        ('twitter', 'apps.poster.platforms.twitter_poster.TwitterPoster'),
    ]

    for platform_name, poster_path in platforms_to_check:
        try:
            module_path, class_name = poster_path.rsplit('.', 1)
            import importlib
            module = importlib.import_module(module_path)
            poster_class = getattr(module, class_name)
            result = poster_class().test_connection()

            was_connected = False
            try:
                existing = PlatformConnection.objects.get(platform=platform_name)
                was_connected = existing.is_connected
            except PlatformConnection.DoesNotExist:
                pass

            conn, _ = PlatformConnection.objects.get_or_create(platform=platform_name)
            conn.is_connected = result.get('connected', False)
            conn.error_message = result.get('error', '')
            conn.save()

            # Alert on new disconnection (platform was connected but now is not)
            if was_connected and not result.get('connected', False):
                error_msg = result.get('error', 'Unknown error')
                logger.warning(f"Platform {platform_name} went down! Sending alert...")
                from apps.marketing.whatsapp_notifier import send_platform_alert
                try:
                    send_platform_alert(platform_name, error_msg)
                except Exception as alert_e:
                    logger.error(f"Failed to send platform alert: {alert_e}")
        except Exception as e:
            logger.error(f"Connection check failed for {platform_name}: {e}")


# ── Job definitions (registered by start_scheduler) ──
SCHEDULER_JOBS = [
    {
        'fn': scrape_trending_products,
        'trigger': CronTrigger(hour="3,9,15,21", minute=0, timezone=IST),
        'id': 'scrape_products',
    },
    {
        'fn': check_event_boost,
        'trigger': CronTrigger(hour=6, minute=0, timezone=IST),
        'id': 'check_event_boost',
    },
    {
        'fn': generate_content,
        'trigger': CronTrigger(hour="*/2", minute=15, timezone=IST),
        'id': 'generate_content',
    },
    {
        'fn': publish_to_telegram,
        'trigger': CronTrigger(hour="6,8,10,12,14,16,18,20,22", minute=0, timezone=IST),
        'id': 'post_telegram',
    },
    {
        'fn': publish_to_instagram,
        'trigger': CronTrigger(hour="9,13,20", minute=0, timezone=IST),
        'id': 'post_instagram',
    },
    {
        'fn': publish_to_facebook,
        'trigger': CronTrigger(hour="10,14,19", minute=0, timezone=IST),
        'id': 'post_facebook',
    },
    {
        'fn': publish_to_pinterest,
        'trigger': CronTrigger(hour="8,12,17,22", minute=0, timezone=IST),
        'id': 'post_pinterest',
    },
    {
        'fn': publish_to_twitter,
        'trigger': CronTrigger(hour="9,15,21", minute=30, timezone=IST),
        'id': 'post_twitter',
    },
    {
        'fn': publish_to_threads,
        'trigger': CronTrigger(hour="9,18", minute=30, timezone=IST),
        'id': 'post_threads',
    },
    {
        'fn': recycle_content,
        'trigger': CronTrigger(hour="4,8,12,16,20,23", minute=30, timezone=IST),
        'id': 'recycle_content',
    },
    {
        'fn': sync_commissions,
        'trigger': CronTrigger(hour=0, minute=0, timezone=IST),
        'id': 'sync_commissions',
    },
    {
        'fn': check_platform_connections,
        'trigger': CronTrigger(minute="*/30"),
        'id': 'check_connections',
    },
    {
        'fn': send_daily_report,
        'trigger': CronTrigger(hour=8, minute=0, timezone=IST),
        'id': 'send_daily_report',
    },
    {
        'fn': send_whatsapp_digest,
        'trigger': CronTrigger(hour=9, minute=0, timezone=IST),
        'id': 'send_whatsapp_digest',
    },
    {
        'fn': refresh_stale_prices,
        # Weekly on Sunday at 4:00 AM IST
        'trigger': CronTrigger(day_of_week='sun', hour=4, minute=0, timezone=IST),
        'id': 'refresh_stale_prices',
    },
]


def start_scheduler():
    """Initialize and start the APScheduler with all automation jobs."""
    scheduler = get_scheduler()

    # Register all jobs
    for job_def in SCHEDULER_JOBS:
        scheduler.add_job(
            job_def['fn'],
            trigger=job_def['trigger'],
            id=job_def['id'],
            replace_existing=True,
            misfire_grace_time=300,
        )

    # Log any active event boost
    try:
        from apps.content.festival_booster import get_booster
        boost_info = get_booster().get_boost_info()
        if boost_info['has_active_boost']:
            logger.info(f"🎉 Event boost active on startup: {boost_info['multiplier']}x | {' '.join(boost_info['events'])}")
    except Exception:
        pass

    # Register connection cleanup event listener
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
    
    def cleanup_db_connections(event):
        from django.db import close_old_connections
        try:
            close_old_connections()
        except Exception as e:
            logger.error(f"Error in scheduler connection cleanup: {e}")
            
    scheduler.add_listener(cleanup_db_connections, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # Start the scheduler (no-op if already running)
    if not scheduler.running:
        scheduler.start()
        logger.info("FashionBazzer automation scheduler started successfully!")
        logger.info("""
    ┌──────────────────────────────────────────────────┐
    │   SCHEDULE: 24+ posts/day | 11 automation jobs   │
    │   ├─ Products:   Every 6 hours                   │
    │   ├─ Content:    Every 2 hours                   │
    │   ├─ Recycle:    4,8,12,16,20,23 (6x/day)       │
    │   ├─ Telegram:   6AM-10PM every 2h (9x/day)      │
    │   ├─ Instagram:  9AM, 1PM, 8PM                  │
    │   ├─ Facebook:   10AM, 2PM, 7PM                 │
    │   ├─ Pinterest:  8AM, 12PM, 5PM, 10PM           │
    │   ├─ Twitter:    9AM, 3PM, 9PM                  │
    │   ├─ Threads:    9:30AM, 6:30PM                 │
    │   ├─ Commissions: Daily at midnight IST          │
    │   └─ Connections: Every 30 minutes               │
    └──────────────────────────────────────────────────┘
        """)

    return scheduler


def publish_post_to_all(post_obj) -> bool:
    """
    Publish a single post to all configured platforms.
    Used for manual "publish now" action.
    """
    from .platforms.telegram_poster import TelegramPoster
    from .platforms.instagram_poster import InstagramPoster
    from .platforms.facebook_poster import FacebookPoster
    from .platforms.pinterest_poster import PinterestPoster
    from .platforms.twitter_poster import TwitterPoster
    from .platforms.threads_poster import ThreadsPoster

    posters = [
        ('telegram', TelegramPoster()),
        ('instagram', InstagramPoster()),
        ('facebook', FacebookPoster()),
        ('pinterest', PinterestPoster()),
        ('twitter', TwitterPoster()),
        ('threads', ThreadsPoster()),
    ]

    attempted = 0
    succeeded = 0

    for name, poster in posters:
        # Check if platform is configured
        is_configured = False
        if name == 'telegram':
            is_configured = bool(poster.bot_token and poster.channel_id)
        elif name == 'instagram':
            is_configured = bool(poster.access_token and poster.ig_user_id)
        elif name == 'facebook':
            is_configured = bool(poster.access_token and poster.page_id)
        elif name == 'pinterest':
            is_configured = bool(poster.access_token and (poster._board_name or poster._board_id))
        elif name == 'twitter':
            is_configured = poster.client is not None
        elif name == 'threads':
            is_configured = bool(poster.access_token and poster.ig_user_id)

        if not is_configured:
            logger.info(f"Skipping unconfigured platform for manual publish: {name}")
            continue

        attempted += 1
        try:
            if poster.send(post_obj):
                succeeded += 1
            else:
                logger.warning(f"Manual post to {name} returned False")
        except Exception as e:
            logger.error(f"Manual posting failed for {name}: {e}")

    # Mark as published if at least one attempt succeeded,
    # or if no platforms are configured (to avoid posts getting stuck forever)
    if succeeded > 0 or attempted == 0:
        post_obj.status = 'published'
        post_obj.published_at = timezone.now()
        post_obj.save()
        return True
    
    post_obj.status = 'failed'
    post_obj.save()
    return False

