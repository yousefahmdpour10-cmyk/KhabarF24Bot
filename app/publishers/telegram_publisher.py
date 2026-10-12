"""
Telegram Publisher - KhabarF24
ارسال نهایی خبر به کانال تلگرام
"""

import io

from telegram import Bot
from telegram.error import BadRequest

from config import settings
from app.models.raw_news import RawNews
from app.formatter.formatter import Formatter
from app.utils.watermark import build_watermarked_image
from app.utils.logger import logger

# محدودیت واقعی تلگرام برای توضیح زیر عکس/ویدیو (کوتاه‌تر از پیام متنی)
CAPTION_LIMIT = 1024

# پیش‌فرض کتابخانه‌ی تلگرام فقط ۵ ثانیه است و آپلود عکس گاهی بیشتر
# طول می‌کشد (خطای Timed out).
UPLOAD_TIMEOUT = 40


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

        نکته: عمداً parse_mode نمی‌گذاریم (متن ساده). قالب‌ها هیچ
        Markdown ای ندارند، ولی هشتگ‌هایی مثل #فرمول_یک یا #سری_آ یک
        زیرخط دارند و در Markdown قدیمی تلگرام باعث خطای
        "can't find end of the entity" و گم‌شدن کل پست می‌شدند.

        اگر خبر عکس داشته باشد و متن پست زیر محدودیت caption باشد،
        به‌صورت عکس (با لوگوی کانال) ارسال می‌شود؛ اگر تلگرام عکس را
        نپذیرد (BadRequest)، همان خبر به‌صورت متن ساده ارسال می‌شود.
        """
        try:
            text = await self.formatter.format(news)

            image_url = getattr(news, "image_url", None)

            if image_url and len(text) <= CAPTION_LIMIT:

                image_bytes = await build_watermarked_image(image_url)

                if image_bytes:

                    try:
                        await self.bot.send_photo(
                            chat_id=settings.CHANNEL_ID,
                            photo=io.BytesIO(image_bytes),
                            caption=text,
                            read_timeout=UPLOAD_TIMEOUT,
                            write_timeout=UPLOAD_TIMEOUT,
                            connect_timeout=20,
                        )

                        logger.info(
                            f"✅ Published (photo) to Telegram: {news.title[:70]}..."
                        )
                        return True

                    except BadRequest as e:
                        # عکس مشکل دارد؛ خبر را بدون عکس می‌فرستیم.
                        # (TimedOut عمداً گرفته نمی‌شود: ممکن است عکس
                        # واقعاً ارسال شده باشد و ارسال متن، تکراری شود.)
                        logger.warning(
                            f"TelegramPublisher: تلگرام عکس را نپذیرفت ({e}); ارسال متن ساده"
                        )

                else:
                    logger.warning(
                        "TelegramPublisher: ساخت عکس واترمارک‌دار ناموفق بود، ارسال متن ساده"
                    )

            await self.bot.send_message(
                chat_id=settings.CHANNEL_ID,
                text=text,
                disable_web_page_preview=True,
            )

            logger.info(f"✅ Published to Telegram: {news.title[:70]}...")
            return True

        except Exception as e:
            logger.error(f"❌ Telegram publish error: {e}")
            return False
