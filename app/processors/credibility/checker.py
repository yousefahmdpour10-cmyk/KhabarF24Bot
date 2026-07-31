"""
Credibility Checker
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger

from .rules import MIN_CREDIBILITY_SCORE
from .source_reputation import SOURCE_REPUTATION


class CredibilityChecker:

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        score = SOURCE_REPUTATION.get(
            news.source_name,
            50,
        )

        news.credibility_score = score

        news.is_verified = (
            score >= MIN_CREDIBILITY_SCORE
        )

        logger.info(
            f"Credibility: {score}"
        )

        return news
