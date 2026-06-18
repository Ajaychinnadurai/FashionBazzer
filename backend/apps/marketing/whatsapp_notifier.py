"""
WhatsApp notification service for FashionBazzer.
Sends daily summaries and platform alerts via the Twilio WhatsApp API.

Uses Twilio's WhatsApp Sandbox (free to test). To receive messages:
1. Sign up at twilio.com and activate the WhatsApp Sandbox
2. Send the join code (e.g. "join fashion-bazzer") to the sandbox number from your phone
3. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER, and WHATSAPP_TO_NUMBER

If credentials are missing, messages are logged to the console instead.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from django.conf import settings
from django.utils import timezone

from apps.tracker.analytics import AnalyticsEngine
from apps.products.models import Product
from apps.poster.models import PostQueue

logger = logging.getLogger(__name__)


def format_inr(amount) -> str:
    """Format a number as Indian Rupees with commas."""
    try:
        val = float(amount)
        if val >= 10000000:
            return f"₹{val / 10000000:.2f}Cr"
        elif val >= 100000:
            return f"₹{val / 100000:.2f}L"
        else:
            return f"₹{val:,.0f}"
    except (ValueError, TypeError):
        return "₹0"


def _get_platform_emoji(platform: str) -> str:
    emojis = {
        'telegram': '✈️', 'instagram': '📸', 'facebook': '👍',
        'pinterest': '📌', 'twitter': '🐦', 'threads': '🧵',
        'meesho': '🛍️', 'amazon': '🛒', 'flipkart': '📦',
        'myntra': '👗', 'ajio': '🛍️',
    }
    return emojis.get(platform.lower(), '🔗')


def build_digest_message() -> str:
    """
    Build a daily WhatsApp digest message with key stats.
    Returns a plain-text message (WhatsApp doesn't support rich HTML).
    """
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    stats = AnalyticsEngine.get_dashboard_stats()
    platform_status = AnalyticsEngine.get_platform_status()

    total_products = stats.get('total_products', 0)
    total_clicks = stats.get('total_clicks', 0)
    total_earnings = stats.get('total_earnings', 0)
    total_posts = stats.get('total_posts', 0)
    total_conversions = stats.get('total_conversions', 0)
    conversion_rate = stats.get('conversion_rate', 0)
    today_clicks = stats.get('today_clicks', 0)
    today_earnings = stats.get('today_earnings', 0)
    active_platforms = stats.get('active_platforms', 0)

    pending_posts = PostQueue.objects.filter(status='pending').count()
    published_today = PostQueue.objects.filter(
        status='published',
        published_at__gte=today,
    ).count()

    # Platform health summary
    connected = [p for p in platform_status if p.get('is_connected')]
    disconnected = [p for p in platform_status if not p.get('is_connected')]
    health_line = ""
    if connected:
        health_line += "✅ " + ", ".join(p['display_name'] for p in connected[:4])
    if disconnected:
        if health_line:
            health_line += "\n"
        health_line += "❌ " + ", ".join(p['display_name'] for p in disconnected[:3])
    if not platform_status:
        health_line = "ℹ️ No platforms configured yet"

    # Products scraped today (last 24h)
    products_today = Product.objects.filter(created_at__gte=today).count()
    products_by_platform = {}
    for plat in ['meesho', 'amazon', 'flipkart', 'myntra', 'ajio']:
        count = Product.objects.filter(platform=plat).count()
        if count > 0:
            emoji = _get_platform_emoji(plat)
            products_by_platform[plat] = (emoji, count)

    products_line = ""
    if products_by_platform:
        products_line = "\n".join(
            f"  {e} {p.title()}: {c}" for p, (e, c) in products_by_platform.items()
        )

    # Top product
    top_products = AnalyticsEngine.get_top_products(limit=3)
    top_line = ""
    if top_products:
        top_line = "🏆 Top Products:\n"
        for i, prod in enumerate(top_products[:3], 1):
            top_line += f"  {i}. {prod['product_name'][:35]} — {format_inr(prod['earnings'])}\n"

    date_str = now.strftime('%A, %B %d')

    message = f"""📊 *FashionBazzer Daily Digest*
{date_str}

📈 *Today's Activity*
  👆 Clicks: {today_clicks:,}
  💰 Earnings: {format_inr(today_earnings)}
  📤 Posts Published: {published_today}
  🆕 New Products: {products_today}

📊 *All-Time Stats*
  👆 Total Clicks: {total_clicks:,}
  💰 Total Earnings: {format_inr(total_earnings)}
  🛒 Conversions: {total_conversions} ({conversion_rate}%)
  📦 Total Products: {total_products}
  📤 Total Posts: {total_posts}
  ⏳ Pending Posts: {pending_posts}

📦 *Product Sources*
{products_line if products_line else "  No products scraped yet"}

🔌 *Platform Health*
{health_line}

{top_line}
⚡ *FashionBazzer* — Fully Automated
🔗 https://fashionbazzer-frontend.onrender.com"""

    return message


def build_alert_message(platform: str, error: str) -> str:
    """
    Build an alert message when a platform connection fails.
    """
    emoji = _get_platform_emoji(platform)
    return f"""🚨 *Platform Connection Alert*

{emoji} *{platform.title()}* just failed!

Error: {error[:200]}

🔧 Check your API credentials in the Render dashboard.
📊 View full status: Dashboard → Platform Status

⚡ *FashionBazzer* — Automated Monitoring"""


def send_whatsapp(message_body: str) -> Dict:
    """
    Send a WhatsApp message via Twilio API.
    Falls back to console logging if credentials are missing.

    Returns a dict with status and details.
    """
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_WHATSAPP_NUMBER
    to_number = settings.WHATSAPP_TO_NUMBER

    if not all([account_sid, auth_token, from_number, to_number]):
        logger.info("📱 WhatsApp notification (not configured — logging to console)")
        logger.info(f"  To: {to_number or 'Not set'}")
        logger.info(f"  Message:\n{message_body}")
        logger.info("  ℹ️  To enable, set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
                     "TWILIO_WHATSAPP_NUMBER, and WHATSAPP_TO_NUMBER in your environment.")
        return {
            'status': 'logged',
            'method': 'console',
            'message': 'WhatsApp message logged to console (credentials not configured)',
        }

    try:
        from twilio.rest import Client

        client = Client(account_sid, auth_token)

        # Ensure numbers are in whatsapp: format
        if not from_number.startswith('whatsapp:'):
            from_number = f'whatsapp:{from_number}'
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'

        twilio_message = client.messages.create(
            from_=from_number,
            body=message_body,
            to=to_number,
        )

        logger.info(f"📱 WhatsApp message sent to {to_number} (SID: {twilio_message.sid})")
        return {
            'status': 'sent',
            'method': 'twilio',
            'sid': twilio_message.sid,
            'to': to_number,
        }

    except Exception as e:
        logger.error(f"📱 Failed to send WhatsApp message: {e}")
        return {
            'status': 'error',
            'method': 'twilio',
            'error': str(e),
        }


def send_daily_digest() -> Dict:
    """
    Send the daily WhatsApp digest.
    Called by APScheduler at 9AM IST daily.
    """
    logger.info("📱 Building daily WhatsApp digest...")
    try:
        message = build_digest_message()
        result = send_whatsapp(message)
        logger.info(f"📱 Daily digest result: {result.get('status')}")
        return result
    except Exception as e:
        logger.error(f"📱 Failed to build/send daily digest: {e}")
        return {'status': 'error', 'error': str(e)}


def send_platform_alert(platform: str, error: str) -> Dict:
    """
    Send an alert when a platform connection fails.
    Used by the platform connection checker.
    """
    logger.info(f"📱 Sending platform alert for {platform}...")
    try:
        message = build_alert_message(platform, error)
        result = send_whatsapp(message)
        return result
    except Exception as e:
        logger.error(f"📱 Failed to send platform alert: {e}")
        return {'status': 'error', 'error': str(e)}
