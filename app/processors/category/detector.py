"""
Category Detector
تشخیص دسته‌بندی خبر
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.category.keywords import CATEGORY_KEYWORDS
from app.utils.logger import logger

MIN_CATEGORY_SCORE = 2

# منابعی که کاملاً داخلی/ایرانی هستند. اگر هیچ دسته‌ی دیگری با کلیدواژه
# به‌درستی تشخیص داده نشود (خبر افتاد در general)، چون این منابع خودشان
# رسانه‌ی داخلی ایران هستند، منطقی‌تر است پیش‌فرض به "iran" برود تا
# "general" بی‌معنا -- حتی اگر متن خبر اسم صریح "ایران"/"تهران" نداشته باشد.
IRANIAN_SOURCES = {
    "isna",
    "mehr news",
    "tasnim news",
    "khabar online",
    "tabnak",
    "yjc",
    "irna",
    "fars",
}


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

            source = (getattr(news, "source", None) or "").strip().lower()

            if source in IRANIAN_SOURCES:
                final_category = "iran"
                logger.info(
                    f"Category: iran (defaulted from general, source '{news.source}' is a domestic Iranian outlet)"
                )
                news.category = final_category
                return news

        news.category = final_category
        logger.info(f"Category: {final_category}")

        return news
