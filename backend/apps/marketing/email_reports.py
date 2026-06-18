"""
Daily email report service for FashionBazzer.
Generates a rich HTML summary of daily analytics and sends it via SendGrid.

Uses the free tier (100 emails/day, 60-day trial). If no SENDGRID_API_KEY
is configured, the report is logged to the console instead.
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string

from apps.tracker.analytics import AnalyticsEngine
from apps.products.models import Product
from apps.poster.models import PostQueue

logger = logging.getLogger(__name__)


def format_inr(amount) -> str:
    """Format a number as Indian Rupees with en-IN locale."""
    try:
        val = float(amount)
        if val >= 10000000:  # 1 crore+
            return f"₹{val / 10000000:.2f}Cr"
        elif val >= 100000:  # 1 lakh+
            return f"₹{val / 100000:.2f}L"
        elif val >= 1000:
            return f"₹{val:,.0f}"
        else:
            return f"₹{val:.0f}"
    except (ValueError, TypeError):
        return "₹0"


def format_number(n) -> str:
    """Format a number with Indian-style commas."""
    try:
        val = int(n)
        return f"{val:,}"
    except (ValueError, TypeError):
        return "0"


def _get_platform_emoji(platform: str) -> str:
    """Return an emoji for the given platform name."""
    emojis = {
        'telegram': '✈️',
        'instagram': '📸',
        'facebook': '👍',
        'pinterest': '📌',
        'twitter': '🐦',
        'threads': '🧵',
        'meesho': '🛍️',
        'amazon': '🛒',
        'flipkart': '📦',
        'myntra': '👗',
    }
    return emojis.get(platform.lower(), '🔗')


def build_report_data() -> Dict:
    """Collect all data needed for the daily email report."""
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    last_7 = today - timedelta(days=7)

    # ── Overall stats ──
    stats = AnalyticsEngine.get_dashboard_stats()

    # ── Clicks by platform (last 7 days) ──
    clicks_data = AnalyticsEngine.get_clicks_by_platform(days=7)

    # ── Top products ──
    top_products = AnalyticsEngine.get_top_products(limit=5)

    # ── Platform status ──
    platform_status = AnalyticsEngine.get_platform_status()

    # ── Post queue status ──
    pending_posts = PostQueue.objects.filter(status='pending').count()
    published_today = PostQueue.objects.filter(
        status='published',
        published_at__gte=today,
    ).count()

    # ── Today's activity ──
    today_clicks = stats.get('today_clicks', 0)
    today_earnings = stats.get('today_earnings', 0)

    # ── Product count by platform ──
    products_by_platform = {}
    for platform in ['amazon', 'flipkart', 'meesho', 'myntra']:
        count = Product.objects.filter(platform=platform).count()
        if count > 0:
            products_by_platform[platform] = count

    # ── Single category breakdown (top 5) ──
    from django.db.models import Count
    category_counts = (
        Product.objects.values('category')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    return {
        'report_date': now.strftime('%A, %B %d, %Y'),
        'report_time': now.strftime('%I:%M %p IST'),
        'total_products': stats.get('total_products', 0),
        'total_clicks': stats.get('total_clicks', 0),
        'total_earnings': format_inr(stats.get('total_earnings', 0)),
        'total_conversions': stats.get('total_conversions', 0),
        'conversion_rate': stats.get('conversion_rate', 0),
        'today_clicks': today_clicks,
        'today_earnings': format_inr(today_earnings),
        'active_platforms': stats.get('active_platforms', 0),
        'clicks_by_platform': clicks_data,
        'top_products': top_products,
        'platform_status': platform_status,
        'pending_posts': pending_posts,
        'published_today': published_today,
        'total_posts': stats.get('total_posts', 0),
        'products_by_platform': products_by_platform,
        'category_counts': list(category_counts),
        'get_platform_emoji': _get_platform_emoji,
        'format_number': format_number,
        'format_inr': format_inr,
    }


def build_html_report(data: Dict) -> str:
    """Build a beautiful HTML email from report data."""
    platform_rows = ""
    for p in data.get('clicks_by_platform', []):
        emoji = _get_platform_emoji(p['platform'])
        platform_rows += f"""
        <tr>
            <td style="padding:8px 12px;border-bottom:1px solid #eef">{emoji} {p['platform'].title()}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eef;text-align:center;font-weight:600">{format_number(p['clicks'])}</td>
        </tr>"""

    top_products_rows = ""
    for i, prod in enumerate(data.get('top_products', [])[:5], 1):
        top_products_rows += f"""
        <tr>
            <td style="padding:8px 12px;border-bottom:1px solid #eef;color:#666">{i}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eef">{prod['product_name'][:45]}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eef;text-align:center">{format_number(prod['clicks'])}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eef;text-align:center">{format_inr(prod['earnings'])}</td>
        </tr>"""

    status_icons = ""
    for p in data.get('platform_status', []):
        emoji = _get_platform_emoji(p['platform'])
        if p.get('is_connected'):
            status_icons += f'<span style="display:inline-block;margin:4px 8px 4px 0;padding:4px 10px;border-radius:12px;background:#e8f5e9;color:#2e7d32;font-size:13px">{emoji} {p["display_name"]} ✅</span>'
        else:
            status_icons += f'<span style="display:inline-block;margin:4px 8px 4px 0;padding:4px 10px;border-radius:12px;background:#fce4ec;color:#c62828;font-size:13px">{emoji} {p["display_name"]} ❌</span>'

    platform_sources = ""
    for plat, count in data.get('products_by_platform', {}).items():
        emoji = _get_platform_emoji(plat)
        platform_sources += f'<span style="display:inline-block;margin:4px 8px 4px 0;padding:4px 10px;border-radius:12px;background:#f3f4f6;color:#374151;font-size:13px">{emoji} {plat.title()} ({format_number(count)})</span>'

    category_chips = ""
    for cat in data.get('category_counts', []):
        category_chips += f'<span style="display:inline-block;margin:4px 8px 4px 0;padding:4px 10px;border-radius:12px;background:#e0f2fe;color:#0369a1;font-size:13px">{cat["category"]} ({cat["total"]})</span>'

    conversion_rate = data.get('conversion_rate', 0)
    conversion_color = "#2e7d32" if conversion_rate >= 1 else "#e65100" if conversion_rate > 0 else "#666"

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:24px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08)">
    <!-- HEADER -->
    <tr>
        <td style="background:linear-gradient(135deg,#FF3CAC,#784BA0,#2B86C5);padding:32px 24px;text-align:center">
            <h1 style="margin:0;font-size:28px;color:#fff;letter-spacing:-0.5px">📊 FashionBazzer Daily Report</h1>
            <p style="margin:8px 0 0;color:rgba(255,255,255,0.85);font-size:14px">{data['report_date']} · {data['report_time']}</p>
        </td>
    </tr>

    <!-- STATS ROW -->
    <tr>
        <td style="padding:24px 24px 8px">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="width:33%;text-align:center;padding:12px 8px">
                        <div style="font-size:24px;font-weight:700;color:#FF3CAC">{format_number(data['today_clicks'])}</div>
                        <div style="font-size:12px;color:#666;margin-top:4px">Today's Clicks</div>
                    </td>
                    <td style="width:33%;text-align:center;padding:12px 8px">
                        <div style="font-size:24px;font-weight:700;color:#00D4AA">{data['today_earnings']}</div>
                        <div style="font-size:12px;color:#666;margin-top:4px">Today's Earnings</div>
                    </td>
                    <td style="width:33%;text-align:center;padding:12px 8px">
                        <div style="font-size:24px;font-weight:700;color:#2B86C5">{format_number(data['published_today'])}</div>
                        <div style="font-size:12px;color:#666;margin-top:4px">Posts Today</div>
                    </td>
                </tr>
                <tr>
                    <td style="width:33%;text-align:center;padding:12px 8px;border-top:1px solid #f0f0f0">
                        <div style="font-size:20px;font-weight:600;color:#333">{format_number(data['total_clicks'])}</div>
                        <div style="font-size:12px;color:#666;margin-top:4px">Total Clicks</div>
                    </td>
                    <td style="width:33%;text-align:center;padding:12px 8px;border-top:1px solid #f0f0f0">
                        <div style="font-size:20px;font-weight:600;color:#333">{data['total_earnings']}</div>
                        <div style="font-size:12px;color:#666;margin-top:4px">Total Earnings</div>
                    </td>
                    <td style="width:33%;text-align:center;padding:12px 8px;border-top:1px solid #f0f0f0">
                        <div style="font-size:20px;font-weight:600;color:#333;color:{conversion_color}">{conversion_rate}%</div>
                        <div style="font-size:12px;color:#666;margin-top:4px">Conversion Rate</div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>

    <!-- CLICKS BY PLATFORM -->
    <tr><td style="padding:16px 24px 0"><h2 style="font-size:16px;margin:0;color:#333">👆 Clicks by Platform (Last 7 Days)</h2></td></tr>
    <tr><td style="padding:8px 24px">
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">
            <tr style="background:#f9fafb">
                <th style="padding:8px 12px;text-align:left;font-size:12px;color:#666;text-transform:uppercase;letter-spacing:0.5px">Platform</th>
                <th style="padding:8px 12px;text-align:center;font-size:12px;color:#666;text-transform:uppercase;letter-spacing:0.5px">Clicks</th>
            </tr>
            {platform_rows if platform_rows else '<tr><td colspan="2" style="padding:16px;text-align:center;color:#999">No click data yet</td></tr>'}
        </table>
    </td></tr>

    <!-- TOP PRODUCTS -->
    <tr><td style="padding:16px 24px 0"><h2 style="font-size:16px;margin:0;color:#333">🔥 Top Performing Products</h2></td></tr>
    <tr><td style="padding:8px 24px">
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">
            <tr style="background:#f9fafb">
                <th style="padding:8px 12px;text-align:left;font-size:12px;color:#666;text-transform:uppercase;letter-spacing:0.5px">#</th>
                <th style="padding:8px 12px;text-align:left;font-size:12px;color:#666;text-transform:uppercase;letter-spacing:0.5px">Product</th>
                <th style="padding:8px 12px;text-align:center;font-size:12px;color:#666;text-transform:uppercase;letter-spacing:0.5px">Clicks</th>
                <th style="padding:8px 12px;text-align:center;font-size:12px;color:#666;text-transform:uppercase;letter-spacing:0.5px">Earnings</th>
            </tr>
            {top_products_rows if top_products_rows else '<tr><td colspan="4" style="padding:16px;text-align:center;color:#999">No product data yet</td></tr>'}
        </table>
    </td></tr>

    <!-- INVENTORY -->
    <tr><td style="padding:16px 24px 0"><h2 style="font-size:16px;margin:0;color:#333">📦 Product Inventory</h2></td></tr>
    <tr><td style="padding:8px 24px">
        <div style="margin-bottom:8px">
            <span style="font-weight:600;font-size:14px">Sources:</span>
            <div style="margin-top:8px">{platform_sources if platform_sources else '<span style="color:#999">No products scraped yet</span>'}</div>
        </div>
        <div>
            <span style="font-weight:600;font-size:14px">Categories:</span>
            <div style="margin-top:8px">{category_chips if category_chips else '<span style="color:#999">No categories yet</span>'}</div>
        </div>
        <div style="margin-top:12px;padding:12px;background:#f9fafb;border-radius:8px;font-size:13px;color:#555">
            <strong>Total Products:</strong> {format_number(data['total_products'])} ·
            <strong>Pending Posts:</strong> {format_number(data['pending_posts'])} ·
            <strong>Total Posts:</strong> {format_number(data['total_posts'])}
        </div>
    </td></tr>

    <!-- PLATFORM STATUS -->
    <tr><td style="padding:16px 24px 0"><h2 style="font-size:16px;margin:0;color:#333">🔌 Platform Connections</h2></td></tr>
    <tr><td style="padding:8px 24px 0">
        <div>{status_icons}</div>
        <p style="font-size:12px;color:#999;margin:8px 0 16px">
            {data['active_platforms']} of 6 platforms connected
        </p>
    </td></tr>

    <!-- FOOTER -->
    <tr>
        <td style="padding:24px;text-align:center;border-top:1px solid #f0f0f0">
            <p style="margin:0;font-size:12px;color:#999">
                FashionBazzer · Automated Affiliate Marketing Engine<br>
                <a href="https://fashionbazzer-frontend.onrender.com/dashboard" style="color:#FF3CAC;text-decoration:none">Open Dashboard →</a>
            </p>
            <p style="margin:8px 0 0;font-size:11px;color:#bbb">You're receiving this because you configured daily email reports in FashionBazzer.</p>
        </td>
    </tr>
</table>
</body>
</html>"""

    return html


