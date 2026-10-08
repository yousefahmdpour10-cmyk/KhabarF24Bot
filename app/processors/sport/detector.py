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

    تشخیص بر اساس:
    1. عنوان خبر
    2. خلاصه خبر
    3. متن خبر
    4. دسته‌بندی منبع
    5. نام منبع
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # متن اصلی خبر
        text = " ".join(
            [
                str(getattr(news, "title", "") or ""),
                str(getattr(news, "summary", "") or ""),
                str(getattr(news, "content", "") or ""),
            ]
        )

        # اطلاعات منبع
        source_name = str(
            getattr(news, "source", "") or ""
        )

        source_category = str(
            getattr(news, "category", "") or ""
        )

        # برای تشخیص بهتر، نام منبع و دسته منبع
        # نیز به متن تشخیص اضافه می‌شوند.
        detection_text = " ".join(
            [
                text,
                source_name,
                source_category,
            ]
        )

        scores = defaultdict(int)

        # ---------------------------------------------------------
        # 1. تشخیص بر اساس کلیدواژه‌های ورزشی
        # ---------------------------------------------------------

        for sport_id, sport in SPORTS.items():

            for keyword in sport["keywords"]:

                if keyword_in_text(keyword, detection_text):
                    scores[sport_id] += 1

        # ---------------------------------------------------------
        # 2. تقویت تشخیص فوتبال بر اساس منابع تخصصی فوتبال
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

        for keyword in football_source_keywords:

            if keyword_in_text(keyword, source_name):
                scores["football"] += 3

        # ---------------------------------------------------------
        # 3. دسته‌بندی منبع
        # ---------------------------------------------------------

        football_categories = [
            "football",
            "transfer",
            "premier_league",
            "champions_league",
            "europa_league",
            "international",
        ]

        for category in football_categories:

            if category in source_category.lower():
                scores["football"] += 3

        # ---------------------------------------------------------
        # 4. نتیجه نهایی
        # ---------------------------------------------------------

        if scores:

            best = max(
                scores,
                key=scores.get,
            )

            best_score = scores[best]

            news.sport = best
            news.sport_name = SPORTS[best]["name"]
            news.sport_emoji = SPORTS[best]["emoji"]
            news.sport_hashtag = SPORTS[best]["hashtag"]

            logger.info(
                f"Sport: {news.sport_name} "
                f"(score={best_score})"
            )

        else:

            news.sport = None
            news.sport_name = None
            news.sport_emoji = None
            news.sport_hashtag = None

            logger.info("Sport: not detected")

        return news
