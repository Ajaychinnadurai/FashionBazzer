"""
Caption style templates and rotation logic for FashionBazzer.
Enhanced with more variety, seasonal formats, and platform-specific best practices.
"""
import random

# ── Caption style rotation ──
CAPTION_STYLES = [
    "excited",
    "informative",
    "urgency",
    "social_proof",
    "lifestyle",
    "discount",
    "trendy",
    "question",
    "storytelling",
    "seasonal",
    "comparison",
    "challenge",
]

# Seasonal events for context-aware captions
SEASONS = [
    "Summer Vibes ☀️",
    "Monsoon Magic 🌧️",
    "Festival Season 🪔",
    "College Fest 🎓",
    "Weekend Party 🎉",
    "Date Night 💕",
    "Beach Day 🏖️",
    "Brunch Date 🥂",
    "Night Out 🌃",
    "Office Chic 💼",
]


def get_caption_style_for_post(post_index: int) -> str:
    """Rotate through styles to avoid repetition."""
    return CAPTION_STYLES[post_index % len(CAPTION_STYLES)]


# ── Hashtag bank per platform ──
HASHTAGS = {
    "telegram": [
        "#FashionBazzer #TrendingFashion #DressGoals #GenZFashion",
        "#FashionBazzer #OOTD #BudgetFashion #IndianFashion",
        "#FashionBazzer #DressOfTheDay #StyleInspo #FashionDaily",
        "#FashionBazzer #TrendyDress #CollegeFashion #PartyWear",
        "#FashionBazzer #FashionSale #DressUnder500 #NewArrival",
        "#FashionBazzer #InstaFashion #DressLove #StyleGoals",
        "#FashionBazzer #FashionDeals #CuteDress #TrendAlert",
        "#FashionBazzer #FashionAddict #DressCollection #OOTDIndia",
    ],
    "instagram": [
        "#FashionBazzer #OOTD #GenZFashion #DressOfTheDay #TrendingNow #StyleInspo #IndianFashion #BudgetFashion",
        "#FashionBazzer #InstaStyle #DressGoals #FashionDaily #OOTDIndia #TrendyDress #CollegeWear #PartyLook",
        "#FashionBazzer #StyleInspo #DressLove #FashionAddict #WhatIWore #DesiFashion #CuteDress #VibeCheck",
    ],
    "facebook": [
        "#FashionBazzer #TrendingFashion #DressSale #IndianFashion",
        "#FashionBazzer #FashionDaily #DressGoals #StyleInspo",
    ],
    "pinterest": [
        "#FashionBazzer #DressInspo #OOTD #IndianFashion #TrendyDress",
        "#FashionBazzer #FashionBlog #DressStyle #BudgetFashion",
    ],
    "twitter": [
        "#FashionBazzer #OOTD #DressGoals",
        "#FashionBazzer #TrendingNow #FashionDeal",
    ],
    "threads": [
        "#FashionBazzer #DressGoals",
        "#FashionBazzer #OOTD #Style",
    ],
}


def random_hashtags(platform: str) -> str:
    """Pick a random hashtag set for the given platform."""
    tags = HASHTAGS.get(platform, HASHTAGS["telegram"])
    return random.choice(tags)


# ──────────────────────────────────────────
# TELEGRAM TEMPLATES (6 clean styles)
# ──────────────────────────────────────────
TELEGRAM_TEMPLATES = {
    "style_pick": """✨ Selected Style Pick

🌸 Product: {product_name}
{ai_tagline}

🛍️ Pricing details:
• Original: ₹{original_price}
• Deal Price: ₹{price} (Save {discount}%)

💫 Upgrade your wardrobe today.
👇 Shop link in the button below! buy now {discount}% off link : {affiliate_link}""",

    "trending_pick": """🔥 Trending Pick of the Day

👗 Product: {product_name}
{ai_tagline}

💰 Pricing details:
• Original Price: ₹{original_price}
• Deal Price: ₹{price} (Save {discount}%)

💫 Upgrade your wardrobe today.
👇 Shop link in the button below! buy now {discount}% off link : {affiliate_link}""",

    "budget_pick": """💎 Budget-Friendly Pick

🛍️ Product: {product_name}
{ai_tagline}

📊 Pricing breakdown:
• Original: ₹{original_price}
• Deal Price: ₹{price} (Save {discount}%)

💫 Upgrade your wardrobe today.
👇 Shop link in the button below! buy now {discount}% off link : {affiliate_link}""",

    "top_rated": """⭐ Top Rated Style Pick

🌟 Product: {product_name}
{ai_tagline}

🛍️ Pricing details:
• Original: ₹{original_price}
• Deal Price: ₹{price} (Save {discount}%)

💫 Upgrade your wardrobe today.
👇 Shop link in the button below! buy now {discount}% off link : {affiliate_link}""",

    "deal_alert": """💥 Hot Deal Alert!

🎯 Product: {product_name}
{ai_tagline}

🛍️ Pricing details:
• Original: ₹{original_price}
• Deal Price: ₹{price} (Save {discount}%)

💫 Upgrade your wardrobe today.
👇 Shop link in the button below! buy now {discount}% off link : {affiliate_link}""",

    "must_have": """💖 Must-Have Pick

🌸 Product: {product_name}
{ai_tagline}

🛍️ Pricing details:
• Original: ₹{original_price}
• Deal Price: ₹{price} (Save {discount}%)

💫 Upgrade your wardrobe today.
👇 Shop link in the button below! buy now {discount}% off link : {affiliate_link}""",
}

