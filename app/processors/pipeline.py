"""
KhabarF24 Processing Pipeline
"""

from app.models.raw_news import RawNews

from app.processors.language import LanguageDetector
from app.processors.translate import Translator

from app.processors.category import CategoryDetector
from app.processors.sport import SportDetector

from app.processors.importance import ImportanceScorer
from app.processors.credibility import CredibilityChecker

from app.processors.duplicate import DuplicateChecker
from app.processors.summarize import Summarizer

from app.utils.logger import logger


class NewsPipeline:

    def __init__(self):

        self.language = LanguageDetector()

        self.translator = Translator()

        self.category = CategoryDetector()

        self.sport = SportDetector()

        self.importance = ImportanceScorer()

        self.credibility = CredibilityChecker()

        self.duplicate = DuplicateChecker()

        self.summarizer = Summarizer()

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        logger.info("Pipeline Started")

        news = await self.language.process(news)

        news = await self.translator.process(news)

        news = await self.category.process(news)

        news = await self.sport.process(news)

        news = await self.importance.process(news)

        news = await self.credibility.process(news)

        news = await self.duplicate.process(news)

        news = await self.summarizer.process(news)

        logger.info("Pipeline Finished")

        return news
