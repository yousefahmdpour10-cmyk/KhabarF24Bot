"""
app/processors/pipeline.py

KhabarF24 Processing Pipeline
"""

from app.ai.content_generator import ContentGenerator
from app.models.raw_news import RawNews

from app.processors.language.detector import LanguageDetector
from app.processors.category import CategoryDetector
from app.processors.sport import SportDetector
from app.processors.duplicate import DuplicateChecker
from app.processors.credibility import CredibilityChecker
from app.processors.importance import ImportanceScorer

from app.publishers.telegram_publisher import TelegramPublisher
from app.utils.logger import logger


class NewsPipeline:

    def __init__(self):
        self.language = LanguageDetector()
        self.category = CategoryDetector()
        self.sport = SportDetector()
        self.duplicate = DuplicateChecker()
        self.credibility = CredibilityChecker()
        self.importance = ImportanceScorer()
        self.content_generator = ContentGenerator()
        self.publisher = TelegramPublisher()

    async def process(self, news: RawNews) -> RawNews:
        logger.info("Pipeline Started")

        news = await self.language.process(news)
        news = await self.category.process(news)
        news = await self.sport.process(news)

        news = await self.duplicate.process(news)
        if getattr(news, "is_duplicate", False):
            logger.info("Pipeline Stopped: duplicate news")
            return news

        news = await self.credibility.process(news)
        if not getattr(news, "is_verified", True):
            logger.info("Pipeline Stopped: low credibility")
            return news

        news = await self.importance.process(news)

        news = await self.content_generator.process(news)
        if not getattr(news, "content_generated", False):
            logger.info("Pipeline Stopped: AI content generation failed, not publishing raw/untranslated text")
            return news

        await self.publisher.publish(news)

        logger.info("Pipeline Finished")
        return news
