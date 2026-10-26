"""
Sport Detector

تشخیص رشته ورزشی (و مسابقه‌ی مربوط به آن برای هشتگ)
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.sport.keywords import SPORTS
from app.processors.sport.league_detector import detect_league
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


class SportDetector:
    """
    تشخیص رشته ورزشی
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # اگر fetcher مطمئنی (مثل ESPN) رشته را از قبل مشخص کرده، آن را
        # با حدسِ کلیدواژه‌ای خراب نمی‌کنیم.
        if getattr(news, "sport", None):
            logger.info(
                f"Sport: {getattr(news, 'sport_name', news.sport)} (از منبع مشخص شده)"
            )
            return news

        text = f"{news.title} {news.summary}"

        scores = defaultdict(int)

        for sport_id, sport in SPORTS.items():

            for keyword in sport["keywords"]:

                if keyword_in_text(keyword, text):

                    scores[sport_id] += 1

        if scores:

            best = max(
                scores,
                key=scores.get,
            )

            news.sport = best

            news.sport_name = SPORTS[best]["name"]

            news.sport_emoji = SPORTS[best]["emoji"]

            news.sport_hashtag = SPORTS[best]["hashtag"]

            logger.info(
                f"Sport: {news.sport_name}"
            )

            # مسابقه (لیگ یا جام) برای هشتگ دوم پست
            if not getattr(news, "league", None):
                league = detect_league(text)

                if league:
                    news.league = league
                    logger.info(f"League: {league}")

        else:

            news.sport = None

            news.sport_name = None

            news.sport_emoji = None

            news.sport_hashtag = None

        return news
