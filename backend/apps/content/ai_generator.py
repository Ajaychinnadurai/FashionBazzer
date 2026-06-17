"""
AI content generation engine for FashionBazzer.

Uses HuggingFace's free inference API for AI caption generation
and Pillow for image composition.
"""
import logging
import random
import requests
from typing import Dict, Optional
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont
import textwrap

from django.conf import settings
from django.utils import timezone

from .caption_templates import (
    TELEGRAM_TEMPLATES, INSTAGRAM_TEMPLATES, FACEBOOK_TEMPLATES,
    PINTEREST_TEMPLATES, TWITTER_TEMPLATES, THREADS_TEMPLATES,
    CAPTION_STYLES, get_caption_style_for_post,
    random_hashtags, SEASONS,
)
from .models import GenerationLog
from apps.poster.models import PostQueue, PostLog
from apps.products.models import Product
from apps.tracker.link_builder import LinkBuilder

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generates AI-powered content for affiliate products."""

    TEMPLATES = {
        'telegram': TELEGRAM_TEMPLATES,
        'instagram': INSTAGRAM_TEMPLATES,
        'facebook': FACEBOOK_TEMPLATES,
        'pinterest': PINTEREST_TEMPLATES,
        'twitter': TWITTER_TEMPLATES,
        'threads': THREADS_TEMPLATES,
    }

    def __init__(self):
        self.hf_api_key = settings.HUGGINGFACE_API_KEY
        self.link_builder = LinkBuilder()

    def generate_batch(self, limit: int = 10, recycle: bool = False) -> Dict:
        """
        Generate content for products.

        Args:
            limit: Maximum number of products to process.
            recycle: If True, re-process products that already have content
                     (creates fresh PostQueue entries with new captions).
                     If False, only processes products without ai_tagline.

        Returns:
            Dict with 'generated' count and 'errors'.
        """
        if recycle:
            # Recycle: pick products that have been posted before,
            # but EXCLUDE products that already have pending posts in the queue
            # to prevent duplicate posting of the same product
            # Skip products that already have pending posts
            # (prevents duplicate posting of the same product)
            products_with_pending = PostQueue.objects.filter(
                status='pending'
            ).values_list('product_id', flat=True).distinct()

            products = Product.objects.filter(
                ai_tagline__gt=''
            ).exclude(
                id__in=products_with_pending
            ).order_by('?')[:limit]
        else:
            # Fresh: only products that haven't had content generated yet
            products = Product.objects.filter(
                ai_tagline=''
            ).order_by('-rating', '-review_count')[:limit]

        generated = 0
        errors = []

        for product in products:
            try:
                post_queue = self.generate_for_product(product, force_regenerate=recycle)
                if post_queue:
                    generated += 1
            except Exception as e:
                errors.append(str(e))
                logger.error(f"Content generation failed for {product.id}: {e}")

        return {
            'generated': generated,
            'errors': errors[:5],
        }

    def generate_for_product(self, product, force_regenerate: bool = False) -> Optional[PostQueue]:
        """
        Generate complete content for a single product.
        Creates AI tagline, platform-specific captions, and composed image.

        Args:
            product: Product instance or product ID.
            force_regenerate: If True, generate new content even if product
                              already has a tagline (creates fresh PostQueue).

        Returns:
            PostQueue instance or None on failure.
        """
        if isinstance(product, int):
            try:
                product = Product.objects.get(id=product)
            except Product.DoesNotExist:
                return None

        # Step 1: Generate AI tagline (or use existing if not force_regenerate)
        style = random.choice(CAPTION_STYLES)
        if force_regenerate or not product.ai_tagline:
            tagline = self._generate_ai_tagline(product)
            product.ai_tagline = tagline
            product.save(update_fields=['ai_tagline'])
        else:
            tagline = product.ai_tagline

        # Step 2: Build tracked affiliate links per platform
        platforms = ['telegram', 'instagram', 'facebook', 'pinterest', 'twitter', 'threads']
        affiliate_links = {}
        for platform in platforms:
            affiliate_links[platform] = self.link_builder.build(
                affiliate_url=product.affiliate_url or product.product_url,
                product_id=product.id,
                platform=platform,
            )

        # Step 3: Generate captions for each platform
        season = random.choice(SEASONS)
        context = {
            'product_name': product.name[:50],
            'price': int(product.sale_price),
            'original_price': int(product.original_price),
            'discount': product.discount_percent,
            'save_amount': int(product.original_price - product.sale_price),
            'rating': product.rating,
            'reviews': product.review_count,
            'category': product.get_category_display() if product.category else 'Dress',
            'ai_tagline': tagline,
            'stock_left': random.randint(5, 50),
            'season': season,
        }

        captions = {}
        for platform in platforms:
            # Use the platform-specific tracked link and hashtags
            context['affiliate_link'] = affiliate_links[platform]
            context['hashtags'] = random_hashtags(platform)
            captions[f'{platform}_caption'] = self.generate_caption(product, platform, context)

        # Step 4: Compose image with overlays
        image_path = self.compose_image(product, context)

        # Construct public image URL from local image path for Meta / Pinterest
        public_image_url = ''
        if image_path:
            import os
            try:
                # Get the relative path from BASE_DIR (e.g. "media/composed_posts/post_1_1234.jpg")
                rel_path = os.path.relpath(image_path, settings.BASE_DIR).replace('\\', '/')
                # REDIRECT_BASE_URL is like "https://fashionbazzer-backend.onrender.com/r/"
                base_url = settings.REDIRECT_BASE_URL.split('/r/')[0]
                public_image_url = f"{base_url}/{rel_path}"
            except Exception as e:
                logger.error(f"Failed to resolve public image URL: {e}")

        # Step 5: Create PostQueue entry
        post = PostQueue.objects.create(
            product=product,
            telegram_caption=captions.get('telegram_caption', ''),
            instagram_caption=captions.get('instagram_caption', ''),
            facebook_caption=captions.get('facebook_caption', ''),
            pinterest_caption=captions.get('pinterest_caption', ''),
            twitter_caption=captions.get('twitter_caption', ''),
            threads_caption=captions.get('threads_caption', ''),
            image_path=image_path or '',
            public_image_url=public_image_url,
            caption_style=style,
            scheduled_time=timezone.now(),
            status='pending',
        )

        # Log generation
        GenerationLog.objects.create(
            product=product,
            model_used='mistral-7b-instruct',
            prompt_tokens=len(tagline),
            generated_captions=captions,
            image_composed=bool(image_path),
            duration_ms=0,
            success=True,
        )

        logger.info(f"Generated content for product #{product.id}: {product.name[:40]}")
        return post

    def generate_caption(self, product, platform: str, context: Dict) -> str:
        """Generate platform-specific caption using templates."""
        templates = self.TEMPLATES.get(platform, {})
        if not templates:
            return ""

        # Choose a random template for variety
        template_key = random.choice(list(templates.keys()))
        template = templates[template_key]

        try:
            return template.format(**context)
        except KeyError as e:
            logger.warning(f"Missing template key {e} for {platform}")
            return f"Check out {product.name} at ₹{product.sale_price}! {context.get('affiliate_link', '')}"

    def _generate_ai_tagline(self, product) -> str:
        """
        Generate a trendy Gen Z tagline using HuggingFace inference API.
        Falls back to template-based taglines if API key is not configured.
        """
        if not self.hf_api_key or self.hf_api_key == 'hf_xxx':
            return self._fallback_tagline(product)

        prompt = (
            f"Generate a trendy, Gen Z style 1-sentence tagline for this dress: "
            f"Name: {product.name[:60]}, "
            f"Price: ₹{int(product.sale_price)}, "
            f"Category: {product.get_category_display() if product.category else 'Dress'}. "
            f"Make it catchy, use emojis, appeal to 15-30 year old Indian audience. "
            f"MAX 15 words."
        )

        try:
            API_URL = (
                "https://api-inference.huggingface.co/models/"
                "mistralai/Mistral-7B-Instruct-v0.2"
            )
            response = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {self.hf_api_key}"},
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 50,
                        "temperature": 0.8,
                        "top_p": 0.9,
                    }
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get('generated_text', '')
                    # Extract just the generated part after the prompt
                    if 'MAX 15 words.' in text:
                        text = text.split('MAX 15 words.')[-1].strip()
                    return text[:200]
        except Exception as e:
            logger.warning(f"HuggingFace API error: {e}")

        return self._fallback_tagline(product)

    def _fallback_tagline(self, product) -> str:
        """Generate taglines without AI API for development.
        NOTE: Taglines should NOT include price/rating — templates already handle that.
        """
        taglines = [
            "💖 This piece is giving main character energy! 🔥",
            "✨ Your new closet obsession has arrived! 💫",
            "💃 Slay every moment in this stunning piece! 🔥",
            "🌸 Obsessed is an understatement! Get this look ✨",
            "⭐ Pure perfection — and we totally get why! 💕",
            "🎯 The fit everyone's been asking about! 💥",
            "🌟 Affordable luxury at its finest! 💎",
            "🔥 Manifesting good vibes in this gorgeous piece 💖",
            "💸 Chic, classy, and totally unreal! 🎉",
            "👗 Your wardrobe called — it needs this stunner! ✨",
            "✨ The definition of style and comfort! 💫",
            "🌸 Wear your confidence today! 💪",
            "🎀 Twirl-worthy and totally YOU! 💕",
            "🌟 Upgrade your style game instantly! 🔥",
            "💖 Ready to turn heads wherever you go! 👀",
        ]
        return random.choice(taglines)

    def compose_image(self, product, context: Dict) -> Optional[str]:
        """
        Compose product image with price overlay for social media.
        Creates a beautiful 1080x1080 square image suitable for all platforms.
        Renders a polished branded fallback even without a product photo.
        """
        try:
            # ── Background with gradient ──
            img = Image.new('RGB', (1080, 1080), '#121220')

            # Draw a gradient rectangle (dark navy -> purple-pink)
            draw = ImageDraw.Draw(img)
            for y in range(1080):
                ratio = y / 1080
                r = int(18 + (255 - 18) * ratio * 0.35)
                g = int(18 + (60 - 18) * ratio * 0.40)
                b = int(34 + (172 - 34) * ratio * 0.30)
                draw.line([(0, y), (1080, y)], fill=(r, g, b))

            # ── Accent circles (decorative) - draw on RGBA then composite ──
            img_rgba = img.convert('RGBA')
            accent_layer = Image.new('RGBA', (1080, 1080), (0, 0, 0, 0))
            accent_draw = ImageDraw.Draw(accent_layer)
            accent_draw.ellipse([(740, -60), (1140, 340)], fill=(255, 60, 172, 30))
            accent_draw.ellipse([(580, 780), (1080, 1180)], fill=(67, 134, 197, 20))
            img = Image.alpha_composite(img_rgba, accent_layer)

            # ── Try to place the product image ──
            image_placed = False
            if product.image_url:
                try:
                    import requests as img_requests
                    from io import BytesIO
                    response = img_requests.get(product.image_url, timeout=10)
                    if response.status_code == 200:
                        product_img = Image.open(BytesIO(response.content))
                        product_img = product_img.convert('RGBA')

                        # Create a rounded-rect mask for a modern look
                        thumb = Image.new('RGBA', (800, 800), (0, 0, 0, 0))
                        thumb_draw = ImageDraw.Draw(thumb)
                        thumb_draw.rounded_rectangle([(0, 0), (800, 800)], radius=24, fill=(255, 255, 255, 255))

                        product_img.thumbnail((780, 780), Image.Resampling.LANCZOS)
                        x_offset = (1080 - product_img.width) // 2
                        y_offset = 40

                        # Composite with rounded mask
                        mask = thumb.crop((0, 0, product_img.width, product_img.height)).resize(product_img.size)
                        img_rgba = img.convert('RGBA')
                        img_rgba.paste(product_img, (x_offset, y_offset), mask)
                        img = img_rgba.convert('RGB')
                        image_placed = True
                except Exception as e:
                    logger.warning(f"Failed to overlay product image: {e}")

            if not image_placed:
                # ── Beautiful fallback: fashion illustration / dress silhouette ──
                # Create a centered card with brand styling
                img_rgba = img.convert('RGBA')
                card = Image.new('RGBA', (600, 700), (0, 0, 0, 0))
                card_draw = ImageDraw.Draw(card)
                card_draw.rounded_rectangle([(0, 0), (600, 700)], radius=32, fill=(30, 30, 50, 220))

                # Decorative dress silhouette (simple shape)
                cx, cy = 300, 320
                # Bodice
                card_draw.rounded_rectangle([(cx-60, cy-80), (cx+60, cy+40)], radius=30, fill=(255, 60, 172, 80))
                # Skirt (triangle-like)
                for yo in range(0, 260):
                    width = int(200 * (yo / 260) + 60)
                    card_draw.line([(cx - width//2, cy + 40 + yo), (cx + width//2, cy + 40 + yo)],
                                   fill=(255, 60, 172, max(30, 80 - yo//4)))
                # Circle accent (like a hanger)
                card_draw.ellipse([(cx-16, cy-100), (cx+16, cy-68)], fill=(255, 60, 172, 120))

                # Center the card
                card_x = (1080 - 600) // 2
                card_y = 40
                img_rgba.paste(card, (card_x, card_y), card)
                img = img_rgba.convert('RGB')

            # ── Shadow gradient at bottom (for text legibility) ──
            img_rgba = img.convert('RGBA')
            overlay = Image.new('RGBA', (1080, 1080), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            for y in range(560, 1080):
                alpha = int(200 * (1 - (y - 560) / 520))
                overlay_draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
            img = Image.alpha_composite(img_rgba, overlay)
            draw = ImageDraw.Draw(img)

            # ── Fonts ──
            try:
                font_price = ImageFont.truetype("arial.ttf", 80)
                font_name = ImageFont.truetype("arial.ttf", 38)
                font_brand = ImageFont.truetype("arial.ttf", 28)
                font_tagline = ImageFont.truetype("arial.ttf", 30)
                font_discount = ImageFont.truetype("arial.ttf", 36)
            except (IOError, OSError):
                font_price = ImageFont.load_default()
                font_name = ImageFont.load_default()
                font_brand = ImageFont.load_default()
                font_tagline = ImageFont.load_default()
                font_discount = ImageFont.load_default()

            # ── Text overlays ──

            # Discount badge
            discount = context.get('discount', 0)
            if discount:
                draw.text((50, 590), f"-{discount}% OFF", fill="#00D4AA", font=font_discount)

            # Price
            price_text = f"₹{context.get('price', '')}"
            draw.text((50, 640), price_text, fill="#FF3CAC", font=font_price)

            # Original price strikethrough (use draw.textlength for font-safe measurement)
            orig = context.get('original_price', 0)
            if orig:
                price_w = draw.textlength(price_text, font=font_price)
                orig_text = f"₹{orig}"
                draw.text((50 + int(price_w) + 20, 660),
                          orig_text, fill="#888888", font=font_name)
                strike_y = 698
                strike_x_start = 50 + int(price_w) + 20
                strike_x_end = strike_x_start + int(draw.textlength(orig_text, font=font_name))
                draw.line([(strike_x_start, strike_y), (strike_x_end, strike_y)], fill="#FF3CAC", width=3)

            # Product name (wrapped for long names)
            name = context.get('product_name', '')[:50]
            draw.text((50, 740), name, fill="white", font=font_name)

            # Rating + reviews
            rating = context.get('rating', 0)
            reviews = context.get('reviews', 0)
            draw.text((50, 800), f"⭐ {rating}/5 · {reviews}+ reviews", fill="#FFB800", font=font_tagline)

            # Tagline
            tagline = context.get('ai_tagline', '')[:80]
            draw.text((50, 860), tagline, fill="#CCCCCC", font=font_tagline)

            # Brand
            draw.text((50, 990), "FashionBazzer.in", fill="#FF69B4", font=font_brand)
            draw.text((50, 1030), "Your daily fashion fix ✨", fill="#A0A0B0", font=font_brand)

            # ── Save ──
            output_dir = settings.MEDIA_ROOT / 'composed_posts'
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(output_dir / f"post_{product.id}_{random.randint(1000,9999)}.jpg")
            img.convert('RGB').save(output_path, quality=95)

            logger.info(f"Composed image saved: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Image composition failed: {e}")
            return None
