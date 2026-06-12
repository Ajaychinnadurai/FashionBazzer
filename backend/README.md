# FashionBazzer Backend

Automated affiliate marketing engine for trending dresses.
Built with Django + DRF + APScheduler.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## API Endpoints

- `GET /api/products/` - List all products
- `GET /api/products/trending/` - Top trending products
- `GET /api/queue/` - Post queue
- `POST /api/queue/generate/` - Generate AI content
- `POST /api/queue/publish-now/` - Force publish
- `GET /api/analytics/overview/` - Dashboard stats
- `GET /api/analytics/clicks/` - Click analytics
- `GET /api/analytics/earnings/` - Earnings breakdown
- `GET /api/platforms/status/` - Platform connections
- `POST /api/platforms/test/` - Test platform connection
- `GET /r/<short_code>/` - Redirect + track click

## Automation Schedule (24+ posts/day, IST timezone)

| Job | Frequency | Description |
|-----|-----------|-------------|
| Scrape products | Every 6h (3,9,15,21 IST) | Meesho & Amazon |
| Generate content | Every 2h | AI captions + image composition |
| Content recycle | 4,8,12,16,20,23 IST | Re-refills pipeline from existing products |
| Post to Telegram | 6AM–10PM every 2h (9x/day) | 5 posts per batch |
| Post to Instagram | 9AM, 1PM, 8PM | Feed posts |
| Post to Facebook | 10AM, 2PM, 7PM | Page photo posts |
| Post to Pinterest | 8AM, 12PM, 5PM, 10PM | Pins with affiliate links |
| Post to Twitter | 9AM, 3PM, 9PM | Tweets with images |
| Post to Threads | 9:30AM, 6:30PM | Thread-style posts |
| Sync commissions | Daily 12AM IST | Affiliate earnings sync |
| Check connections | Every 30 minutes | Platform API health |

**Smart Pipeline**: Auto-top-up when queue < 10. Content recycle 6x/day for fresh captions. Total: **24+ posts/day** — Zero human work!

