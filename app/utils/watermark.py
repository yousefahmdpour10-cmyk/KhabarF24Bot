
Watermark Utility
اضافه‌کردن هدر نوشتاری KhabarF24 به گوشه پایین-چپ عکس خبر.
"""

import io
from pathlib import Path
from typing import Optional

import aiohttp
from PIL import Image

from app.utils.logger import logger


# هدر نوشتاری شفاف KhabarF24
# این فایل را داخل پوشه assets قرار بده.
LOGO_PATH = Path("assets/khabarf24_header.png")

# اندازه هدر نسبت به عرض عکس.
# 18٪ همان اندازه‌ای است که در نمونه نهایی مناسب بود.
LOGO_WIDTH_RATIO = 0.18

# فاصله کاملاً یکسان از پایین و چپ تصویر.
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
                f"Watermark: فایل هدر پیدا نشد -> {LOGO_PATH}"
            )

            fallback = io.BytesIO()
            base.convert("RGB").save(
                fallback,
                format="JPEG",
                quality=90,
                optimize=True,
            )
            return fallback.getvalue()

        logo = Image.open(LOGO_PATH).convert("RGBA")

        # اندازه هدر فقط بر اساس عرض عکس تعیین می‌شود.
        # نسبت طول/ارتفاع خود هدر حفظ می‌شود تا کاملاً صاف و تراز بماند.
        logo_width = max(1, int(base.width * LOGO_WIDTH_RATIO))
        scale = logo_width / logo.width
        logo_height = max(1, int(logo.height * scale))

        logo = logo.resize(
            (logo_width, logo_height),
            Image.Resampling.LANCZOS,
        )

        # فاصله دقیق و مساوی از چپ و پایین
        margin_x = int(base.width * MARGIN_RATIO)
        margin_y = int(base.height * MARGIN_RATIO)

        # پایین-چپ، بدون چرخش، بدون کشیدگی و بدون جابه‌جایی عمودی
        position = (
            margin_x,
            base.height - logo_height - margin_y,
        )

        base.alpha_composite(logo, dest=position)

        output = io.BytesIO()
        base.convert("RGB").save(
            output,
            format="JPEG",
            quality=92,
            optimize=True,
        )

        return output.getvalue()

    except Exception as e:
        logger.warning(f"Watermark: خطا در ساخت واترمارک -> {e}")
        return None


async def build_watermarked_image(url: str) -> Optional[bytes]:
    """
    عکس خبر را دانلود می‌کند و هدر KhabarF24 را
    دقیقاً در گوشه پایین-چپ تصویر قرار می‌دهد.
    """

    if not url:
        return None

    raw = await _download_image(url)

    if not raw:
        return None

    return _add_watermark(raw)
