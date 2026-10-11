
"""
Category Detector
تشخیص دسته‌بندی خبر
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.category.keywords import CATEGORY_KEYWORDS
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text

MIN_CATEGORY_SCORE = 2


class CategoryDetector:
    """
    تشخیص دسته خبر.

    این کلاس بعد از SportDetector اجرا می‌شود.
    اگر SportDetector رشته ورزشی را تشخیص داده باشد،
    دسته اصلی خبر برابر sport خواهد بود.
    """

    async def process(self, news: RawNews) -> RawNews:

        # اگر SportDetector رشته ورزشی را تشخیص داده باشد،
        # نتیجه آن را حفظ می‌کنیم.
        if getattr(news, "sport", None):
            news.category = "sport"
            logger.info(
                "Category: sport (detected sport='%s')",
                news.sport,
            )
            return news

        text = (
            f"{getattr(news, 'title', '') or ''} "
            f"{getattr(news, 'summary', '') or ''}"
        )

        scores = defaultdict(int)

        # تشخیص دسته بر اساس محتوای خبر
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword_in_text(keyword, text):
                    scores[category] += 1

        final_category = "general"

        if scores:
            best_category = max(
                scores,
                key=scores.get,
            )

            best_score = scores[best_category]

            if best_score >= MIN_CATEGORY_SCORE:
                final_category = best_category

        # اگر محتوا به اندازه کافی کلیدواژه نداشت،
        # از دسته‌بندی تعریف‌شده برای منبع کمک می‌گیریم.
        if final_category == "general":
            hint = getattr(
                news,
                "source_category_hint",
                None,
            ) or []

            normalized_hint = {
                str(item).strip().lower()
                for item in hint
                if item
            }

            # football یک زیرشاخه از sport است؛
            # دسته اصلی خبر باید sport باشد.
            if "sport" in normalized_hint or "football" in normalized_hint:
                final_category = "sport"

                logger.info(
                    "Category: sport (source hint, source='%s', hints=%s)",
                    getattr(news, "source", "Unknown"),
                    sorted(normalized_hint),
                )

            elif "general" not in normalized_hint:
                # دسته‌های دیگر فقط در صورتی پذیرفته می‌شوند
                # که در دسته‌بندی‌های معتبر پروژه وجود داشته باشند.
                valid_categories = set(CATEGORY_KEYWORDS.keys())
                valid_hints = normalized_hint & valid_categories

                if len(valid_hints) == 1:
                    final_category = next(iter(valid_hints))

                    logger.info(
                        "Category: %s (source hint, source='%s')",
                        final_category,
                        getattr(news, "source", "Unknown"),
                    )

        news.category = final_category

        logger.info(
            "Category: %s | source=%s",
            final_category,
            getattr(news, "source", "Unknown"),
        )

        return news
