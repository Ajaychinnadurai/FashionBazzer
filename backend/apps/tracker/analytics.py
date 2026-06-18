"""
Analytics engine for FashionBazzer.
Handles click aggregation, conversion tracking, and commission reporting.
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone

from django.conf import settings
from .models import TrackedLink, Click, Commission, PlatformConnection
from apps.products.models import Product
from apps.poster.models import PostQueue, PostLog


logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Aggregates analytics data for the dashboard."""

    @staticmethod
    def get_dashboard_stats() -> Dict:
        """Get high-level dashboard statistics."""
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total_clicks = TrackedLink.objects.aggregate(
            total=Sum('click_count')
        )['total'] or 0

        today_clicks = Click.objects.filter(
            clicked_at__gte=today_start
        ).count()

        total_earnings = Commission.objects.aggregate(
            total=Sum('amount', filter=Q(status='approved'))
        )['total'] or Decimal('0')

        today_earnings = Commission.objects.filter(
            recorded_at__gte=today_start, status='approved'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        total_posts = PostQueue.objects.count()
        total_products = Product.objects.count()
        total_conversions = Commission.objects.filter(
            status='approved'
        ).count()

        active_platforms = PlatformConnection.objects.filter(
            is_connected=True
        ).count()

        conversion_rate = 0.0
        if total_clicks > 0:
            conversion_rate = round((total_conversions / total_clicks) * 100, 2)

        return {
            'total_clicks': total_clicks,
            'total_earnings': total_earnings,
            'total_posts': total_posts,
            'total_products': total_products,
            'total_conversions': total_conversions,
            'today_clicks': today_clicks,
            'today_earnings': today_earnings,
            'active_platforms': active_platforms,
            'conversion_rate': conversion_rate,
        }

    @staticmethod
    def get_clicks_by_platform(days: int = 30) -> List[Dict]:
        """Get click data grouped by platform for the last N days."""
        since = timezone.now() - timedelta(days=days)

        links = TrackedLink.objects.values('platform').annotate(
            total_clicks=Sum('click_count'),
        ).filter(
            created_at__gte=since
        ).order_by('-total_clicks')

        result = []
        for item in links:
            result.append({
                'platform': item['platform'],
                'clicks': item['total_clicks'] or 0,
            })

        return result

    @staticmethod
    def get_earnings_breakdown(days: int = 30) -> List[Dict]:
        """Get commission breakdown by affiliate platform."""
        since = timezone.now() - timedelta(days=days)

        commissions = Commission.objects.values('affiliate_platform').annotate(
            total=Sum('amount'),
            pending=Sum('amount', filter=Q(status='pending')),
            approved=Sum('amount', filter=Q(status='approved')),
            count=Count('id'),
        ).filter(recorded_at__gte=since)

        return [
            {
                'platform': c['affiliate_platform'],
                'total_earnings': c['total'] or Decimal('0'),
                'pending': c['pending'] or Decimal('0'),
                'approved': c['approved'] or Decimal('0'),
                'transactions': c['count'],
            }
            for c in commissions
        ]

    @staticmethod
    def get_top_products(limit: int = 10) -> List[Dict]:
        """Get top performing products by clicks and conversions."""
        top_links = TrackedLink.objects.select_related('product').annotate(
            total_clicks=Sum('click_count'),
        ).order_by('-total_clicks')[:limit]

        result = []
        for link in top_links:
            result.append({
                'product_id': link.product.id,
                'product_name': link.product.name[:60],
                'price': link.product.sale_price,
                'platform': link.platform,
                'clicks': link.click_count,
                'conversions': Commission.objects.filter(
                    product=link.product, status='approved'
                ).count(),
                'earnings': Commission.objects.filter(
                    product=link.product, status='approved'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0'),
            })

        return result

    @staticmethod
    def get_platform_status() -> List[Dict]:
        """Get connection status for all platforms."""
        connections = PlatformConnection.objects.all()
        if not connections:
            return [
                {'platform': p, 'is_connected': False}
                for p in ['telegram', 'instagram', 'facebook', 'pinterest', 'twitter', 'threads']
            ]

        return [
            {
                'platform': c.platform,
                'display_name': c.get_platform_display(),
                'is_connected': c.is_connected,
                'last_checked': c.last_checked,
                'error_message': c.error_message,
                'posts_today': c.posts_today,
            }
            for c in connections
        ]


    @staticmethod
    def get_caption_performance(days: int = 30) -> List[Dict]:
        """
        Get performance metrics grouped by caption style and platform.
        Shows which caption styles drive the most clicks per platform.
        """
        since = timezone.now() - timedelta(days=days)

        # Join PostQueue -> Product -> TrackedLink to get clicks per caption_style per platform
        from django.db.models import Sum, Count

        # Get all published posts with their caption styles
        posts = PostQueue.objects.filter(
            status='published',
            created_at__gte=since,
        ).exclude(caption_style='').values('caption_style').annotate(
            total_posts=Count('id'),
        ).order_by('-total_posts')

        # Get clicks per caption style by joining through Product -> TrackedLink
        caption_clicks = {}
        for post in posts:
            style = post['caption_style']
            # Find all TrackedLinks for products that had posts with this style
            product_ids = PostQueue.objects.filter(
                caption_style=style,
                status='published',
                created_at__gte=since,
            ).values_list('product_id', flat=True).distinct()

            links = TrackedLink.objects.filter(
                product_id__in=list(product_ids),
                created_at__gte=since,
            ).values('platform').annotate(
                total_clicks=Sum('click_count'),
                total_links=Count('id'),
            )

            # Aggregate clicks per platform for this style
            total_clicks = 0
            platform_breakdown = {}
            for link in links:
                platform = link['platform']
                clicks = link['total_clicks'] or 0
                total_clicks += clicks
                platform_breakdown[platform] = clicks

            if total_clicks > 0 or post['total_posts'] > 0:
                caption_clicks[style] = {
                    'caption_style': style,
                    'total_posts': post['total_posts'],
                    'total_clicks': total_clicks,
                    'clicks_per_post': round(total_clicks / post['total_posts'], 1) if post['total_posts'] > 0 else 0,
                    'platforms': platform_breakdown,
                }

        # Sort by total clicks descending
        result = sorted(caption_clicks.values(), key=lambda x: x['total_clicks'], reverse=True)

        return result


class CommissionSync:
    """Sync commission data from affiliate platforms."""

    def run_all(self) -> Dict:
        """Sync commissions from all configured affiliate platforms."""
        results = {}
        platforms = ['meesho', 'amazon', 'flipkart']
        for platform in platforms:
            try:
                count = self.sync_platform(platform)
                results[platform] = {'synced': count}
            except Exception as e:
                results[platform] = {'error': str(e)}
        return results

    def sync_platform(self, platform: str) -> int:
        """Fetch and save commission data for a specific platform.

        Production behavior: integrate with the affiliate network APIs.

        Dev/demo behavior: OFF by default. We never create fake commissions
        automatically because it can pollute dashboard analytics.
        """
        # Disable all demo commission creation unless explicitly enabled.
        # This prevents “fallback/demo data” from showing up in production dashboards.
        demo_enabled = getattr(settings, 'FASHIONBAZZER_DEMO_COMMISSION_SYNC', False)
        if not demo_enabled:
            logger.info(
                "Commission sync skipped for %s (demo mode disabled)",
                platform,
            )
            return 0

        # Demo mode (manual/test only): create sample commission records.
        products = Product.objects.filter(platform=platform)[:5]
        count = 0

        for product in products:
            click_count = product.tracked_links.aggregate(
                total=Sum('click_count')
            )['total'] or 0

            if click_count > 0 and not Commission.objects.filter(
                product=product,
                affiliate_platform=platform,
                recorded_at__date=timezone.now().date(),
            ).exists():
                estimated_commission = float(product.sale_price) * 0.08 * min(click_count / 100, 1)
                if estimated_commission > 0:
                    Commission.objects.create(
                        product=product,
                        affiliate_platform=platform,
                        amount=Decimal(str(round(estimated_commission, 2))),
                        status='pending',
                    )
                    count += 1

        return count