# ──────────────────────────────────────────
# INSTAGRAM TEMPLATES (6 styles)
# ──────────────────────────────────────────
INSTAGRAM_TEMPLATES = {
    "excited": """{ai_tagline} ✨

This {category} dress is EVERYTHING! 😍
Price: ₹{price} only 🤯 (was ₹{original_price})

🛒 Link in bio to shop!

{hashtags}""",

    "lifestyle": """✨ Steal of the day!

{product_name}
₹{price} · ⭐ {rating}/5

Perfect for your next girls' trip, date night,
or college party 🎉

{ai_tagline}

👇 Link in bio!

{hashtags}""",

    "discount": """💸 Deal alert! Save {discount}%!

{product_name}
Was ₹{original_price} → Now ₹{price}

Limited stock! Grab fast 🏃‍♀️

{ai_tagline}

{hashtags}""",

    "trendy": """🔥 POV: You found the perfect {category} dress

{product_name}
₹{price} · ⭐ {rating}/5

{ai_tagline}

Link in bio to shop! 👆

{hashtags}""",

    "storytelling": """🎀 You deserve this. Period.

{product_name}
₹{price} (was ₹{original_price})

{ai_tagline}

✨ Treat yourself — link in bio!

{hashtags}""",

    "seasonal": """☀️ {season} essentials loaded 🔥

{product_name}
₹{price} · ⭐ {rating}/5

Your new favorite for {season} ✨

{ai_tagline}

Link in bio!

{hashtags}""",
}

# ──────────────────────────────────────────
# FACEBOOK TEMPLATES (5 styles)
# ──────────────────────────────────────────
FACEBOOK_TEMPLATES = {
    "excited": """💃 DEAL ALERT for all fashion lovers!

{product_name} — Now at just ₹{price}!

{ai_tagline}

Perfect for college, dates, parties & everything!
★★★★★ Rated {rating}/5 by {reviews}+ shoppers

👇 Get yours before it's gone!
{affiliate_link}""",

    "informative": """📢 New arrival alert!

{product_name}
✨ ₹{price} (Save {discount}%)
⭐ {rating}/5 · {reviews} reviews

{ai_tagline}

Order now 👇
{affiliate_link}""",

    "social_proof": """🔥 {reviews}+ people already bought this!

{product_name}
⭐ {rating}/5 Stars
💰 ₹{price} only

{ai_tagline}

Don't be the only one missing out! 👇
{affiliate_link}""",

    "lifestyle": """✨ Weekend plans? We've got your outfit sorted!

{product_name}
₹{price} · ⭐ {rating}/5

{ai_tagline}

👇 Shop now:
{affiliate_link}""",

    "trendy": """🌊 This dress is breaking the internet!

{product_name} — trending at ₹{price} only 🔥
⭐ {rating}/5 · {reviews}+ reviews

{ai_tagline}

👇 Grab yours:
{affiliate_link}""",
}

# ──────────────────────────────────────────
# PINTEREST TEMPLATES (4 styles)
# ──────────────────────────────────────────
PINTEREST_TEMPLATES = {
    "default": "{product_name} | ₹{price} | {ai_tagline} | Shop: {affiliate_link} {hashtags}",
    "trendy": "Trending: {product_name} just ₹{price} 🔥 {ai_tagline} {hashtags}",
    "lifestyle": "How to style {product_name} for {season} ✨ {ai_tagline} ₹{price} only! {hashtags}",
    "comparison": "Before: Overpaying at malls 🤯 After: {product_name} at just ₹{price} 😍 {ai_tagline} {hashtags}",
}

# ──────────────────────────────────────────
# TWITTER/X TEMPLATES (5 styles)
# ──────────────────────────────────────────
TWITTER_TEMPLATES = {
    "excited": "🔥 {product_name} for just ₹{price}! {ai_tagline} 👗 {hashtags}",
    "discount": "💰 Save {discount}%! {product_name} now ₹{price} (was ₹{original_price}). {ai_tagline} 👗 {hashtags}",
    "trendy": "✨ {product_name} is trending! ₹{price} only. {ai_tagline} 👗 {hashtags}",
    "question": "🤔 Need a {category} dress under ₹{price}? 👗 {product_name}. {ai_tagline} {hashtags}",
    "lifestyle": "💃 Your {season} wardrobe isn't complete without {product_name}. Just ₹{price}! {ai_tagline} {hashtags}",
}

# ──────────────────────────────────────────
# THREADS TEMPLATES (4 styles)
# ──────────────────────────────────────────
THREADS_TEMPLATES = {
    "trendy": "{ai_tagline}\n\n✨ {product_name}\n💰 ₹{price}\n\n{hashtags}",
    "question": "Rate this dress 1-10 👇\n\n{product_name} · ₹{price}\n{ai_tagline}\n\n{hashtags}",
    "lifestyle": "This is your sign to buy that {category} dress you've been eyeing ✨\n\n{product_name} · ₹{price}\n{ai_tagline}\n\n{hashtags}",
    "storytelling": "PSA: {product_name} exists and it's only ₹{price} 😍\n\n{ai_tagline}\n\n{hashtags}",
}
