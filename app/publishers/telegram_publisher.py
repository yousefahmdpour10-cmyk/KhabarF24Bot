"""
Telegram Publisher - KhabarF24
ارسال نهایی خبر به کانال تلگرام
"""

from telegram import Bot

from config import settings
from app.models.raw_news import RawNews
from app.formatter.formatter import Formatter
from app.utils.logger import logger


class TelegramPublisher:

    def __init__(self):
        if not settings.BOT_TOKEN:
            raise ValueError("BOT_TOKEN تنظیم نشده است")
        if not settings.CHANNEL_ID:
            raise ValueError("CHANNEL_ID تنظیم نشده است")

        self.bot = Bot(token=settings.BOT_TOKEN)
        self.formatter = Formatter()

    async def publish(self, news: RawNews) -> bool:
        """
        یک خبر را به کانال ارسال می‌کند.

        مسیریابی بین دسته‌ها (سیاست/ایران/جهان/... و رشته‌های ورزشی مثل
        فوتبال/بسکتبال/...) کاملاً داخل Formatter انجام می‌شود؛ این فایل
        هیچ تصمیمی درباره‌ی نوع خبر نمی‌گیرد.
        """
        try:
            text = await self.formatter.format(news)

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
