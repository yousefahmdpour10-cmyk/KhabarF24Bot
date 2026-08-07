"""
Telegram Publisher - KhabarF24
ارسال نهایی خبر به کانال تلگرام
"""

from telegram import Bot

from app.config import settings
from app.models.raw_news import RawNews
from app.formatter.formatter import format_news
from app.formatter.sports.football.builder import FootballBuilder
from app.utils.logger import logger


class TelegramPublisher:

    def __init__(self):
        if not settings.BOT_TOKEN:
            raise ValueError("BOT_TOKEN تنظیم نشده است")
        if not settings.CHANNEL_ID:
            raise ValueError("CHANNEL_ID تنظیم نشده است")

        self.bot = Bot(token=settings.BOT_TOKEN)
        self.football_builder = FootballBuilder()

    def _build_text(self, news: RawNews) -> str:
        """
        تصمیم می‌گیرد کدام formatter/builder متن نهایی پست را بسازد.

        - category == "sports" و sport == "football" -> FootballBuilder
          (گزارش کامل بازی: ترکیب، داور، ورزشگاه و غیره)
        - هر خبر دیگری (سیاست/جهان/اقتصاد/... و رشته‌های ورزشی که هنوز
          builder اختصاصی ندارند) -> قالب عمومی format_news
        """
        if news.category == "sports" and news.sport == "football":
            return self.football_builder.build(news)

        return format_news(news)

    async def publish(self, news: RawNews) -> bool:
        """
        یک خبر را به کانال ارسال می‌کند
        """
        try:
            text = self._build_text(news)

            await self.bot.send_message(
                chat_id=settings.CHANNEL_ID,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

            logger.info(f"✅ Published to Telegram: {news.title[:70]}...")
            return True

        except Exception as e:
            logger.error(f"❌ Telegram publish error: {e}")
            return False
