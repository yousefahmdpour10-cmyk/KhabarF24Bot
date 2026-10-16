"""
Telegram Publisher - KhabarF24
انتشار خبر به ترتیب اولویت:
۱. ویدئوی واترمارک‌دار
۲. عکس واترمارک‌دار
۳. متن ساده
"""

from pathlib import Path

from telegram import Bot
from telegram.error import TelegramError, BadRequest

from config import settings
from app.models.raw_news import RawNews
from app.formatter.formatter import Formatter
from app.utils.watermark import build_watermarked_image
from app.utils.video_watermark import (
    build_watermarked_video,
    cleanup_watermarked_video,
)
from app.utils.logger import logger


CAPTION_LIMIT = 1024
UPLOAD_TIMEOUT = 120


class TelegramPublisher:
    def __init__(self):
        if not settings.BOT_TOKEN:
            raise ValueError("BOT_TOKEN تنظیم نشده است")

        if not settings.CHANNEL_ID:
            raise ValueError("CHANNEL_ID تنظیم نشده است")

        self.bot = Bot(token=settings.BOT_TOKEN)
        self.formatter = Formatter()

    async def publish(self, news: RawNews) -> bool:
        title = getattr(news, "title", "") or ""

        try:
            text = await self.formatter.format(news)
            if not isinstance(text, str):
                text = str(text or "")

            # مرحله اول: انتشار ویدئوی واترمارک‌دار
            video_url = (
                getattr(news, "video_url", None) or ""
            ).strip()

            if video_url and len(text) <= CAPTION_LIMIT:
                logger.info(
                    "VIDEO CANDIDATE: title=%s | url=%s",
                    title[:70],
                    video_url[:180],
                )

                video_path = await build_watermarked_video(video_url)

                if video_path:
                    try:
                        path = Path(video_path)

                        if not path.is_file() or path.stat().st_size == 0:
                            logger.warning(
                                "Watermarked video file is missing or empty: %s",
                                video_path,
                            )
                        else:
                            with path.open("rb") as video_file:
                                await self.bot.send_video(
                                    chat_id=settings.CHANNEL_ID,
                                    video=video_file,
                                    caption=text,
                                    supports_streaming=True,
                                    read_timeout=UPLOAD_TIMEOUT,
                                    write_timeout=UPLOAD_TIMEOUT,
                                    connect_timeout=30,
                                    pool_timeout=30,
                                )

                            logger.info(
                                "Published (video) to Telegram: %s",
                                title[:70],
                            )
                            return True

                    except (BadRequest, TelegramError, OSError) as exc:
                        logger.warning(
                            "Video upload failed; trying photo/text: %s",
                            exc,
                        )

                    finally:
                        cleanup_watermarked_video(video_path)

                else:
                    logger.warning(
                        "Video watermarking failed; trying photo/text: %s",
                        title[:70],
                    )

            elif video_url:
                logger.info(
                    "Video available but caption exceeds Telegram limit; "
                    "trying photo/text: %s",
                    title[:70],
                )
            else:
                logger.info(
                    "No video_url available; trying photo/text: %s",
                    title[:70],
                )

            # مرحله دوم: انتشار عکس واترمارک‌دار
            image_url = (
                getattr(news, "image_url", None) or ""
            ).strip()

            if image_url and len(text) <= CAPTION_LIMIT:
                try:
                    image_bytes = await build_watermarked_image(image_url)

                    if image_bytes:
                        await self.bot.send_photo(
                            chat_id=settings.CHANNEL_ID,
                            photo=image_bytes,
                            caption=text,
                            read_timeout=UPLOAD_TIMEOUT,
                            write_timeout=UPLOAD_TIMEOUT,
                            connect_timeout=30,
                            pool_timeout=30,
                        )

                        logger.info(
                            "Published (photo) to Telegram: %s",
                            title[:70],
                        )
                        return True

                    logger.warning(
                        "Image watermarking failed; trying text: %s",
                        title[:70],
                    )

                except (BadRequest, TelegramError, OSError, ValueError) as exc:
                    logger.warning(
                        "Photo upload failed; trying text: %s",
                        exc,
                    )

            elif image_url:
                logger.info(
                    "Image available but caption exceeds Telegram limit; "
                    "trying text: %s",
                    title[:70],
                )
            else:
                logger.info(
                    "No image_url available; trying text: %s",
                    title[:70],
                )

            # مرحله سوم: انتشار متن
            await self.bot.send_message(
                chat_id=settings.CHANNEL_ID,
                text=text,
                disable_web_page_preview=True,
                read_timeout=UPLOAD_TIMEOUT,
                write_timeout=UPLOAD_TIMEOUT,
                connect_timeout=30,
                pool_timeout=30,
            )

            logger.info(
                "Published (text) to Telegram: %s",
                title[:70],
            )
            return True

        except Exception:
            logger.exception(
                "Telegram publish error for '%s'",
                title[:70],
            )
            return False
