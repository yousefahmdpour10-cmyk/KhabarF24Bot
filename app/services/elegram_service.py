"""
Telegram Service - KhabarF24
ارسال نهایی خبر به کانال تلگرام
"""

from telegram import Bot
from app.core.config import BOT_TOKEN, CHANNEL_ID   # مسیر config را مطابق پروژه‌ات تنظیم کن
from app.models.raw_news import RawNews
from app.formatter.formatter import Formatter
from app.utils.logger import logger


class TelegramService:

    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.formatter = Formatter()

    async def send_news(self, news: RawNews) -> bool:
        """
        ارسال یک خبر به کانال
        """
        try:
            # ساخت متن نهایی با Template
            text = await self.formatter.format(news)

            await self.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode="Markdown"
            )

            logger.info(f"✅ Sent to Telegram: {news.title[:60]}...")
            return True

        except Exception as e:
            logger.error(f"❌ Telegram Error: {e}")
            return False
