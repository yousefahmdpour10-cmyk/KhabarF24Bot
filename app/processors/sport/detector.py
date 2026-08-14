"""
Sport Detector

تشخیص رشته ورزشی
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.sport.keywords import SPORTS
from app.utils.logger import logger


class SportDetector:
    """
    تشخیص رشته ورزشی
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        text = f"{news.title} {news.summary}".lower()

        scores = defaultdict(int)

        for sport_id, sport in SPORTS.items():

            for keyword in sport["keywords"]:

                if keyword.lower() in text:

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

        else:

            news.sport = None

            news.sport_name = None

            news.sport_emoji = None

            news.sport_hashtag = None

        return news
