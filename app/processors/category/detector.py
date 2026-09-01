"""
Category Detector
تشخیص دسته‌بندی خبر
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.category.keywords import CATEGORY_KEYWORDS
from app.utils.logger import logger

MIN_CATEGORY_SCORE = 2


class CategoryDetector:
    """
    تشخیص دسته خبر
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        text = f"{news.title} {news.summary}".lower()

        scores = defaultdict(int)

        for category, keywords in CATEGORY_KEYWORDS.items():

            for keyword in keywords:

                if keyword.lower() in text:
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

        if final_category == "general":

            # اگر کلیدواژه‌ها ضعیف بودند، به دسته‌بندی‌ای که خودمان
            # موقع تعریف این منبع در sources.json برایش مشخص کرده‌ایم
            # اعتماد می‌کنیم -- فقط وقتی که منبع دقیقاً یک دسته دارد
            # (یعنی بدون ابهام است، مثل یک فید اختصاصی فوتبال یا یک
            # خبرگزاری کاملاً داخلی ایران).
            hint = getattr(news, "source_category_hint", None)

            if hint and len(hint) == 1:
                final_category = hint[0]
                logger.info(
                    f"Category: {final_category} (defaulted from general via source hint, source='{news.source}')"
                )
                news.category = final_category
                return news

        news.category = final_category
        logger.info(f"Category: {final_category}")

        return news
