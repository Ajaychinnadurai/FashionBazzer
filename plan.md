# 🛍️ FashionBazzer — Complete Affiliate Marketing Automation Master Plan

> **Zero Human Involvement · Free Setup · Deploy on Render · Target: Age 15–30**

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack & Architecture](#2-tech-stack--architecture)
3. [File Structure](#3-file-structure)
4. [Affiliate Platforms (Free)](#4-affiliate-platforms-free)
5. [Trending Dress Products Strategy](#5-trending-dress-products-strategy)
6. [Backend — Django Automation Engine](#6-backend--django-automation-engine)
7. [Frontend — React Dashboard](#7-frontend--react-dashboard)
8. [Social Media Automation (No Human)](#8-social-media-automation-no-human)
9. [AI Content Generation Pipeline](#9-ai-content-generation-pipeline)
10. [Earn Quickly Strategy](#10-earn-quickly-strategy)
11. [Database Schema](#11-database-schema)
12. [API Endpoints](#12-api-endpoints)
13. [Deployment on Render (Free Tier)](#13-deployment-on-render-free-tier)
14. [Automation Flow Diagram](#14-automation-flow-diagram)
15. [Free Tools & Services Used](#15-free-tools--services-used)
16. [Phase-wise Build Plan](#16-phase-wise-build-plan)
17. [Revenue Projection](#17-revenue-projection)
18. [Security & Compliance](#18-security--compliance)

---

## 1. Project Overview

**FashionBazzer** is a fully automated affiliate marketing engine targeting Gen Z and young millennials (ages 15–30) who shop for trendy, budget dresses. The system:

- Discovers trending dress products from affiliate networks
- Generates viral social media content using AI (text + image captions)
- Posts automatically to Telegram, Instagram, Facebook, Pinterest, Twitter/X, and Threads
- Tracks clicks, conversions, and commissions in real time
- Requires **zero human involvement** after initial setup
- Costs **₹0 / $0** to set up (all free tiers)
- Deploys entirely on **Render free tier**

---

## 2. Tech Stack & Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FASHIONBAZZER SYSTEM                     │
├───────────────────┬─────────────────────┬───────────────────┤
│   FRONTEND        │      BACKEND        │   EXTERNAL APIs   │
│   React + CSS     │   Django + DRF      │                   │
│                   │   Celery + Redis     │  - Amazon PA API  │
│   - Dashboard     │   APScheduler       │  - Meesho API     │
│   - Analytics     │   SQLite → Postgres │  - Telegram Bot   │
│   - Preview       │   Pillow (images)   │  - Meta Graph API │
│   - Link Manager  │   Hugging Face AI   │  - Pinterest API  │
│                   │                     │  - Twitter API    │
└───────────────────┴─────────────────────┴───────────────────┘
```

### Core Automation Engine

```
[Product Scraper] → [AI Caption Generator] → [Image Composer]
       ↓                                              ↓
[Affiliate Link Builder] ← [Link Tracker DB] ← [Post Scheduler]
       ↓
[Multi-Platform Poster] → Telegram / Instagram / Facebook /
                           Pinterest / Twitter / Threads
```

---

## 3. File Structure

```
FashionBazzer\
│
├── frontend\
│   ├── public\
│   │   └── index.html
│   ├── src\
│   │   ├── components\
│   │   │   ├── Dashboard\
│   │   │   │   ├── Dashboard.jsx
│   │   │   │   ├── Dashboard.css
│   │   │   │   ├── StatsCard.jsx
│   │   │   │   └── RevenueChart.jsx
│   │   │   ├── Products\
│   │   │   │   ├── ProductList.jsx
│   │   │   │   ├── ProductCard.jsx
│   │   │   │   └── ProductCard.css
│   │   │   ├── Posts\
│   │   │   │   ├── PostPreview.jsx
│   │   │   │   ├── PostQueue.jsx
│   │   │   │   └── PostHistory.jsx
│   │   │   ├── Platforms\
│   │   │   │   ├── PlatformStatus.jsx
│   │   │   │   └── PlatformToggle.jsx
│   │   │   ├── Analytics\
│   │   │   │   ├── ClicksChart.jsx
│   │   │   │   ├── ConversionTable.jsx
│   │   │   │   └── EarningsTracker.jsx
│   │   │   ├── Settings\
│   │   │   │   ├── Settings.jsx
│   │   │   │   └── APIConfig.jsx
│   │   │   └── Shared\
│   │   │       ├── Navbar.jsx
│   │   │       ├── Sidebar.jsx
│   │   │       └── Loader.jsx
│   │   ├── pages\
│   │   │   ├── Home.jsx
│   │   │   ├── ProductsPage.jsx
│   │   │   ├── PostsPage.jsx
│   │   │   ├── AnalyticsPage.jsx
│   │   │   └── SettingsPage.jsx
│   │   ├── services\
│   │   │   ├── api.js              ← Axios calls to Django
│   │   │   ├── affiliateService.js
│   │   │   └── analyticsService.js
│   │   ├── context\
│   │   │   └── AppContext.jsx
│   │   ├── hooks\
│   │   │   ├── useProducts.js
│   │   │   └── useAnalytics.js
│   │   ├── utils\
│   │   │   └── formatters.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   ├── .env
│   ├── package.json
│   └── README.md
│
└── backend\
    ├── fashionbazzer\              ← Django project root
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── apps\
    │   ├── products\               ← Affiliate product scraping
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── serializers.py
    │   │   ├── scrapers\
    │   │   │   ├── amazon_scraper.py
    │   │   │   ├── meesho_scraper.py
    │   │   │   ├── flipkart_scraper.py
    │   │   │   └── base_scraper.py
    │   │   └── urls.py
    │   ├── content\                ← AI content generation
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── ai_generator.py     ← HuggingFace / Claude API
    │   │   ├── image_composer.py   ← Pillow image overlays
    │   │   ├── caption_templates.py
    │   │   └── serializers.py
    │   ├── poster\                 ← Multi-platform posting
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── platforms\
    │   │   │   ├── telegram_poster.py
    │   │   │   ├── instagram_poster.py
    │   │   │   ├── facebook_poster.py
    │   │   │   ├── pinterest_poster.py
    │   │   │   ├── twitter_poster.py
    │   │   │   └── threads_poster.py
    │   │   └── scheduler.py        ← APScheduler jobs
    │   ├── tracker\                ← Click & conversion tracking
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── link_builder.py     ← UTM + short link
    │   │   └── analytics.py
    │   └── dashboard\             ← Dashboard API
    │       ├── views.py
    │       └── serializers.py
    ├── media\
    │   ├── product_images\
    │   └── composed_posts\
    ├── static\
    ├── templates\
    ├── requirements.txt
    ├── manage.py
    ├── .env
    ├── Procfile                   ← For Render
    ├── render.yaml                ← Render deploy config
    └── README.md
```

---

## 4. Affiliate Platforms (Free)

### Primary Platforms (All Free to Join)

| Platform | Commission | Product Type | Join URL |
|----------|-----------|--------------|----------|
| **Amazon Associates** | 4–8% | All dresses, fast fashion | affiliate-program.amazon.in |
| **Meesho Affiliate** | 5–15% | Budget Indian fashion ₹199–999 | affiliate.meesho.com |
| **Flipkart Affiliate** | 5–10% | Trending dresses | affiliate.flipkart.com |
| **Myntra Affiliate** | 3–8% | Premium brands, youth | partner.myntra.com |
| **AJIO Affiliate** | 5–12% | Trendy Gen Z fashion | ajio.com/affiliates |
| **ShareASale** | Varies | Western fashion brands | shareasale.com |
| **CJ Affiliate** | Varies | International brands | cj.com |
| **Cuelinks** | 1–20% | Aggregates all Indian stores | cuelinks.com |
| **EarnKaro** | Up to 25% | Meesho, Myntra, Ajio combined | earnkaro.com |

### Best Strategy for 15–30 Age Group

```
Tier 1 (High Volume, Low Price ₹199–799):
  → Meesho + EarnKaro (budget Gen Z buyers)
  → AJIO (trendy, affordable)

Tier 2 (Medium Price ₹799–2000):
  → Myntra + Amazon (branded, aspirational)
  → Flipkart (sale events, Big Billion Days)

Tier 3 (Impulse Buy):
  → Cuelinks (cashback appeal to students)
```

---

## 5. Trending Dress Products Strategy

### Trending Categories (2024–2025 for 15–30 Age)

```
1. Co-ord Sets (Top trending — 400%+ search growth)
2. Y2K Dresses (Retro revival — TikTok/Instagram viral)
3. Bodycon Mini Dresses (Night out, college fest)
4. Cottagecore Maxi Dresses (Aesthetic Pinterest)
5. Indo-Western Fusion Dresses (Indian Gen Z)
6. Athleisure Dresses (WFH + college)
7. Cut-out Dresses (Party wear, trending globally)
8. Printed Wrap Dresses (Versatile everyday)
```

### Automated Product Discovery

```python
# backend/apps/products/scrapers/trend_detector.py

TRENDING_KEYWORDS = [
    "co-ord set under 500",
    "Y2K dress",
    "bodycon dress under 699",
    "aesthetic dress",
    "indo western dress girls",
    "mini dress trending",
    "cottagecore dress india",
    "party dress under 999",
    "college girl dress",
    "summer dress 2025"
]

# Scrape every 6 hours via APScheduler
# Filter: Price ₹199–1499, Rating > 4.0, Reviews > 50
# Sort by: BSR (Best Seller Rank) + Review velocity
```

---

## 6. Backend — Django Automation Engine

### 6.1 Core Django Settings

```python
# backend/fashionbazzer/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'django_apscheduler',
    'apps.products',
    'apps.content',
    'apps.poster',
    'apps.tracker',
    'apps.dashboard',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
    }
}

# APScheduler Config
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
SCHEDULER_AUTOSTART = True

CORS_ALLOWED_ORIGINS = [
    "https://fashionbazzer-frontend.onrender.com",
]
```

### 6.2 Automated Scheduler Jobs

```python
# backend/apps/poster/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

# ──────────────────────────────────────────
#  JOB 1: Scrape trending products (every 6h)
# ──────────────────────────────────────────
@scheduler.scheduled_job("interval", hours=6, id="scrape_products")
def scrape_trending_products():
    from apps.products.scrapers.meesho_scraper import MeeshoScraper
    from apps.products.scrapers.amazon_scraper import AmazonScraper
    MeeshoScraper().run()
    AmazonScraper().run()

# ──────────────────────────────────────────
#  JOB 2: Generate AI content (every 3h)
# ──────────────────────────────────────────
@scheduler.scheduled_job("interval", hours=3, id="generate_content")
def generate_content():
    from apps.content.ai_generator import ContentGenerator
    ContentGenerator().generate_batch(limit=10)

# ──────────────────────────────────────────
#  JOB 3: Post to all platforms (scheduled)
# ──────────────────────────────────────────
@scheduler.scheduled_job("cron", hour="9,13,18,21", id="post_content")
def post_to_all_platforms():
    from apps.poster.platforms.telegram_poster import TelegramPoster
    from apps.poster.platforms.instagram_poster import InstagramPoster
    from apps.poster.platforms.facebook_poster import FacebookPoster
    from apps.poster.platforms.pinterest_poster import PinterestPoster
    from apps.poster.platforms.twitter_poster import TwitterPoster

    post_queue = PostQueue.objects.filter(status='pending')[:5]
    for post in post_queue:
        TelegramPoster().send(post)
        InstagramPoster().send(post)
        FacebookPoster().send(post)
        PinterestPoster().send(post)
        TwitterPoster().send(post)
        post.status = 'published'
        post.save()

# ──────────────────────────────────────────
#  JOB 4: Sync affiliate commissions (daily)
# ──────────────────────────────────────────
@scheduler.scheduled_job("cron", hour=0, id="sync_commissions")
def sync_commissions():
    from apps.tracker.analytics import CommissionSync
    CommissionSync().run_all()

scheduler.start()
```

### 6.3 AI Content Generator

```python
# backend/apps/content/ai_generator.py

import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap

class ContentGenerator:
    TEMPLATES = {
        'telegram': """
🔥 TRENDING NOW! 👗

{product_name}
💰 Only ₹{price} (Was ₹{original_price})
⭐ {rating}/5 · {reviews} Reviews

✨ {ai_tagline}

🛒 Buy Now 👇
{affiliate_link}

#FashionBazzer #TrendingFashion #DressGoals
#GenZFashion #{category}
        """,

        'instagram': """
{ai_tagline} ✨

This {category} is EVERYTHING! 😍
Price: ₹{price} only 🤯

🛒 Link in bio to shop!

#FashionBazzer #OOTD #GenZFashion
#DressOfTheDay #TrendingNow #StyleInspo
#IndianFashion #BudgetFashion #CollegeOutfit
        """,

        'facebook': """
💃 DEAL ALERT for all fashion lovers!

{product_name} — Now at just ₹{price}!

{ai_tagline}

Perfect for college, dates, parties & everything!
★★★★★ Rated {rating}/5 by {reviews}+ shoppers

👇 Get yours before it's gone!
{affiliate_link}
        """,

        'pinterest': "{product_name} | ₹{price} | {ai_tagline} | Link: {affiliate_link}",

        'twitter': "🔥 {product_name} for just ₹{price}! {ai_tagline} 👗 #Fashion #OOTD {affiliate_link}",
    }

    def generate_caption(self, product, platform):
        tagline = self._generate_ai_tagline(product)
        template = self.TEMPLATES[platform]
        return template.format(
            product_name=product.name,
            price=product.sale_price,
            original_price=product.original_price,
            rating=product.rating,
            reviews=product.review_count,
            ai_tagline=tagline,
            affiliate_link=product.affiliate_url,
            category=product.category,
        )

    def _generate_ai_tagline(self, product):
        # Uses HuggingFace free inference API
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        prompt = f"""Generate a trendy, Gen Z style 1-sentence tagline for this dress:
        Name: {product.name}, Price: ₹{product.sale_price}, Category: {product.category}
        Make it catchy, use emojis, appeal to 15-30 year olds. MAX 15 words."""

        response = requests.post(API_URL, headers={
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"
        }, json={"inputs": prompt})

        return response.json()[0]['generated_text'].strip()

    def compose_image(self, product, platform):
        """Overlay product info on image for social media"""
        img = Image.open(product.local_image_path).resize((1080, 1080))
        draw = ImageDraw.Draw(img)

        # Gradient overlay at bottom
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        for y in range(700, 1080):
            alpha = int(200 * (y - 700) / 380)
            ImageDraw.Draw(overlay).rectangle([0, y, 1080, y+1], fill=(0,0,0,alpha))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)

        # Add text
        draw = ImageDraw.Draw(img)
        draw.text((40, 720), f"₹{product.sale_price}", fill="white", font=ImageFont.truetype("Arial", 80))
        draw.text((40, 820), product.name[:40], fill="white", font=ImageFont.truetype("Arial", 36))
        draw.text((40, 870), "FashionBazzer.in", fill="#FF69B4", font=ImageFont.truetype("Arial", 28))

        output_path = f"media/composed_posts/{product.id}_{platform}.jpg"
        img.convert('RGB').save(output_path, quality=95)
        return output_path
```

### 6.4 Platform Posters

```python
# backend/apps/poster/platforms/telegram_poster.py

import telegram
from django.conf import settings

class TelegramPoster:
    def __init__(self):
        self.bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.channel_id = settings.TELEGRAM_CHANNEL_ID  # e.g. @FashionBazzer

    def send(self, post_obj):
        with open(post_obj.image_path, 'rb') as photo:
            self.bot.send_photo(
                chat_id=self.channel_id,
                photo=photo,
                caption=post_obj.telegram_caption,
                parse_mode='HTML'
            )

# backend/apps/poster/platforms/instagram_poster.py
# Uses Meta Graph API (Business Account required — FREE)
import requests

class InstagramPoster:
    def __init__(self):
        self.access_token = settings.META_ACCESS_TOKEN
        self.ig_user_id = settings.INSTAGRAM_USER_ID

    def send(self, post_obj):
        # Step 1: Upload image as container
        container = requests.post(
            f"https://graph.facebook.com/v19.0/{self.ig_user_id}/media",
            data={
                "image_url": post_obj.public_image_url,
                "caption": post_obj.instagram_caption,
                "access_token": self.access_token,
            }
        ).json()

        # Step 2: Publish container
        requests.post(
            f"https://graph.facebook.com/v19.0/{self.ig_user_id}/media_publish",
            data={
                "creation_id": container['id'],
                "access_token": self.access_token,
            }
        )

# backend/apps/poster/platforms/facebook_poster.py
class FacebookPoster:
    def send(self, post_obj):
        requests.post(
            f"https://graph.facebook.com/v19.0/{settings.FB_PAGE_ID}/photos",
            data={
                "url": post_obj.public_image_url,
                "message": post_obj.facebook_caption,
                "access_token": settings.FB_PAGE_ACCESS_TOKEN,
            }
        )

# backend/apps/poster/platforms/pinterest_poster.py
class PinterestPoster:
    def send(self, post_obj):
        requests.post(
            "https://api.pinterest.com/v5/pins",
            headers={"Authorization": f"Bearer {settings.PINTEREST_ACCESS_TOKEN}"},
            json={
                "board_id": settings.PINTEREST_BOARD_ID,
                "media_source": {"source_type": "image_url", "url": post_obj.public_image_url},
                "title": post_obj.product.name,
                "description": post_obj.pinterest_caption,
                "link": post_obj.product.affiliate_url,
            }
        )

# backend/apps/poster/platforms/twitter_poster.py
import tweepy

class TwitterPoster:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_SECRET,
        )

    def send(self, post_obj):
        # Upload media first via v1 API
        auth = tweepy.OAuth1UserHandler(...)
        api = tweepy.API(auth)
        media = api.media_upload(post_obj.image_path)
        self.client.create_tweet(
            text=post_obj.twitter_caption,
            media_ids=[media.media_id]
        )
```

### 6.5 Link Tracker

```python
# backend/apps/tracker/link_builder.py

import hashlib
from apps.tracker.models import TrackedLink

class LinkBuilder:
    BASE_URL = "https://fashionbazzer-backend.onrender.com/r/"

    def build(self, affiliate_url, product_id, platform):
        short_code = hashlib.md5(
            f"{product_id}{platform}{affiliate_url}".encode()
        ).hexdigest()[:8]

        TrackedLink.objects.get_or_create(
            short_code=short_code,
            defaults={
                'affiliate_url': affiliate_url,
                'product_id': product_id,
                'platform': platform,
            }
        )
        return f"{self.BASE_URL}{short_code}"

# backend/apps/tracker/views.py — Redirect + track
class RedirectView(View):
    def get(self, request, short_code):
        link = TrackedLink.objects.get(short_code=short_code)
        link.click_count += 1
        link.save()

        Click.objects.create(
            link=link,
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            referrer=request.META.get('HTTP_REFERER'),
        )
        return redirect(link.affiliate_url)
```

---

## 7. Frontend — React Dashboard

### 7.1 Dashboard Layout

```jsx
// frontend/src/pages/Home.jsx
import Dashboard from '../components/Dashboard/Dashboard';
import PlatformStatus from '../components/Platforms/PlatformStatus';
import PostQueue from '../components/Posts/PostQueue';
import EarningsTracker from '../components/Analytics/EarningsTracker';

export default function Home() {
  return (
    <div className="home-grid">
      <Dashboard />           {/* Today's stats */}
      <PlatformStatus />      {/* All platforms green/red */}
      <EarningsTracker />     {/* Live earnings counter */}
      <PostQueue />           {/* Next scheduled posts */}
    </div>
  );
}
```

### 7.2 CSS Design System (Gen Z Aesthetic)

```css
/* frontend/src/index.css */
:root {
  --primary:    #FF3CAC;   /* Hot pink */
  --secondary:  #784BA0;   /* Purple */
  --accent:     #2B86C5;   /* Blue */
  --gradient:   linear-gradient(225deg, #FF3CAC 0%, #784BA0 50%, #2B86C5 100%);
  --bg-dark:    #0D0D0D;
  --bg-card:    #1A1A2E;
  --text:       #FFFFFF;
  --text-muted: #A0A0B0;
  --success:    #00D4AA;
  --warning:    #FFB800;
  --border:     rgba(255,255,255,0.1);
  --radius:     16px;
  --shadow:     0 8px 32px rgba(255,60,172,0.15);
}

body {
  background: var(--bg-dark);
  color: var(--text);
  font-family: 'Inter', sans-serif;
}

.glass-card {
  background: rgba(26,26,46,0.8);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}
```

### 7.3 Key Dashboard Components

```jsx
// frontend/src/components/Dashboard/StatsCard.jsx
export function StatsCard({ title, value, change, icon }) {
  return (
    <div className="glass-card stats-card">
      <span className="stats-icon">{icon}</span>
      <div className="stats-info">
        <h3>{title}</h3>
        <p className="stats-value">{value}</p>
        <span className={`change ${change > 0 ? 'positive' : 'negative'}`}>
          {change > 0 ? '↑' : '↓'} {Math.abs(change)}%
        </span>
      </div>
    </div>
  );
}

// Usage in Dashboard:
// <StatsCard title="Total Clicks" value="12,456" change={23} icon="👆" />
// <StatsCard title="Earnings Today" value="₹842" change={15} icon="💰" />
// <StatsCard title="Posts Sent" value="48" change={8} icon="📤" />
// <StatsCard title="Conversions" value="37" change={-3} icon="🛒" />
```

---

## 8. Social Media Automation (No Human)

### Posting Schedule (Optimized for 15–30 Age Group)

```
PLATFORM      | TIMES (IST)           | FREQUENCY   | FORMAT
──────────────┼───────────────────────┼─────────────┼──────────────────
Telegram      | 9AM, 1PM, 6PM, 9PM   | 4x/day      | Image + Caption
Instagram     | 9AM, 1PM, 8PM        | 3x/day      | Feed Post + Story
Facebook      | 10AM, 2PM, 7PM       | 3x/day      | Photo Post
Pinterest     | 8AM, 12PM, 5PM, 10PM | 4x/day      | Pin with Link
Twitter/X     | 9AM, 3PM, 9PM        | 3x/day      | Tweet + Image
Threads       | 9:30AM, 6:30PM       | 2x/day      | Thread style
──────────────┴───────────────────────┴─────────────┴──────────────────
TOTAL                                   19 posts/day  ZERO HUMAN WORK
```

### Telegram Channel Setup (Free, Highest Reach for India)

```
Channel Name: @FashionBazzer
Description: 🔥 Daily trending dresses & fashion at steal prices!
             Save 50-80% on top brands. New deals every day!

Bot: @FashionBazzerBot
- Posts automatically at scheduled times
- Sends 4 product posts per day
- Includes clickable affiliate links
- Tracks forwards for viral content detection
```

### Content Variation (Anti-Spam)

```python
# backend/apps/content/caption_templates.py

CAPTION_STYLES = [
    "excited",      # 🔥 OMG you NEED this!
    "informative",  # 📊 4.8/5 stars, 2000+ reviews
    "urgency",      # ⏰ Only 23 left in stock!
    "social_proof", # 💃 1200 people bought this week
    "lifestyle",    # ✨ Perfect for your next girls' trip
    "discount",     # 💸 70% off — ends tonight!
    "trendy",       # 🌊 This is giving main character energy
    "question",     # 🤔 Looking for a dress under ₹500?
]

# Rotate styles per post to avoid repetition and algorithm penalties
```

---

## 9. AI Content Generation Pipeline

### Free AI Tools Used

```
1. HuggingFace Inference API (FREE tier)
   → Model: mistralai/Mistral-7B-Instruct-v0.2
   → Used for: Caption generation, taglines

2. Pillow (Python, FREE)
   → Used for: Image composition, text overlays

3. Unsplash API (FREE tier — 50 req/hour)
   → Used for: Lifestyle background images

4. Remove.bg API (FREE tier — 50/month)
   → Used for: Product background removal

5. Canva-like templates (Custom Python)
   → Used for: Story-sized (9:16) posts for Instagram Stories
```

### Pipeline Flow

```
[Product DB] → [Select Top Performer] → [Download Image]
      ↓
[Remove Background (remove.bg)] → [Compose on Template (Pillow)]
      ↓
[Generate AI Tagline (HuggingFace)] → [Format Caption per Platform]
      ↓
[Save to PostQueue] → [Scheduler picks up] → [Post to All Platforms]
      ↓
[Log post ID + timestamp] → [Track clicks] → [Update Analytics]
```

---

## 10. Earn Quickly Strategy

### Fast Revenue Tactics

**Week 1–2: Setup & First Commissions**
- Focus on Meesho + EarnKaro (pays within 7–15 days)
- Target viral content: price-shock posts ("₹199 dress with 5000+ reviews!")
- Post Telegram first — fastest organic reach in India
- Pin top affiliate post on every channel

**Week 3–4: Scale Up**
- Add Cuelinks for cashback angle ("Get ₹50 cashback + this dress!")
- Enable Myntra during sale events (End of Season Sale = 5x clicks)
- Instagram Reels content (video of product — higher reach)
- Pinterest boards rank on Google → free SEO traffic

**Month 2+: Compound Growth**
- Pinterest pins have 6-month lifespan → passive clicks
- Build email list from Telegram subscribers → higher conversion
- Festival season (Diwali, New Year, Valentine's) = 10x commission spikes

### Revenue Calculator

```
Daily Posts:      19 posts across all platforms
Avg Reach/Post:   500–2000 views (organic, growing)
Click Rate:       3–8% (fashion is high CTR)
Daily Clicks:     ~500–1000
Conversion Rate:  1–3%
Daily Purchases:  5–30
Avg Order Value:  ₹600
Avg Commission:   8%
Daily Earning:    ₹24–₹144
Monthly Earning:  ₹720–₹4,320 (Month 1)
Monthly Earning:  ₹5,000–₹25,000 (Month 3–6 with compounding)
```

---

## 11. Database Schema

```python
# apps/products/models.py
class Product(models.Model):
    name           = models.CharField(max_length=300)
    platform       = models.CharField(max_length=50)   # meesho, amazon, etc.
    original_price = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price     = models.DecimalField(max_digits=8, decimal_places=2)
    rating         = models.FloatField()
    review_count   = models.IntegerField()
    category       = models.CharField(max_length=100)
    product_url    = models.URLField()
    affiliate_url  = models.URLField(blank=True)
    image_url      = models.URLField()
    local_image    = models.ImageField(upload_to='product_images/')
    is_trending    = models.BooleanField(default=False)
    last_scraped   = models.DateTimeField(auto_now=True)
    created_at     = models.DateTimeField(auto_now_add=True)

class PostQueue(models.Model):
    STATUS_CHOICES = [('pending','Pending'),('published','Published'),('failed','Failed')]
    product        = models.ForeignKey(Product, on_delete=models.CASCADE)
    telegram_cap   = models.TextField()
    instagram_cap  = models.TextField()
    facebook_cap   = models.TextField()
    pinterest_cap  = models.TextField()
    twitter_cap    = models.TextField()
    image_path     = models.CharField(max_length=500)
    public_image_url = models.URLField(blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_time = models.DateTimeField()
    published_at   = models.DateTimeField(null=True, blank=True)

class TrackedLink(models.Model):
    short_code     = models.CharField(max_length=20, unique=True)
    affiliate_url  = models.URLField()
    product        = models.ForeignKey(Product, on_delete=models.CASCADE)
    platform       = models.CharField(max_length=50)
    click_count    = models.IntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

class Click(models.Model):
    link           = models.ForeignKey(TrackedLink, on_delete=models.CASCADE)
    clicked_at     = models.DateTimeField(auto_now_add=True)
    ip_address     = models.GenericIPAddressField(null=True)
    user_agent     = models.TextField(blank=True)
    referrer       = models.URLField(blank=True)

class Commission(models.Model):
    product        = models.ForeignKey(Product, on_delete=models.CASCADE)
    affiliate_platform = models.CharField(max_length=50)
    amount         = models.DecimalField(max_digits=8, decimal_places=2)
    status         = models.CharField(max_length=20)  # pending/approved/paid
    recorded_at    = models.DateTimeField(auto_now_add=True)
```

---

## 12. API Endpoints

```
Django REST Framework Endpoints:

GET  /api/products/           → List all scraped products
GET  /api/products/trending/  → Top 10 trending products
GET  /api/products/{id}/      → Product detail

GET  /api/queue/              → View post queue
POST /api/queue/generate/     → Manually trigger content gen
POST /api/queue/publish-now/  → Force publish immediately

GET  /api/analytics/overview/ → Dashboard stats summary
GET  /api/analytics/clicks/   → Click data per platform
GET  /api/analytics/earnings/ → Commission breakdown

GET  /api/platforms/status/   → All platform connection status
POST /api/platforms/test/     → Test a platform connection

GET  /r/{short_code}/         → Redirect + track click (no /api/)
```

---

## 13. Deployment on Render (Free Tier)

### Services to Create on Render

```yaml
# backend/render.yaml

services:
  # ─── Django Backend ─────────────────────────────
  - type: web
    name: fashionbazzer-backend
    runtime: python
    buildCommand: pip install -r requirements.txt && python manage.py migrate
    startCommand: gunicorn fashionbazzer.wsgi:application --bind 0.0.0.0:$PORT
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: DATABASE_URL
        fromDatabase:
          name: fashionbazzer-db
          property: connectionString
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: META_ACCESS_TOKEN
        sync: false
      - key: PINTEREST_ACCESS_TOKEN
        sync: false
      - key: TWITTER_API_KEY
        sync: false
      - key: HUGGINGFACE_API_KEY
        sync: false
    plan: free

  # ─── React Frontend ──────────────────────────────
  - type: static
    name: fashionbazzer-frontend
    buildCommand: npm install && npm run build
    staticPublishPath: ./build
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    plan: free

  # ─── PostgreSQL Database ─────────────────────────
databases:
  - name: fashionbazzer-db
    databaseName: fashionbazzer
    plan: free
```

### Backend requirements.txt

```
django==4.2.9
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-apscheduler==0.6.2
psycopg2-binary==2.9.9
gunicorn==21.2.0
python-telegram-bot==20.7
tweepy==4.14.0
Pillow==10.2.0
requests==2.31.0
python-decouple==3.8
whitenoise==6.6.0
celery==5.3.6  # Optional but recommended
redis==5.0.1   # Use Render Redis free tier
```

### Frontend package.json (key deps)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "axios": "^1.6.7",
    "recharts": "^2.12.0",
    "react-hot-toast": "^2.4.1",
    "react-icons": "^5.0.1"
  }
}
```

### Environment Variables (Set in Render Dashboard)

```bash
# Django
SECRET_KEY=<auto-generated>
DEBUG=false
ALLOWED_HOSTS=fashionbazzer-backend.onrender.com
FRONTEND_URL=https://fashionbazzer-frontend.onrender.com

# Affiliate
AMAZON_ASSOCIATE_ID=fashionbazzer-21
MEESHO_AFFILIATE_ID=your_id
CUELINKS_ID=your_id

# Social Media APIs
TELEGRAM_BOT_TOKEN=bot123456789:ABCdef...
TELEGRAM_CHANNEL_ID=@FashionBazzer
META_ACCESS_TOKEN=EAABsm...
FB_PAGE_ID=123456789
INSTAGRAM_USER_ID=987654321
PINTEREST_ACCESS_TOKEN=pina_...
PINTEREST_BOARD_ID=your_board_id
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_SECRET=xxx

# AI
HUGGINGFACE_API_KEY=hf_xxx

# Media Hosting (Cloudinary free tier for public image URLs)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

---

## 14. Automation Flow Diagram

```
                        ┌─────────────────────┐
                        │   RENDER CRON JOB   │
                        │   (APScheduler)     │
                        └──────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │ Every 6h          │ Every 3h           │ Daily
              ▼                   ▼                    ▼
   ┌──────────────────┐ ┌─────────────────┐ ┌──────────────────┐
   │ PRODUCT SCRAPER  │ │ CONTENT ENGINE  │ │ COMMISSION SYNC  │
   │                  │ │                 │ │                  │
   │ • Meesho API     │ │ • AI Taglines   │ │ • Amazon         │
   │ • Amazon PA API  │ │ • Image Compose │ │ • Meesho         │
   │ • Flipkart API   │ │ • Caption gen   │ │ • Flipkart       │
   │ • Filter trends  │ │ • Per platform  │ │ • Store in DB    │
   └────────┬─────────┘ └────────┬────────┘ └──────────────────┘
            │                    │
            ▼                    ▼
   ┌──────────────────────────────────────────┐
   │              POSTGRESQL DB               │
   │  Products | PostQueue | Links | Clicks   │
   └──────────────────────┬───────────────────┘
                          │
              ┌───────────▼───────────┐
              │   POST SCHEDULER      │
              │  9AM/1PM/6PM/9PM IST  │
              └──────────┬────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────────┐
   │ TELEGRAM │   │INSTAGRAM │   │   FACEBOOK   │
   │  Channel │   │  + Story │   │     Page     │
   └──────────┘   └──────────┘   └──────────────┘
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐   ┌──────────┐   ┌──────────────┐
   │PINTEREST │   │TWITTER/X │   │   THREADS    │
   │  Boards  │   │  Tweets  │   │   Account    │
   └──────────┘   └──────────┘   └──────────────┘
         │
         ▼
   ┌─────────────────────────────────────────┐
   │         CLICK TRACKING LAYER            │
   │  fashionbazzer-backend.onrender.com/r/  │
   │  → Logs IP, platform, time → Redirects │
   └─────────────────────────────────────────┘
         │
         ▼
   ┌─────────────────────────────────────────┐
   │      REACT DASHBOARD (Real-time)        │
   │  Clicks | Earnings | Posts | Status     │
   └─────────────────────────────────────────┘
```

---

## 15. Free Tools & Services Used

| Service | Purpose | Free Tier Limit |
|---------|---------|-----------------|
| **Render.com** | Hosting frontend + backend + DB | 750 hrs/month web, 90-day DB |
| **PostgreSQL on Render** | Database | 256MB (enough for 1M links) |
| **Telegram Bot API** | Post to channel | Unlimited |
| **Meta Graph API** | Instagram + Facebook | Unlimited (with Business acct) |
| **Twitter API v2** | Tweet posting | 1,500 tweets/month (free) |
| **Pinterest API v5** | Pin creation | 100 pins/day (free) |
| **HuggingFace API** | AI caption gen | 30,000 tokens/month free |
| **Cloudinary** | Public image hosting | 25 GB / 25K transforms/month |
| **Cuelinks** | Multi-affiliate links | Free, no minimum payout |
| **EarnKaro** | Affiliate link gen | Free, pays ₹10 minimum |
| **remove.bg API** | BG removal | 50 API calls/month free |

**Total Monthly Cost: ₹0**

---

## 16. Phase-wise Build Plan

### Phase 1 — Foundation (Week 1–2)

```
[ ] Setup Django project + DRF
[ ] Create PostgreSQL models
[ ] Build Meesho + Amazon scrapers
[ ] Implement link tracker (short codes + redirect)
[ ] Setup Telegram bot and test posting
[ ] Deploy backend to Render
[ ] Test end-to-end flow manually
```

### Phase 2 — Content Engine (Week 2–3)

```
[ ] Integrate HuggingFace API for captions
[ ] Build Pillow image composer
[ ] Create all caption templates (per platform)
[ ] Setup APScheduler jobs
[ ] Add Cloudinary for public image URLs
[ ] Test full content pipeline
```

### Phase 3 — Multi-Platform (Week 3–4)

```
[ ] Connect Instagram Business API (Meta)
[ ] Connect Facebook Page API
[ ] Connect Pinterest API
[ ] Connect Twitter API v2
[ ] Implement Threads via Meta API
[ ] Test all platform posters
[ ] Setup posting schedule
```

### Phase 4 — React Dashboard (Week 4–5)

```
[ ] Build Dashboard home page
[ ] Build PostQueue view
[ ] Build Analytics charts (Recharts)
[ ] Build Platform status panel
[ ] Build Settings / API config
[ ] Connect to Django REST endpoints
[ ] Deploy frontend to Render (static site)
```

### Phase 5 — Optimization (Week 5–6)

```
[ ] A/B test caption styles
[ ] Analyze which platform drives most conversions
[ ] Add festival/sale event detection (auto-boost)
[ ] Add daily email report (via SendGrid free tier)
[ ] Monitor and fine-tune posting times
[ ] Add more affiliate platforms (AJIO, Myntra)
```

---

## 17. Revenue Projection

```
Month 1: ₹500  – ₹2,000    (Building audience, low reach)
Month 2: ₹2,000 – ₹6,000   (Growing Telegram + Pinterest)
Month 3: ₹6,000 – ₹15,000  (Pinterest SEO kicks in)
Month 4: ₹15,000 – ₹30,000 (Festival season bonus)
Month 6: ₹30,000 – ₹80,000 (Compound audience growth)

Key multipliers:
✓ Diwali/Navratri: 5-10x commission rates on Myntra/Ajio
✓ End of Season Sale: 3-5x click rate boost
✓ Valentine's Day: High dress demand from 15-25 age group
✓ College Fest season (Oct-March): Perfect audience
```

---

## 18. Security & Compliance

```
✓ All API keys stored in Render environment variables (never in code)
✓ Django CSRF protection enabled
✓ CORS configured to allow only frontend domain
✓ Rate limiting on /r/ redirect endpoint (prevent abuse)
✓ Affiliate disclosure on all posts ("AD" or "Affiliate link")
✓ Meta API — requires Facebook Business Verification
✓ Twitter — Free tier only allows 1,500 tweets/month
✓ Instagram — Content policy: no misleading claims
✓ Pinterest — Must mark as affiliate content
✓ No PII stored from link clicks (only anonymized)
✓ WhiteNoise for Django static files (no S3 needed)
```

---

## 🚀 Quick Start Commands

```bash
# Backend setup
cd FashionBazzer/backend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend setup
cd FashionBazzer/frontend
npm install
npm start

# Deploy to Render
# 1. Push to GitHub
# 2. Connect repo to Render
# 3. Create Web Service (backend) + Static Site (frontend)
# 4. Add all environment variables in Render dashboard
# 5. Deploy — everything runs automatically!
```

---

*FashionBazzer Master Plan — Built for 100% automation, ₹0 setup cost, deployed on Render*
*Target: 15–30 age | Trending dresses | 19 posts/day | Zero human involvement*
