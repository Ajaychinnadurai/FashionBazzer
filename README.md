# 👗 FashionBazzer

**Fully Automated Affiliate Marketing Engine** — Zero human involvement, ₹0 setup cost, deployed on Render.

Target: Gen Z & Millennials (15–30) | Trending Dresses | 24+ posts/day

---

## 🚀 Quick Start

### Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FASHIONBAZZER SYSTEM                     │
├───────────────────┬─────────────────────┬───────────────────┤
│   FRONTEND        │      BACKEND        │   EXTERNAL APIs   │
│   React + CSS     │   Django + DRF      │                   │
│                   │   APScheduler       │  - Amazon PA API  │
│   - Dashboard     │   Pillow (images)   │  - Meesho API     │
│   - Analytics     │   Hugging Face AI   │  - Telegram Bot   │
│   - Post Manager  │   SQLite/Postgres   │  - Meta Graph API │
│                   │                     │  - Pinterest API  │
└───────────────────┴─────────────────────┴───────────────────┘
```

## 📡 Automation Schedule (24+ posts/day)

| Platform | Times (IST) | Posts/Day |
|----------|-------------|-----------|
| Telegram | 6AM, 8AM, 10AM, 12PM, 2PM, 4PM, 6PM, 8PM, 10PM | **9** |
| Instagram | 9AM, 1PM, 8PM | 3 |
| Facebook | 10AM, 2PM, 7PM | 3 |
| Pinterest | 8AM, 12PM, 5PM, 10PM | 4 |
| Twitter/X | 9AM, 3PM, 9PM | 3 |
| Threads | 9:30AM, 6:30PM | 2 |
| **Total** | | **24+** |

## 🔧 Automated Jobs (11 jobs, IST timezone)

| Job | Frequency | Description |
|-----|-----------|-------------|
| Product Scraping | Every 6h (3,9,15,21 IST) | Scrapes Meesho & Amazon for trending dresses |
| AI Content Gen | Every 2h | Generates captions + composes images (auto-recycles if queue low) |
| Content Recycle | 4,8,12,16,20,23 IST | Re-generates content for existing products to keep pipeline full |
| Telegram Posting | 6AM–10PM every 2h (9x/day) | Highest frequency — best reach for Indian audience |
| Instagram Posting | 9AM, 1PM, 8PM | Feed posts with product images |
| Facebook Posting | 10AM, 2PM, 7PM | Page photo posts |
| Pinterest Posting | 8AM, 12PM, 5PM, 10PM | Pins with tracked affiliate links |
| Twitter/X Posting | 9AM, 3PM, 9PM | Tweets with images |
| Threads Posting | 9:30AM, 6:30PM | Casual thread-style posts |
| Commission Sync | Daily at midnight IST | Syncs earnings from all affiliate platforms |
| Connection Health | Every 30 minutes | Checks all platform API connections |

> **Smart Pipeline**: When the pending queue drops below 10, Telegram job auto-triggers content generation. Dedicated recycle job (6x/day) re-processes existing products with fresh captions and taglines. Pipeline never runs dry.

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List all products |
| GET | `/api/products/trending/` | Top 10 trending |
| GET | `/api/queue/` | View post queue |
| POST | `/api/queue/generate/` | Trigger AI content gen |
| POST | `/api/queue/publish-now/` | Force publish |
| GET | `/api/analytics/overview/` | Dashboard stats |
| GET | `/api/analytics/clicks/` | Click analytics |
| GET | `/api/analytics/earnings/` | Earnings breakdown |
| GET | `/api/platforms/status/` | Platform connections |
| POST | `/api/platforms/test/` | Test connection |
| GET | `/r/<code>/` | Redirect + track click |

## 🚢 Deploy to Render

1. Push to GitHub
2. Connect repo to [Render](https://render.com)
3. Create:
   - **Web Service**: Backend (Django)
   - **Static Site**: Frontend (React)
   - **PostgreSQL**: Database
4. Set environment variables
5. 🚀 Deploy — everything runs automatically!

## 📊 Revenue Projection

| Month | Earnings (₹) |
|-------|-------------|
| Month 1 | 500 – 2,000 |
| Month 2 | 2,000 – 6,000 |
| Month 3 | 6,000 – 15,000 |
| Month 6 | 30,000 – 80,000 |

## 🎯 Target Audience

- Age: 15–30 (Gen Z & Millennials)
- Location: India
- Interests: Budget fashion, trending dresses, college wear
- Platforms: Telegram, Instagram, Pinterest (highest engagement)
