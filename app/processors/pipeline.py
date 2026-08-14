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
        # ترجمه + خلاصه‌نویسی + تیتر، هر سه با یک فراخوانی Gemini
        # (جایگزین Translator و Summarizer قدیمی)
        self.content_generator = ContentGenerator()
        self.publisher = TelegramPublisher()

    async def process(self, news: RawNews) -> RawNews:
        logger.info("Pipeline Started")

        news = await self.language.process(news)
        news = await self.category.process(news)
        news = await self.sport.process(news)

        # فیلترهای ارزان قبل از هر کاری که سهمیه/زمان مصرف می‌کند
        news = await self.duplicate.process(news)
        if news.is_duplicate:
            logger.info("Pipeline Stopped: duplicate news")
            return news

        news = await self.credibility.process(news)
        if not news.is_verified:
            logger.info("Pipeline Stopped: low credibility")
            return news

        news = await self.importance.process(news)

        # فقط برای خبرهایی که تا اینجا رد شدند، سهمیه‌ی رایگان Gemini مصرف می‌شود
        news = await self.content_generator.process(news)

        await self.publisher.publish(news)

        logger.info("Pipeline Finished")
        return news
