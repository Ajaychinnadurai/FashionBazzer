"""
Image composition utilities for FashionBazzer.
Creates platform-optimized images with product overlays.
"""
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import logging
import os
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Color palette matching the brand identity
BRAND_COLORS = {
    'pink': '#FF3CAC',
    'purple': '#784BA0',
    'blue': '#2B86C5',
    'dark': '#0D0D0D',
    'card': '#1A1A2E',
    'success': '#00D4AA',
    'warning': '#FFB800',
    'white': '#FFFFFF',
    'muted': '#A0A0B0',
}


def create_instagram_story(product_data: Dict, output_path: str) -> Optional[str]:
    """
    Create a 9:16 (1080x1920) Instagram Story post.
    """
    try:
        img = Image.new('RGB', (1080, 1920), BRAND_COLORS['card'])
        draw = ImageDraw.Draw(img)

        # Add gradient background
        for y in range(1920):
            alpha = int(50 * (1 - y / 1920))
            overlay = Image.new('RGBA', (1080, 1), (255, 60, 172, alpha))

        # Try to overlay product image
        if product_data.get('image_url'):
            try:
                response = requests.get(product_data['image_url'], timeout=10)
                if response.status_code == 200:
                    product_img = Image.open(BytesIO(response.content))
                    product_img = product_img.resize((900, 900))
                    x_offset = (1080 - 900) // 2
                    y_offset = 200
                    img.paste(product_img, (x_offset, y_offset))
            except Exception as e:
                logger.warning(f"Image overlay failed: {e}")

        # Text overlays
        draw = ImageDraw.Draw(img)
        draw.text((50, 1200), f"₹{product_data.get('sale_price', '')}", fill=BRAND_COLORS['pink'])
        draw.text((50, 1350), product_data.get('name', '')[:50], fill=BRAND_COLORS['white'])
        draw.text((50, 1450), "⬆️ Swipe up to shop!", fill=BRAND_COLORS['success'])
        draw.text((50, 1820), "FashionBazzer.in", fill=BRAND_COLORS['muted'])

        img.save(output_path, quality=95)
        return output_path

    except Exception as e:
        logger.error(f"Story creation failed: {e}")
        return None


def create_pinterest_pin(product_data: Dict, output_path: str) -> Optional[str]:
    """
    Create a 2:3 (1000x1500) Pinterest pin.
    """
    try:
        img = Image.new('RGB', (1000, 1500), BRAND_COLORS['dark'])
        draw = ImageDraw.Draw(img)

        # Product image
        if product_data.get('image_url'):
            try:
                response = requests.get(product_data['image_url'], timeout=10)
                product_img = Image.open(BytesIO(response.content))
                product_img = product_img.resize((800, 800))
                x_offset = (1000 - 800) // 2
                img.paste(product_img, (x_offset, 100))
            except Exception as e:
                logger.warning(f"Pin image failed: {e}")

        draw.text((50, 950), product_data.get('name', '')[:60], fill=BRAND_COLORS['white'])
        draw.text((50, 1050), f"₹{product_data.get('sale_price', '')}", fill=BRAND_COLORS['pink'])
        draw.text((50, 1420), "FashionBazzer.in", fill=BRAND_COLORS['muted'])

        img.save(output_path, quality=95)
        return output_path

    except Exception as e:
        logger.error(f"Pin creation failed: {e}")
        return None
