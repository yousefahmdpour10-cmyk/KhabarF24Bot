"""
Story Match

تشخیص «همان خبر از رسانه‌ی دیگر» روی تیتر فارسیِ تولیدشده.

با ۲۰۰+ منبع، هر خبر مهم را ده‌ها رسانه پوشش می‌دهند و تیتر فارسی
هرکدام کمی فرق دارد.

مثال:

«ترامپ: توافق با تهران ممکن است رخ دهد»

و:

«ترامپ می‌گوید توافق با ایران ممکن است»

این تابع فقط کلمه‌های مهم را مقایسه می‌کند.
"""

from typing import Iterable

from .checker import _normalize_headline


MIN_SHARED_WORDS = 3
MIN_KEY_JACCARD = 0.4


# --------------------------------------------------------------
# کلمات عمومی که برای تشخیص یکسان بودن داستان ارزش کمی دارند.
# --------------------------------------------------------------

STOPWORDS = frozenset(
    """
    در از به را که با این آن برای بر
    است بود شد شده شود
    کرد کرده کند کنند
    می‌کند میکند میکنند
    میگوید میگویند
    گفت گفته
    اعلام درباره
    پس پیش بعد
    تا یا هم نیز
    دارد دارند
    داد دهد دهند
    خواهد باید
    بیان گزارش خبر
    ممکن احتمال
    جدید تازه
    علیه مقابل
    بین میان
    طی طبق اساس
    امروز
    دیروز
    فردا
    اکنون
    همزمان
    """.split()
)


def key_words(headline: str) -> set:
    """
    استخراج کلمه‌های مهم تیتر.

    - نرمال‌سازی
    - حذف stopword
    - حذف کلمات کمتر از ۳ حرف
    """

    words = _normalize_headline(
        headline
    ).split()

    return {
        word
        for word in words
        if len(word) >= 3
        and word not in STOPWORDS
    }


def is_same_story(
    headline: str,
    recent: Iterable[str],
) -> bool:
    """
    آیا این تیتر همان خبری است که
    در تیترهای اخیر وجود دارد؟
    """

    words = key_words(
        headline
    )

    if len(words) < MIN_SHARED_WORDS:
        return False

    for old in recent:

        old_words = key_words(
            old
        )

        if not old_words:
            continue

        shared = len(
            words & old_words
        )

        if shared < MIN_SHARED_WORDS:
            continue

        union = len(
            words | old_words
        )

        if not union:
            continue

        jaccard = (
            shared / union
        )

        if jaccard >= MIN_KEY_JACCARD:
            return True

    return False
