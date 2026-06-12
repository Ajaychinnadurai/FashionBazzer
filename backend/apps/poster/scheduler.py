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


# ──────────────────────────────────────────
# JOB 1: Scrape trending products (every 6h)
# ──────────────────────────────────────────
def scrape_trending_products():
    """Scrape all affiliate platforms for new trending products."""
    logger.info("Starting product scraping cycle...")
    from apps.products.scrapers.meesho_scraper import MeeshoScraper
    from apps.products.scrapers.amazon_scraper import AmazonScraper
    from apps.products.scrapers.image_scraper import update_product_images

    results = {
        'meesho': MeeshoScraper().run(),
        'amazon': AmazonScraper().run(),
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
# JOB 2: Generate AI content (every 2h)
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
        pending_count = PostQueue.objects.filter(status='pending').count()
        if pending_count < 15:
            logger.info(f"Low pending queue ({pending_count}), recycling content...")
            recycle_result = generator.generate_batch(limit=8, recycle=True)
            result['recycled'] = recycle_result.get('generated', 0)
            result['total'] = result.get('generated', 0) + result.get('recycled', 0)

    logger.info(f"Content generation complete: {result}")
    return result


# ──────────────────────────────────────────
# JOB 3: Post to Telegram (9x/day — peak hours)
# ──────────────────────────────────────────
def publish_to_telegram():
    """Post pending content to Telegram channel.
    Posts every 2 hours from 6AM to 10PM IST (9 posts/day).
    If queue is low, auto-triggers content generation.
    """
    logger.info("Publishing to Telegram...")
    from .models import PostQueue
    from .platforms.telegram_poster import TelegramPoster

    posts = PostQueue.objects.filter(status='pending').order_by('-created_at')[:5]
    poster = TelegramPoster()

    published = 0
    for post in posts:
        success = poster.send(post)
        if success:
            post.status = 'published'
            post.published_at = timezone.now()
            post.save()
            published += 1

    logger.info(f"Published {published}/{len(posts)} posts to Telegram")

    # Auto-top-up: if queue is running low, trigger content generation
    remaining = PostQueue.objects.filter(status='pending').count()
    if remaining < 10:
        logger.info(f"Low pending queue ({remaining}), auto-triggering content generation...")
        from apps.content.ai_generator import ContentGenerator
        try:
            generator = ContentGenerator()
            gen_result = generator.generate_batch(limit=10, recycle=True)
            logger.info(f"Auto-generated {gen_result.get('generated', 0)} more posts")
        except Exception as e:
            logger.error(f"Auto content generation failed: {e}")


# ──────────────────────────────────────────
# JOB 4: Post to Instagram (3x/day)
# ──────────────────────────────────────────
def publish_to_instagram():
    """Post pending content to Instagram."""
    from .models import PostQueue
    from .platforms.instagram_poster import InstagramPoster

    posts = PostQueue.objects.filter(status='pending').order_by('-created_at')[:3]
    poster = InstagramPoster()
    for post in posts:
        success = poster.send(post)
        if success:
            post.status = 'published'
            post.published_at = timezone.now()
            post.save()


# ──────────────────────────────────────────
# JOB 5: Post to Facebook (3x/day)
# ──────────────────────────────────────────
def publish_to_facebook():
    """Post pending content to Facebook Page."""
    from .models import PostQueue
    from .platforms.facebook_poster import FacebookPoster

    posts = PostQueue.objects.filter(status='pending').order_by('-created_at')[:3]
    poster = FacebookPoster()
    for post in posts:
        poster.send(post)


# ──────────────────────────────────────────
# JOB 6: Post to Pinterest (4x/day)
# ──────────────────────────────────────────
def publish_to_pinterest():
    """Create Pinterest pins from pending content."""
    from .models import PostQueue
    from .platforms.pinterest_poster import PinterestPoster

    posts = PostQueue.objects.filter(status='pending').order_by('-created_at')[:4]
    poster = PinterestPoster()
    for post in posts:
        poster.send(post)


# ──────────────────────────────────────────
# JOB 7: Post to Twitter/X (3x/day)
# ──────────────────────────────────────────
def publish_to_twitter():
    """Post tweets with product images."""
    from .models import PostQueue
    from .platforms.twitter_poster import TwitterPoster

    posts = PostQueue.objects.filter(status='pending').order_by('-created_at')[:3]
    poster = TwitterPoster()
    for post in posts:
        poster.send(post)


# ──────────────────────────────────────────
# JOB 8: Post to Threads (2x/day)
# ──────────────────────────────────────────
def publish_to_threads():
    """Post content to Threads."""
    from .models import PostQueue
    from .platforms.threads_poster import ThreadsPoster

    posts = PostQueue.objects.filter(status='pending').order_by('-created_at')[:2]
    poster = ThreadsPoster()
    for post in posts:
        poster.send(post)


# ──────────────────────────────────────────
# JOB 9: Content Recycle (6x/day)
# ──────────────────────────────────────────
def recycle_content():
    """
    Recycle content for products that have already been posted.
    This ensures the pipeline never runs dry.
    """
    logger.info("Starting content recycle cycle...")
    from apps.content.ai_generator import ContentGenerator
    from .models import PostQueue

    pending_count = PostQueue.objects.filter(status='pending').count()
    if pending_count >= 20:
        logger.info(f"Pending queue healthy ({pending_count}), skipping recycle")
        return

    generator = ContentGenerator()
    result = generator.generate_batch(limit=12, recycle=True)
    logger.info(f"Content recycle complete: {result}")


# ──────────────────────────────────────────
# JOB 10: Sync affiliate commissions (daily)
# ──────────────────────────────────────────
def sync_commissions():
    """Sync commission data from all affiliate platforms."""
    logger.info("Syncing affiliate commissions...")
    from apps.tracker.analytics import CommissionSync

    syncer = CommissionSync()
    result = syncer.run_all()
    logger.info(f"Commission sync complete: {result}")


# ──────────────────────────────────────────
# JOB 11: Update platform status (every 30min)
# ──────────────────────────────────────────
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

            conn, _ = PlatformConnection.objects.get_or_create(platform=platform_name)
            conn.is_connected = result.get('connected', False)
            conn.error_message = result.get('error', '')
            conn.save()
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

    success = True
    posters = [
        TelegramPoster(),
        InstagramPoster(),
        FacebookPoster(),
        PinterestPoster(),
        TwitterPoster(),
        ThreadsPoster(),
    ]

    for poster in posters:
        try:
            if not poster.send(post_obj):
                success = False
        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            success = False

    if success:
        post_obj.status = 'published'
        post_obj.published_at = timezone.now()
        post_obj.save()

    return success
