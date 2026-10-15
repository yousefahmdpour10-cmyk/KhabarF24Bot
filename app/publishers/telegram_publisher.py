"""
Telegram Publisher - KhabarF24
انتشار خبر به شکل ویدئو، عکس واترمارک‌دار یا متن.
"""

import io

from telegram import Bot
from telegram.error import BadRequest

from config import settings
from app.models.raw_news import RawNews
from app.formatter.formatter import Formatter
from app.utils.watermark import build_watermarked_image
from app.utils.video_watermark import build_watermarked_video
from app.utils.logger import logger

CAPTION_LIMIT = 1024
UPLOAD_TIMEOUT = 60


class TelegramPublisher:

    def __init__(self):
        if not settings.BOT_TOKEN:
            raise ValueError("BOT_TOKEN تنظیم نشده است")
        if not settings.CHANNEL_ID:
            raise ValueError("CHANNEL_ID تنظیم نشده است")

        self.bot = Bot(token=settings.BOT_TOKEN)
        self.formatter = Formatter()

    async def publish(self, news: RawNews) -> bool:
        try:
            text = await self.formatter.format(news)

            # ۱. ابتدا ویدئو را امتحان کن.
            video_url = getattr(news, "video_url", None)

            if video_url and len(text) <= CAPTION_LIMIT:
                video_bytes = await build_watermarked_video(video_url)

                if video_bytes:
                    try:
                        await self.bot.send_video(
                            chat_id=settings.CHANNEL_ID,
                            video=io.BytesIO(video_bytes),
                            caption=text,
                            supports_streaming=True,
                            read_timeout=UPLOAD_TIMEOUT,
                            write_timeout=UPLOAD_TIMEOUT,
                            connect_timeout=20,
                            pool_timeout=20,
                        )

                        logger.info(
                            f"Published (video) to Telegram: {news.title[:70]}"
                        )
                        return True

                    except BadRequest as exc:
                        logger.warning(
                            f"Telegram rejected video; trying photo/text: {exc}"
                        )
                else:
                    logger.warning(
                        "Video processing failed; trying photo/text"
                    )

            # ۲. اگر ویدئو موجود یا قابل پردازش نبود، عکس را امتحان کن.
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
                            pool_timeout=20,
                        )

                        logger.info(
                            f"Published (photo) to Telegram: {news.title[:70]}"
                        )
                        return True

                    except BadRequest as exc:
                        logger.warning(
                            f"Telegram rejected photo; sending text: {exc}"
                        )
                else:
                    logger.warning(
                        "Photo watermark failed; sending text"
                    )

            # ۳. آخرین راه: متن ساده.
            await self.bot.send_message(
                chat_id=settings.CHANNEL_ID,
                text=text,
                disable_web_page_preview=True,
                read_timeout=UPLOAD_TIMEOUT,
                write_timeout=UPLOAD_TIMEOUT,
                connect_timeout=20,
                pool_timeout=20,
            )

            logger.info(f"Published (text) to Telegram: {news.title[:70]}")
            return True

        except Exception as exc:
            logger.error(
                f"Telegram publish error for '{getattr(news, 'title', '')[:70]}': "
                f"{exc}"
            )
            return False
