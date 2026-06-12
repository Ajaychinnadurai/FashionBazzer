"""
Caption style templates and rotation logic for FashionBazzer.
Each platform gets different caption styles to avoid repetition.
"""
import random

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


def get_caption_style_for_post(post_index: int) -> str:
    """Rotate through styles to avoid repetition."""
    return CAPTION_STYLES[post_index % len(CAPTION_STYLES)]


# ──────────────────────────────────────────
# TELEGRAM TEMPLATES
# ──────────────────────────────────────────
TELEGRAM_TEMPLATES = {
    "excited": """🔥 TRENDING NOW! 👗

{product_name}
💰 Only ₹{price} (Was ₹{original_price}) — Save {discount}%!
⭐ {rating}/5 · {reviews} Reviews

✨ {ai_tagline}

🛒 Shop Now 👇
{affiliate_link}

#FashionBazzer #TrendingFashion #DressGoals #GenZFashion #{category}""",

    "informative": """📊 TOP RATED DRESS ALERT!

{product_name}
💰 ₹{price} only (M.R.P. ₹{original_price})
⭐ {rating}/5 stars · {reviews}+ reviews

✅ High quality fabric
✅ Perfect for {category} look
✅ {discount}% cheaper than MRP

👇 Grab yours:
{affiliate_link}

#FashionBazzer #TopRated #DressLover #GenZFashion""",

    "urgency": """⏰ FLASH DEAL! Only a few left!

{product_name}
💥 ₹{price} — That's {discount}% OFF!

{ai_tagline}

⚠️ Only {stock_left} left in stock!

🛒 Order now before it sells out:
{affiliate_link}

#FashionBazzer #FlashSale #TrendingNow #{category}""",

    "discount": """💸 BIG DISCOUNT ALERT!

{product_name}
🤑 Was ₹{original_price} → Now ₹{price}
🎯 You save ₹{save_amount} ({discount}% OFF!)

{ai_tagline}

Don't miss this deal! 👇
{affiliate_link}

#FashionBazzer #DealAlert #DiscountFashion #BudgetStyle""",

    "lifestyle": """✨ New in your feed!

Imagine yourself in this stunning {product_name} 🔥
Perfect for: dates, college, parties, brunch 🎉

💰 Price: ₹{price} only!
⭐ {rating}/5 stars from {reviews}+ happy customers

{ai_tagline}

Get yours: 👇
{affiliate_link}

#FashionBazzer #OOTD #StyleInspo #EverydayFashion""",

    "trendy": """🌊 This is YOUR sign to buy this dress!

{product_name} is giving MAIN CHARACTER ENERGY ✨
🤯 For just ₹{price}?!

{ai_tagline}

💕 Trust us, your wardrobe NEEDS this!
👇
{affiliate_link}

#FashionBazzer #MainCharacterEnergy #TrendyDress #{category}""",

    "question": """🤔 Looking for the perfect {category} dress?

Say hello to {product_name} ✨
⭐ {rating}/5 · {reviews}+ reviews
💰 Just ₹{price} (was ₹{original_price})

{ai_tagline}

👇 Shop now:
{affiliate_link}

#FashionBazzer #DressGoals #FindYourDress #{category}""",

    "social_proof": """💃 JOIN {reviews}+ happy customers!

{product_name} is trending BIG TIME 🔥
⭐ {rating}/5 stars
💰 Only ₹{price}

{ai_tagline}

Thousands loving this — don't miss out! 👇
{affiliate_link}

#FashionBazzer #TrendingNow #MostLoved #{category}""",
}

# ──────────────────────────────────────────
# INSTAGRAM TEMPLATES
# ──────────────────────────────────────────
INSTAGRAM_TEMPLATES = {
    "excited": """{ai_tagline} ✨

This {category} dress is EVERYTHING! 😍
Price: ₹{price} only 🤯 (was ₹{original_price})

🛒 Link in bio to shop!

#FashionBazzer #OOTD #GenZFashion
#DressOfTheDay #TrendingNow #StyleInspo
#IndianFashion #BudgetFashion #CollegeOutfit""",

    "lifestyle": """✨ Steal of the day!

{product_name}
₹{price} · ⭐ {rating}/5

Perfect for your next girls' trip, date night,
or college party 🎉

{ai_tagline}

👇 Link in bio!

#FashionBazzer #OOTD #DressGoals #FashionDaily""",

    "discount": """💸 Deal alert! Save {discount}%!

{product_name}
Was ₹{original_price} → Now ₹{price}

Limited stock! Grab fast 🏃‍♀️

{ai_tagline}

#FashionBazzer #BudgetFashion #DealAlert #DressSale""",
}

# ──────────────────────────────────────────
# FACEBOOK TEMPLATES
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
}

# ──────────────────────────────────────────
# PINTEREST TEMPLATES
# ──────────────────────────────────────────
PINTEREST_TEMPLATES = {
    "default": "{product_name} | ₹{price} | {ai_tagline} | Shop: {affiliate_link}",
    "trendy": "Trending: {product_name} just ₹{price} 🔥 {ai_tagline} #{category} #FashionBazzer",
}

# ──────────────────────────────────────────
# TWITTER/X TEMPLATES
# ──────────────────────────────────────────
TWITTER_TEMPLATES = {
    "excited": "🔥 {product_name} for just ₹{price}! {ai_tagline} 👗 #Fashion #OOTD",
    "discount": "💰 Save {discount}%! {product_name} now ₹{price} (was ₹{original_price}). {ai_tagline} 👗 #DealAlert",
    "trendy": "✨ {product_name} is trending! ₹{price} only. {ai_tagline} 👗 #FashionBazzer",
}

# ──────────────────────────────────────────
# THREADS TEMPLATES
# ──────────────────────────────────────────
THREADS_TEMPLATES = {
    "trendy": "{ai_tagline}\n\n✨ {product_name}\n💰 ₹{price}\n\n#FashionBazzer #DressGoals",
    "question": "Rate this dress 1-10 👇\n\n{product_name} · ₹{price}\n{ai_tagline}\n\n#FashionBazzer",
}
