"""
Telegram Publisher - KhabarF24
ترتیب انتشار:
۱. ویدئوی واترمارک‌دار
۲. عکس واترمارک‌دار
۳. متن ساده

سازگار با RawNews و رسانه‌های استخراج‌شده از شبکه‌های اجتماعی.
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

    @staticmethod
    def _get_video_url(news: RawNews) -> str:
        """گرفتن URL ویدئو از مدل اصلی یا داده‌های خام."""

        video_url = getattr(news, "video_url", None)

        if not video_url and isinstance(
            getattr(news, "raw_data", None), dict
        ):
            video_url = news.raw_data.get("video_url")

        return str(video_url or "").strip()

    @staticmethod
    def _get_image_url(news: RawNews) -> str:
        """گرفتن URL تصویر."""

        image_url = getattr(news, "image_url", None)

        if not image_url and isinstance(
            getattr(news, "raw_data", None), dict
        ):
            image_url = (
                news.raw_data.get("image_url")
                or news.raw_data.get("photo_url")
            )

        return str(image_url or "").strip()

    async def publish(self, news: RawNews) -> bool:
        title = getattr(news, "title", "") or ""
        video_path = None

        try:
            text = await self.formatter.format(news)

            if not isinstance(text, str):
                text = str(text or "")

            text = text.strip()

            if not text:
                logger.warning(
                    "Empty formatted text; skipping: %s",
                    title[:70],
                )
                return False

            video_url = self._get_video_url(news)
            image_url = self._get_image_url(news)

            # مرحله اول: ویدئوی واترمارک‌دار
            if video_url:
                logger.info(
                    "VIDEO CANDIDATE: title=%s | url=%s",
                    title[:70],
                    video_url[:180],
                )

                try:
                    video_path = await build_watermarked_video(
                        video_url
                    )

                    if video_path:
                        path = Path(video_path)

                        if not path.is_file() or path.stat().st_size == 0:
                            logger.warning(
                                "Watermarked video is missing or empty: %s",
                                video_path,
                            )
                        elif len(text) <= CAPTION_LIMIT:
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
                        else:
                            logger.warning(
                                "Caption exceeds video caption limit; "
                                "trying photo/text: %s",
                                title[:70],
                            )
                    else:
                        logger.warning(
                            "Video watermarking returned no file: %s",
                            title[:70],
                        )

                except (
                    BadRequest,
                    TelegramError,
                    OSError,
                    ValueError,
                    TypeError,
                ) as exc:
                    logger.warning(
                        "Video processing/upload failed; "
                        "trying photo/text: %s",
                        exc,
                    )

                finally:
                    if video_path:
                        try:
                            cleanup_watermarked_video(video_path)
                        except Exception as cleanup_error:
                            logger.warning(
                                "Video cleanup failed: %s",
                                cleanup_error,
                            )

                    video_path = None

            else:
                logger.info(
                    "No video URL available; trying photo/text: %s",
                    title[:70],
                )

            # مرحله دوم: عکس واترمارک‌دار
            if image_url and len(text) <= CAPTION_LIMIT:
                try:
                    image_bytes = await build_watermarked_image(
                        image_url
                    )

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
                        "Image watermarking returned no image: %s",
                        title[:70],
                    )

                except (
                    BadRequest,
                    TelegramError,
                    OSError,
                    ValueError,
                    TypeError,
                ) as exc:
                    logger.warning(
                        "Photo processing/upload failed; "
                        "trying text: %s",
                        exc,
                    )

            elif image_url:
                logger.info(
                    "Caption exceeds photo caption limit; "
                    "trying text: %s",
                    title[:70],
                )

            else:
                logger.info(
                    "No image URL available; trying text: %s",
                    title[:70],
                )

            # مرحله سوم: متن کامل
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
