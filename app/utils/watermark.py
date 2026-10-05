"""
Watermark Utility

دانلود عکس خبر و قرار دادن هدر KhabarF24 در گوشه پایین‌چپ.

ویژگی‌ها:
- پنل مشکی ظریف پشت هدر برای جلوگیری از گم‌شدن لوگو
- اندازه هوشمند بر اساس جهت و اندازه عکس
- حفظ کامل نسبت هدر
- قرارگیری دقیق در پایین‌چپ
"""

import io
from pathlib import Path
from typing import Optional

import aiohttp
from PIL import Image, ImageDraw

from app.utils.logger import logger


# ============================================================
# مسیر هدر
# ============================================================

LOGO_PATH = Path(
    "assets/khabarf24_header_transparent_final.png"
)


# ============================================================
# اندازه هوشمند
# ============================================================

# عکس عمودی
PORTRAIT_RATIO = 0.30

# عکس تقریباً مربعی
SQUARE_RATIO = 0.27

# عکس افقی
LANDSCAPE_RATIO = 0.23


# حداقل و حداکثر اندازه واقعی هدر
# برای جلوگیری از خیلی کوچک یا خیلی بزرگ شدن
MIN_LOGO_WIDTH = 80
MAX_LOGO_WIDTH = 380


# ============================================================
# فاصله از لبه‌های عکس
# ============================================================

# فاصله اصلی از چپ و پایین
MARGIN_RATIO = 0.035


# ============================================================
# تنظیمات پنل مشکی
# ============================================================

# فاصله پنل مشکی از خود لوگو
PANEL_PADDING_RATIO = 0.012

# میزان شفافیت پنل
# 255 = کاملاً مشکی
PANEL_ALPHA = 235

# گردی گوشه‌های پنل
PANEL_RADIUS_RATIO = 0.012


# ============================================================
# دانلود عکس
# ============================================================

async def _download_image(url: str) -> Optional[bytes]:

    try:
        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(url) as response:

                if response.status == 200:
                    return await response.read()

                logger.warning(
                    f"Watermark: دانلود عکس ناموفق، "
                    f"HTTP {response.status} -> {url}"
                )

    except Exception as e:

        logger.warning(
            f"Watermark: خطا در دانلود عکس -> {e}"
        )

    return None


# ============================================================
# محاسبه اندازه هوشمند هدر
# ============================================================

def _smart_logo_width(base: Image.Image) -> int:
    """
    اندازه هدر را بر اساس جهت عکس تعیین می‌کند.

    عمودی:
        حدود 30 درصد عرض عکس

    مربعی:
        حدود 27 درصد عرض عکس

    افقی:
        حدود 23 درصد عرض عکس

    سپس حداقل و حداکثر اعمال می‌شود.
    """

    width = base.width
    height = base.height

    if height <= 0:
        return MIN_LOGO_WIDTH

    aspect_ratio = width / height

    # --------------------------------------------
    # عکس عمودی
    # --------------------------------------------

    if aspect_ratio < 0.85:

        ratio = PORTRAIT_RATIO

    # --------------------------------------------
    # عکس تقریباً مربعی
    # --------------------------------------------

    elif aspect_ratio <= 1.20:

        ratio = SQUARE_RATIO

    # --------------------------------------------
    # عکس افقی
    # --------------------------------------------

    else:

        ratio = LANDSCAPE_RATIO

    logo_width = int(width * ratio)

    # محدود کردن اندازه
    logo_width = max(
        MIN_LOGO_WIDTH,
        logo_width
    )

    logo_width = min(
        MAX_LOGO_WIDTH,
        logo_width
    )

    return logo_width


# ============================================================
# ساخت واترمارک
# ============================================================

def _add_watermark(
    image_bytes: bytes
) -> Optional[bytes]:

    try:

        # ----------------------------------------------------
        # باز کردن عکس اصلی
        # ----------------------------------------------------

        base = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGBA")


        # ----------------------------------------------------
        # بررسی وجود هدر
        # ----------------------------------------------------

        if not LOGO_PATH.exists():

            logger.warning(
                f"Watermark: فایل هدر پیدا نشد -> "
                f"{LOGO_PATH}"
            )

            fallback = io.BytesIO()

            base.convert("RGB").save(
                fallback,
                format="JPEG",
                quality=92,
                optimize=True
            )

            return fallback.getvalue()


        # ----------------------------------------------------
        # باز کردن هدر شفاف
        # ----------------------------------------------------

        logo = Image.open(
            LOGO_PATH
        ).convert("RGBA")


        # ----------------------------------------------------
        # اندازه هوشمند
        # ----------------------------------------------------

        logo_width = _smart_logo_width(base)

        scale = logo_width / logo.width

        logo_height = max(
            1,
            int(logo.height * scale)
        )

        logo = logo.resize(
            (
                logo_width,
                logo_height
            ),
            Image.Resampling.LANCZOS
        )


        # ----------------------------------------------------
        # ساخت پنل مشکی پشت هدر
        # ----------------------------------------------------

        padding = max(
            4,
            int(base.width * PANEL_PADDING_RATIO)
        )

        panel_width = (
            logo.width + (padding * 2)
        )

        panel_height = (
            logo.height + (padding * 2)
        )

        panel_radius = max(
            5,
            int(base.width * PANEL_RADIUS_RATIO)
        )


        # پنل کاملاً شفاف در ابتدا
        panel = Image.new(
            "RGBA",
            (
                panel_width,
                panel_height
            ),
            (0, 0, 0, 0)
        )


        # ----------------------------------------------------
        # رسم زمینه مشکی
        # ----------------------------------------------------

        draw = ImageDraw.Draw(panel)

        draw.rounded_rectangle(
            (
                0,
                0,
                panel_width - 1,
                panel_height - 1
            ),
            radius=panel_radius,
            fill=(
                0,
                0,
                0,
                PANEL_ALPHA
            )
        )


        # ----------------------------------------------------
        # قرار دادن هدر وسط پنل
        # ----------------------------------------------------

        panel.alpha_composite(
            logo,
            dest=(
                padding,
                padding
            )
        )


        # ----------------------------------------------------
        # فاصله پنل از لبه عکس
        # ----------------------------------------------------

        margin_x = max(
            8,
            int(base.width * MARGIN_RATIO)
        )

        margin_y = max(
            8,
            int(base.height * MARGIN_RATIO)
        )


        # ----------------------------------------------------
        # موقعیت دقیق پایین چپ
        # ----------------------------------------------------

        position = (
            margin_x,
            base.height
            - panel_height
            - margin_y
        )


        # ----------------------------------------------------
        # چسباندن پنل + هدر
        # ----------------------------------------------------

        base.alpha_composite(
            panel,
            dest=position
        )


        # ----------------------------------------------------
        # خروجی
        # ----------------------------------------------------

        output = io.BytesIO()

        base.convert("RGB").save(
            output,
            format="JPEG",
            quality=92,
            optimize=True
        )

        return output.getvalue()


    except Exception as e:

        logger.warning(
            f"Watermark: خطا در ساخت واترمارک -> {e}"
        )

        return None


# ============================================================
# تابع اصلی
# ============================================================

async def build_watermarked_image(
    url: str
) -> Optional[bytes]:

    """
    عکس خبر را از URL دانلود می‌کند و هدر KhabarF24
    را با پنل مشکی و اندازه هوشمند در پایین‌چپ
    قرار می‌دهد.

    در صورت خطا None برگردانده می‌شود تا سیستم بتواند
    به حالت متن‌ساده برگردد.
    """

    if not url:
        return None


    raw = await _download_image(url)

    if not raw:
        return None


    return _add_watermark(raw)
