"""
Story Match

تشخیص «همان خبر از رسانه‌ی دیگر» روی تیتر فارسیِ تولیدشده.

با ۲۰۰+ منبع، هر خبر مهم را ده‌ها رسانه پوشش می‌دهند و تیتر فارسی هرکدام
کمی فرق دارد (مثلاً «ترامپ: توافق با تهران ممکن است رخ دهد» و «ترامپ
می‌گوید توافق با ایران ممکن است»). مقایسه‌ی کامل تیتر (Jaccard ۰.۶۵) این‌ها را
نمی‌گیرد؛ این تابع فقط «کلمه‌های مهم» (بدون حروف ربط و فعل‌های رایج) را
مقایسه می‌کند: اگر دست‌کم ۳ کلمه‌ی مهم مشترک باشد و شباهتشان به
۰.۴ برسد، همان خبر است.
"""

from typing import Iterable

from .checker import _normalize_headline

MIN_SHARED_WORDS = 3
MIN_KEY_JACCARD = 0.4

# کلمه‌های رایجی که خبر را از خبر دیگر جدا نمی‌کنند
STOPWORDS = frozenset(
    """
    در از به را که با این آن برای است بود شد شده شود کرد کرده کند کنند
    می‌کند میکند میکنند میگوید میگویند گفت گفته اعلام درباره پس پیش بعد
    تا بر یا هم نیز دارد دارند داد دهد دهند خواهد باید بیان گزارش خبر
    ممکن احتمال جدید تازه علیه مقابل بین میان طی طبق اساس
    """.split()
)


def key_words(headline: str) -> set:
    """کلمه‌های مهم یک تیتر (نرمال‌شده، حداقل ۳ حرف، بدون کلمه‌ی رایج)."""

    words = _normalize_headline(headline).split()

    return {w for w in words if len(w) >= 3 and w not in STOPWORDS}


def is_same_story(headline: str, recent: Iterable[str]) -> bool:
    """
    آیا این تیتر همان خبری است که در تیترهای اخیر (نرمال‌شده) هست؟
    """

    words = key_words(headline)

    if len(words) < MIN_SHARED_WORDS:
        return False

    for old in recent:
        old_words = key_words(old)

        if not old_words:
            continue

        shared = len(words & old_words)

        if shared < MIN_SHARED_WORDS:
            continue

        if shared / len(words | old_words) >= MIN_KEY_JACCARD:
            return True

    return False
