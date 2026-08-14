"""
Duplicate Checker
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger

from .normalizer import NewsNormalizer
from .similarity import SimilarityEngine


class DuplicateChecker:

    def __init__(self):

        # بعداً این قسمت با دیتابیس جایگزین می‌شود
        self.cache = []

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        text = NewsNormalizer.normalize(
            f"{news.title} {news.summary}"
        )

        news.is_duplicate = False
        news.duplicate_score = 0

        for old_text in self.cache:

            similarity = SimilarityEngine.compare(
                text,
                old_text,
            )

            if similarity >= 0.90:

                news.is_duplicate = True
                news.duplicate_score = similarity

                logger.info(
                    f"Duplicate ({similarity:.2f})"
                )

                return news

        self.cache.append(text)

        logger.info("Unique News")

        return news
