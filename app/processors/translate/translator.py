"""
Translation Processor
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger

from .google import GoogleTranslateEngine


class Translator:
    """
    مترجم خبر
    """

    def __init__(self):

        self.engine = GoogleTranslateEngine()

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        if news.language == "fa":

            return news

        logger.info(
            f"Translating from {news.language}..."
        )

        news.title = await self.engine.translate(
            news.title,
            news.language,
            "fa",
        )

        if news.summary:

            news.summary = await self.engine.translate(
                news.summary,
                news.language,
                "fa",
            )

        news.language = "fa"

        return news
