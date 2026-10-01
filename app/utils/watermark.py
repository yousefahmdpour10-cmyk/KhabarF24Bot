"""
Watermark Utility

دانلود عکس خبر و اضافه‌کردن لوگوی کانال (کوچک، گوشه‌ی پایین) رویش.
"""

import io
from pathlib import Path
from typing import Optional

import aiohttp
from PIL import Image

from app.utils.logger import logger

LOGO_PATH = Path("assets/IMG_20260720_162446_015.jpg")

# عرض لوگو نسبت به عرض عکس اصلی (مثلاً ۱۸٪ عرض عکس) -- کوچک و
# غیرآزاردهنده، نه بزرگ.
LOGO_WIDTH_RATIO = 0.18
MARGIN_RATIO = 0.03


async def _download_image(url: str) -> Optional[bytes]:

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()

                logger.warning(
                    f"Watermark: دانلود عکس ناموفق، HTTP {response.status} -> {url}"
                )

    except Exception as e:
        logger.warning(f"Watermark: خطا در دانلود عکس -> {e}")

    return None


def _add_watermark(image_bytes: bytes) -> Optional[bytes]:

    try:
        base = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        if not LOGO_PATH.exists():
            logger.warning(
                f"Watermark: فایل لوگو پیدا نشد -> {LOGO_PATH}"
            )
            fallback = io.BytesIO()
            base.convert("RGB").save(fallback, format="JPEG", quality=90)
            return fallback.getvalue()

        logo = Image.open(LOGO_PATH).convert("RGBA")

        logo_width = int(base.width * LOGO_WIDTH_RATIO)
        logo_ratio = logo_width / logo.width
        logo_height = int(logo.height * logo_ratio)
        logo = logo.resize((logo_width, logo_height))

        margin = int(base.width * MARGIN_RATIO)
        position = (
            base.width - logo_width - margin,
            base.height - logo_height - margin,
        )

        base.paste(logo, position, logo)

        output = io.BytesIO()
        base.convert("RGB").save(output, format="JPEG", quality=90)
        return output.getvalue()

    except Exception as e:
        logger.warning(f"Watermark: خطا در ساخت واترمارک -> {e}")
        return None


async def build_watermarked_image(url: str) -> Optional[bytes]:
    """
    عکس خبر را از url دانلود می‌کند و لوگوی کانال را گوشه‌ی پایین
    آن اضافه می‌کند. اگر هر مرحله شکست بخورد، None برمی‌گرداند تا
    فراخوان بتواند به حالت متن‌ساده برگردد.
    """

    if not url:
        return None

    raw = await _download_image(url)

    if not raw:
        return None

    return _add_watermark(raw)