def send_daily_report() -> Dict:
    """
    Main entry point: build and send the daily email report.
    Called by the APScheduler daily job.

    Returns a dict with status, method used, and any error message.
    """
    if not settings.SENDGRID_API_KEY:
        # No API key — log the report data for console visibility
        data = build_report_data()
        logger.info("📧 Daily email report (SendGrid not configured — logging to console)")
        logger.info(f"  📊 Stats: {data['total_products']} products, {data['total_clicks']} clicks, {data['total_earnings']} earnings")
        logger.info(f"  📈 Today: {data['today_clicks']} clicks, {data['today_earnings']} earnings, {data['published_today']} posts")
        logger.info(f"  🔌 Platforms: {data['active_platforms']}/6 connected, {data['pending_posts']} pending posts")
        logger.info("  ℹ️  To enable email delivery, set SENDGRID_API_KEY and REPORT_EMAIL in your environment.")
        return {
            'status': 'logged',
            'method': 'console',
            'message': 'Report data logged to console (no SENDGRID_API_KEY configured)',
        }

    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content

        data = build_report_data()
        html_content = build_html_report(data)

        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        from_email = Email(settings.REPORT_FROM_EMAIL or 'reports@fashionbazzer.com')
        to_email = To(settings.REPORT_EMAIL)

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
        )
        message.subject = f"📊 FashionBazzer Daily Report — {data['report_date']}"
        message.content = Content("text/html", html_content)

        response = sg.send(message)

        logger.info(f"📧 Daily report sent to {settings.REPORT_EMAIL} (status: {response.status_code})")
        return {
            'status': 'sent',
            'method': 'sendgrid',
            'status_code': response.status_code,
            'recipient': settings.REPORT_EMAIL,
        }

    except Exception as e:
        logger.error(f"📧 Failed to send daily report via SendGrid: {e}")
        return {
            'status': 'error',
            'method': 'sendgrid',
            'error': str(e),
        }
