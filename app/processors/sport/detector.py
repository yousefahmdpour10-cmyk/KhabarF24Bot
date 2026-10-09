"""
Sport Detector

تشخیص رشته ورزشی با استفاده از متن خبر
و منابع معتبر و اختصاصی ورزشی.
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.sport.keywords import SPORTS
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


# این منابع مشخصاً روی فوتبال تمرکز دارند.
FOOTBALL_SOURCES = (
    "bbc football",
    "sky sports football",
    "espn soccer",
    "gianluca di marzio",
    "di marzio",
    "fabrizio romano",
    "transfermarkt",
    "premier league",
)


FOOTBALL_SOURCE_CATEGORIES = (
    "football",
    "soccer",
    "premier_league",
    "champions_league",
    "europa_league",
)


class SportDetector:
    """تشخیص رشته ورزشی خبر."""

    async def process(self, news: RawNews) -> RawNews:
        title = str(getattr(news, "title", "") or "")
        summary = str(getattr(news, "summary", "") or "")
        content = str(getattr(news, "content", "") or "")

        source_name = str(
            getattr(news, "source", "") or ""
        ).lower()

        source_category = str(
            getattr(news, "category", "") or ""
        ).lower()

        article_text = " ".join(
            (title, summary, content)
        )

        text_scores = defaultdict(int)

        # مرحله اول: تشخیص بر اساس متن واقعی خبر
        for sport_id, sport in SPORTS.items():
            for keyword in sport["keywords"]:
                if keyword_in_text(keyword, article_text):
                    text_scores[sport_id] += 1

        # مرحله دوم: تقویت تشخیص بر اساس منبع اختصاصی فوتبال
        source_is_football = any(
            keyword in source_name
            for keyword in FOOTBALL_SOURCES
        )

        category_is_football = any(
            keyword in source_category
            for keyword in FOOTBALL_SOURCE_CATEGORIES
        )

        # اگر متن رشته ورزشی را مشخص کرده، همان تشخیص حفظ می‌شود.
        # منبع اختصاصی فوتبال فقط در نبود تشخیص متنی،
        # به‌عنوان راهکار جایگزین استفاده می‌شود.
        if not text_scores:
            if (
                source_is_football
                or category_is_football
            ):
                if "football" in SPORTS:
                    text_scores["football"] = 1

                    logger.info(
                        "Sport detected from football source/category"
                    )

        if not text_scores:
            news.sport = None
            news.sport_name = None
            news.sport_emoji = None
            news.sport_hashtag = None

            logger.info("Sport: not detected")
            return news

        best = max(
            text_scores,
            key=text_scores.get,
        )

        sport_info = SPORTS[best]

        news.sport = best
        news.sport_name = sport_info["name"]
        news.sport_emoji = sport_info["emoji"]
        news.sport_hashtag = sport_info["hashtag"]

        logger.info(
            "Sport: %s (score=%s)",
            news.sport_name,
            text_scores[best],
        )

        return news
