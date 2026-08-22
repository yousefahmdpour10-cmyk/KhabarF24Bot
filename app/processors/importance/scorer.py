"""
Importance Scorer
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger

from .category_scores import CATEGORY_SCORES
from .keywords import KEYWORD_SCORES
from .source_scores import SOURCE_SCORES


class ImportanceScorer:

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        score = 0

        text = f"{news.title} {news.summary}".lower()

        for keyword, value in KEYWORD_SCORES.items():
            if keyword.lower() in text:
                score += value

        score += CATEGORY_SCORES.get(
            news.category,
            0,
        )

        score += SOURCE_SCORES.get(
            news.source,
            0,
        )

        news.importance_score = score

        logger.info(
            f"Importance Score: {score}"
        )

        return news
