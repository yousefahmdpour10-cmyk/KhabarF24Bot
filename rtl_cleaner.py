"""
KhabarF24 RTL Cleaner v8.0
اصلاح مشکلات RTL + نام‌های انگلیسی در متن فارسی
"""

import re
import logging

logger = logging.getLogger(__name__)

print("🔄 KhabarF24 RTL Cleaner v8.0 Loaded")


ENGLISH_TO_PERSIAN = {
    # Technology & Companies
    "OpenAI": "اوپن‌ای‌آی",
    "Google": "گوگل",
    "Microsoft": "مایکروسافت",
    "Apple": "اپل",
    "Tesla": "تسلا",
    "NVIDIA": "انویدیا",
    "Anthropic": "آنتروپیک",
    "Claude": "کلود",
    "Gemini": "جمینای",
    "Grok": "گروک",
    "Boston Dynamics": "بوستون داینامیکس",

    # Sports Clubs
    "Manchester United": "منچستر یونایتد",
    "Manchester City": "منچستر سیتی",
    "Real Madrid": "رئال مادرید",
    "Barcelona": "بارسلونا",
    "Liverpool": "لیورپول",
    "Arsenal": "آرسنال",
    "Bayern Munich": "بایرن مونیخ",

    # Countries
    "United States": "آمریکا",
    "USA": "آمریکا",
    "US": "آمریکا",
    "United Kingdom": "بریتانیا",
    "UK": "بریتانیا",
    "Iran": "ایران",
    "Iraq": "عراق",
    "Israel": "اسرائیل",
    "Russia": "روسیه",
    "China": "چین",
}


def replace_english_names(text: str) -> str:
    """جایگزینی نام‌های انگلیسی با معادل فارسی"""
    if not text:
        return ""

    # جایگزینی از طولانی به کوتاه
    for english, persian in sorted(ENGLISH_TO_PERSIAN.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(english, persian)

    return text


def fix_rtl_text(text: str) -> str:
    """اصلاح نهایی متن راست به چپ"""
    if not text:
        return ""

    text = " ".join(text.split())                    # پاک کردن فاصله‌های اضافی
    text = replace_english_names(text)               # جایگزینی نام‌ها

    # اضافه کردن پیشوند برای نام‌های خاص در ابتدای جمله
    prefixes = {
        "OpenAI": "شرکت ",
        "Google": "شرکت ",
        "Microsoft": "شرکت ",
        "Tesla": "شرکت ",
        "NVIDIA": "شرکت ",
        "Manchester United": "باشگاه ",
        "Real Madrid": "باشگاه ",
        "Barcelona": "باشگاه ",
    }

    for eng, prefix in prefixes.items():
        if text.startswith(eng):
            text = prefix + text
            break

    # اصلاح علائم نگارشی
    text = re.sub(r"\s+([،.!؟:؛])", r"\1", text)
    text = text.replace(" - ", " – ")

    return text.strip()


# تابع کمکی برای لاگ
def clean_and_log(text: str) -> str:
    cleaned = fix_rtl_text(text)
    if cleaned != text:
        logger.debug(f"RTL Fixed: '{text[:60]}...' → '{cleaned[:60]}...'")
    return cleaned
