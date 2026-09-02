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
    تشخیص دسته خبر

    این کلاس باید بعد از SportDetector در pipeline اجرا شود، چون اگر
    SportDetector قبلاً یک رشته‌ی ورزشی مشخص را تشخیص داده باشد (که
    لیست کلیدواژه‌ی بسیار کامل‌تری دارد، شامل نام بازیکنان و اصطلاحات
    تخصصی)، آن نتیجه معتبرتر از حدس دوباره با لیست عمومی‌تر این فایل
    است.
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # اگر SportDetector از قبل رشته‌ای را تشخیص داده، همان را
        # بپذیر -- نیازی به حدس دوباره نیست.
        if getattr(news, "sport", None):
            news.category = "sport"
            logger.info(
                f"Category: sport (trusted from SportDetector, sport='{news.sport}')"
            )
            return news

        text = f"{news.title} {news.summary}"

        scores = defaultdict(int)

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

        if final_category == "general":

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
