"""
KhabarF24 Processing Pipeline
Detailed diagnostics for news processing and publishing.
"""

from app.ai.content_generator import ContentGenerator
from app.models.raw_news import RawNews

from app.processors.language.detector import LanguageDetector
from app.processors.sport import SportDetector
from app.processors.category import CategoryDetector
from app.processors.duplicate import DuplicateChecker
from app.processors.duplicate.story_match import is_same_story
from app.processors.credibility import CredibilityChecker
from app.processors.importance import ImportanceScorer

from app.publishers.telegram_publisher import TelegramPublisher
from app.utils.logger import logger


class NewsPipeline:

    def __init__(self):
        self.language = LanguageDetector()
        self.sport = SportDetector()
        self.category = CategoryDetector()
        self.duplicate = DuplicateChecker()
        self.credibility = CredibilityChecker()
        self.importance = ImportanceScorer()
        self.content_generator = ContentGenerator()
        self.publisher = TelegramPublisher()

    async def process(self, news: RawNews) -> RawNews:
        source = str(getattr(news, "source", "") or "Unknown")
        original_title = str(getattr(news, "title", "") or "")
        title_preview = original_title[:100]

        logger.info(
            "Pipeline Started | source=%s | title=%s",
            source,
            title_preview,
        )

        try:
            news = await self.language.process(news)
            news = await self.sport.process(news)
            news = await self.category.process(news)

            sport_name = getattr(news, "sport_name", None)
            category = getattr(news, "category", "unknown")

            logger.info(
                "Classification | source=%s | category=%s | sport=%s",
                source,
                category,
                sport_name or "not detected",
            )

            news = await self.duplicate.process(news)

            if getattr(news, "is_duplicate", False):
                logger.info(
                    "Pipeline Stopped: duplicate | source=%s | title=%s",
                    source,
                    title_preview,
                )
                return news

            news = await self.credibility.process(news)

            credibility_score = getattr(
                news,
                "credibility_score",
                None,
            )

            if not getattr(news, "is_verified", True):
                logger.warning(
                    "Pipeline Stopped: low credibility | "
                    "source=%s | score=%s | title=%s",
                    source,
                    credibility_score,
                    title_preview,
                )
                return news

            news = await self.importance.process(news)

            logger.info(
                "News passed filters | source=%s | "
                "credibility=%s | importance=%s | category=%s | sport=%s",
                source,
                credibility_score,
                getattr(news, "importance_score", None),
                category,
                sport_name or "not detected",
            )

            news = await self.content_generator.process(news)

            # خبر بی‌محتوا (مثل «N12»): برای همیشه رد می‌شود تا هر چرخه
            # دوباره امتحان نشود
            if getattr(news, "junk_content", False):
                self.duplicate.mark_seen(news)

                logger.info(
                    "Pipeline Stopped: not enough content | "
                    "source=%s | title=%s",
                    source,
                    title_preview,
                )
                return news

            if not getattr(news, "content_generated", False):

                # نوبت Gemini نیست: خطا نیست، دوباره امتحان می‌شود
                if getattr(news, "ai_paused", False):
                    logger.info(
                        "Pipeline Paused: Gemini pacing | source=%s",
                        source,
                    )
                    return news

                logger.warning(
                    "Pipeline Stopped: AI content generation failed | "
                    "source=%s | category=%s | sport=%s | title=%s",
                    source,
                    category,
                    sport_name or "not detected",
                    str(getattr(news, "title", "") or "")[:100],
                )
                return news

            # همین خبر قبلاً از منبع دیگری منتشر شده (تیتر فارسی تقریباً
            # یکسان)؛ دوباره منتشر نمی‌شود.
            # (پست‌های ESPN تیتر فارسیِ قالبی دارند و مستثنی‌اند)
            if not getattr(news, "skip_story_repeat", False) and (
                self.duplicate.is_story_repeat(news)
                or is_same_story(
                    getattr(news, "title", ""),
                    self.duplicate.headlines[-300:],
                )
            ):
                news.is_duplicate = True
                self.duplicate.mark_seen(news)

                logger.info(
                    "Pipeline Stopped: same story already published | "
                    "source=%s | title=%s",
                    source,
                    str(getattr(news, "title", "") or "")[:100],
                )
                return news

            published = await self.publisher.publish(news)
            news.published = bool(published)

            if published:
                self.duplicate.mark_seen(news)

                logger.info(
                    "Pipeline Finished: PUBLISHED | "
                    "source=%s | category=%s | sport=%s | title=%s",
                    source,
                    category,
                    sport_name or "not detected",
                    str(getattr(news, "title", "") or "")[:100],
                )
            else:
                logger.warning(
                    "Pipeline Stopped: Telegram publish failed | "
                    "source=%s | category=%s | sport=%s | title=%s",
                    source,
                    category,
                    sport_name or "not detected",
                    str(getattr(news, "title", "") or "")[:100],
                )

            return news

        except Exception:
            logger.exception(
                "Pipeline Exception | source=%s | title=%s",
                source,
                title_preview,
            )
            raise
