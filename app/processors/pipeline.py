"""
KhabarF24 Processing Pipeline - Final with Telegram Publish
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

from app.publishers.telegram_publisher import TelegramPublisher
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
        self.publisher = TelegramPublisher()   # ← اضافه شد

    async def process(self, news: RawNews) -> RawNews:
        logger.info("Pipeline Started")

        news = await self.language.process(news)
        news = await self.translator.process(news)
        news = await self.category.process(news)
        news = await self.sport.process(news)
        news = await self.importance.process(news)
        news = await self.credibility.process(news)
        news = await self.duplicate.process(news)
        news = await self.summarizer.process(news)

        # ارسال به تلگرام
        published = await self.publisher.publish(news)
        if published:
            logger.info("News published to Telegram successfully")
        else:
            logger.warning("Failed to publish news to Telegram")

        logger.info("Pipeline Finished")
        return news
