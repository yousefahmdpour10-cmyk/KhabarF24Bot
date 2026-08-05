"""
Telegram Service - KhabarF24
ارسال خبر به کانال تلگرام
"""

from telegram import Bot
from config.settings import BOT_TOKEN, CHANNEL_ID
from app.models.raw_news import RawNews
from app.formatter.formatter import Formatter
from app.utils.logger import logger


class TelegramService:

    def __init__(self):
        if not BOT_TOKEN or not CHANNEL_ID:
            raise ValueError("BOT_TOKEN یا CHANNEL_ID تنظیم نشده است")

        self.bot = Bot(token=BOT_TOKEN)
        self.formatter = Formatter()

    async def send_news(self, news: RawNews) -> bool:
        """
        یک خبر را به کانال ارسال می‌کند
        """
        try:
            text = await self.formatter.format(news)

            await self.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

            logger.info(f"✅ Sent to Telegram: {news.title[:70]}...")
            return True

        except Exception as e:
            logger.error(f"❌ Telegram send error: {e}")
            return False
