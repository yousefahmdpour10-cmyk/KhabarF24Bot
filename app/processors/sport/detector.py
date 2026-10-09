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


# منابع خبری اختصاصی یا متمرکز بر فوتبال
FOOTBALL_SOURCES = (
    "bbc football",
    "bbc sport",
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
        ).strip().lower()

        source_category = str(
            getattr(news, "category", "") or ""
        ).strip().lower()

        article_text = " ".join(
            (title, summary, content)
        )

        text_scores = defaultdict(int)

        # مرحله اول: تشخیص بر اساس کلمات متن خبر
        for sport_id, sport in SPORTS.items():
            for keyword in sport.get("keywords", []):
                if keyword_in_text(keyword, article_text):
                    text_scores[sport_id] += 1

        # مرحله دوم: تشخیص منبع اختصاصی فوتبال
        source_is_football = any(
            keyword in source_name
            for keyword in FOOTBALL_SOURCES
        )

        category_is_football = any(
            keyword in source_category
            for keyword in FOOTBALL_SOURCE_CATEGORIES
        )

        football_available = "football" in SPORTS

        # اگر منبع اختصاصی فوتبال است و متن شواهد کافی
        # برای رشته ورزشی دیگری ندارد، فوتبال را تقویت کن.
        if source_is_football or category_is_football:
            if football_available:
                football_score = text_scores.get("football", 0)
                other_scores = {
                    sport_id: score
                    for sport_id, score in text_scores.items()
                    if sport_id != "football"
                }

                if not other_scores or football_score >= max(
                    other_scores.values()
                ):
                    text_scores["football"] = max(
                        football_score,
                        1,
                    )

                    logger.info(
                        "Sport source boost: source=%s category=%s",
                        source_name,
                        source_category,
                    )

        if not text_scores:
            news.sport = None
            news.sport_name = None
            news.sport_emoji = None
            news.sport_hashtag = None

            logger.info("Sport: not detected")
            return news

        # بیشترین امتیاز؛ در تساوی، فوتبال اولویت دارد
        best = max(
            text_scores,
            key=lambda sport_id: (
                text_scores[sport_id],
                sport_id == "football",
            ),
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
