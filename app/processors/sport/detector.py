"""
Sport Detector

تشخیص رشته ورزشی
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.sport.keywords import SPORTS
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


class SportDetector:
    """
    تشخیص رشته ورزشی

    اولویت تشخیص:

    1. متن واقعی خبر
       - عنوان
       - خلاصه
       - متن

    2. اطلاعات منبع
       - نام منبع
       - دسته‌بندی منبع

    نکته مهم:
    اطلاعات منبع به تنهایی نمی‌توانند یک خبر را ورزشی کنند.
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # ---------------------------------------------------------
        # 1. متن واقعی خبر
        # ---------------------------------------------------------

        article_text = " ".join(
            [
                str(getattr(news, "title", "") or ""),
                str(getattr(news, "summary", "") or ""),
                str(getattr(news, "content", "") or ""),
            ]
        )

        # ---------------------------------------------------------
        # 2. اطلاعات منبع
        # ---------------------------------------------------------

        source_name = str(
            getattr(news, "source", "") or ""
        )

        source_category = str(
            getattr(news, "category", "") or ""
        )

        # ---------------------------------------------------------
        # 3. تشخیص رشته ورزشی فقط از متن خبر
        # ---------------------------------------------------------

        text_scores = defaultdict(int)

        for sport_id, sport in SPORTS.items():

            for keyword in sport["keywords"]:

                if keyword_in_text(keyword, article_text):
                    text_scores[sport_id] += 1

        # ---------------------------------------------------------
        # اگر هیچ نشانه ورزشی در خود خبر وجود ندارد،
        # اطلاعات منبع نباید باعث تشخیص اشتباه شود.
        # ---------------------------------------------------------

        if not text_scores:

            news.sport = None
            news.sport_name = None
            news.sport_emoji = None
            news.sport_hashtag = None

            logger.info("Sport: not detected")

            return news

        # ---------------------------------------------------------
        # 4. امتیاز پایه از متن خبر
        # ---------------------------------------------------------

        scores = defaultdict(int)

        for sport_id, score in text_scores.items():
            scores[sport_id] = score

        # ---------------------------------------------------------
        # 5. تقویت بسیار محدود بر اساس منبع
        #
        # منبع فقط می‌تواند رشته‌ای را که از متن تشخیص داده شده
        # تقویت کند؛ هرگز نمی‌تواند یک رشته جدید ایجاد کند.
        # ---------------------------------------------------------

        football_source_keywords = [
            "bbc football",
            "sky sports football",
            "gianluca di marzio",
            "di marzio",
            "fabrizio romano",
            "transfermarkt",
            "premier league",
            "uefa",
            "fifa",
        ]

        football_source_match = any(
            keyword_in_text(keyword, source_name)
            for keyword in football_source_keywords
        )

        if (
            football_source_match
            and "football" in scores
        ):
            scores["football"] += 1

        # ---------------------------------------------------------
        # 6. تقویت محدود بر اساس دسته‌بندی منبع
        #
        # فقط برای رشته‌ای که قبلاً از متن شناسایی شده.
        # ---------------------------------------------------------

        football_categories = [
            "football",
            "transfer",
            "premier_league",
            "champions_league",
            "europa_league",
            "international",
        ]

        source_is_football = any(
            category in source_category.lower()
            for category in football_categories
        )

        if (
            source_is_football
            and "football" in scores
        ):
            scores["football"] += 1

        # ---------------------------------------------------------
        # 7. انتخاب بهترین رشته
        # ---------------------------------------------------------

        best = max(
            scores,
            key=scores.get,
        )

        best_score = scores[best]

        # ---------------------------------------------------------
        # 8. ذخیره نتیجه
        # ---------------------------------------------------------

        news.sport = best
        news.sport_name = SPORTS[best]["name"]
        news.sport_emoji = SPORTS[best]["emoji"]
        news.sport_hashtag = SPORTS[best]["hashtag"]

        logger.info(
            f"Sport: {news.sport_name} "
            f"(score={best_score})"
        )

        return news
