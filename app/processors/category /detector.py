# app/processors/category/detector.py

"""
Category Detector

تشخیص دسته‌بندی خبر
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.category.keywords import CATEGORY_KEYWORDS
from app.utils.logger import logger


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

        if scores:

            best_category = max(
                scores,
                key=scores.get,
            )

            news.category = best_category

            logger.info(
                f"Category: {best_category}"
            )

        else:

            news.category = "general"

            logger.info(
                "Category: general"
            )

        return news
