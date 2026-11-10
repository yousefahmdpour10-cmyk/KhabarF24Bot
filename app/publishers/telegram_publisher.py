"""
Telegram Publisher - KhabarF24

ترتیب انتشار:
۱. ویدئوی واترمارک‌دار
۲. ویدئوی اصلی در صورت شکست واترمارک
۳. عکس واترمارک‌دار
۴. متن ساده

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
            raise ValueError(
                "BOT_TOKEN تنظیم نشده است"
            )

        if not settings.CHANNEL_ID:
            raise ValueError(
                "CHANNEL_ID تنظیم نشده است"
            )

        self.bot = Bot(
            token=settings.BOT_TOKEN
        )

        self.formatter = Formatter()

    # ==========================================================
    # Video URL
    # ==========================================================

    @staticmethod
    def _get_video_url(
        news: RawNews,
    ) -> str:
        """
        گرفتن URL ویدئو از مدل اصلی یا raw_data.
        """

        video_url = getattr(
            news,
            "video_url",
            None,
        )

        if not video_url and isinstance(
            getattr(news, "raw_data", None),
            dict,
        ):
            video_url = news.raw_data.get(
                "video_url"
            )

        return str(
            video_url or ""
        ).strip()

    # ==========================================================
    # Image URL
    # ==========================================================

    @staticmethod
    def _get_image_url(
        news: RawNews,
    ) -> str:
        """
        گرفتن URL تصویر.
        """

        image_url = getattr(
            news,
            "image_url",
            None,
        )

        if not image_url and isinstance(
            getattr(news, "raw_data", None),
            dict,
        ):
            image_url = (
                news.raw_data.get(
                    "image_url"
                )
                or news.raw_data.get(
                    "photo_url"
                )
            )

        return str(
            image_url or ""
        ).strip()

    # ==========================================================
    # Publish
    # ==========================================================

    async def publish(
        self,
        news: RawNews,
    ) -> bool:

        title = (
            getattr(news, "title", "")
            or ""
        )

        video_path = None

        try:

            # --------------------------------------------------
            # ساخت متن
            # --------------------------------------------------

            text = await self.formatter.format(
                news
            )

            if not isinstance(
                text,
                str,
            ):
                text = str(
                    text or ""
                )

            text = text.strip()

            if not text:

                logger.warning(
                    "Empty formatted text; "
                    "skipping: %s",
                    title[:70],
                )

                return False

            # --------------------------------------------------
            # رسانه‌ها
            # --------------------------------------------------

            video_url = self._get_video_url(
                news
            )

            image_url = self._get_image_url(
                news
            )

            logger.info(
                "MEDIA CHECK | title=%s | "
                "video=%s | image=%s",
                title[:70],
                bool(video_url),
                bool(image_url),
            )

            # ==================================================
            # مرحله اول:
            # ویدئوی واترمارک‌دار
            # ==================================================

            if video_url:

                logger.info(
                    "VIDEO CANDIDATE | title=%s | url=%s",
                    title[:70],
                    video_url[:180],
                )

                try:

                    video_path = (
                        await build_watermarked_video(
                            video_url
                        )
                    )

                    if video_path:

                        path = Path(
                            video_path
                        )

                        if (
                            not path.is_file()
                            or path.stat().st_size <= 0
                        ):

                            logger.warning(
                                "VIDEO WATERMARK OUTPUT "
                                "INVALID | title=%s | path=%s",
                                title[:70],
                                video_path,
                            )

                        elif (
                            path.stat().st_size
                            > 49 * 1024 * 1024
                        ):

                            logger.warning(
                                "VIDEO WATERMARK OUTPUT "
                                "TOO LARGE | title=%s | "
                                "size=%d",
                                title[:70],
                                path.stat().st_size,
                            )

                        elif len(text) > CAPTION_LIMIT:

                            logger.warning(
                                "VIDEO CAPTION TOO LONG | "
                                "title=%s | length=%d",
                                title[:70],
                                len(text),
                            )

                        else:

                            logger.info(
                                "VIDEO WATERMARK READY | "
                                "title=%s | size=%.2f MB",
                                title[:70],
                                path.stat().st_size
                                / (1024 * 1024),
                            )

                            with path.open(
                                "rb"
                            ) as video_file:

                                await self.bot.send_video(
                                    chat_id=(
                                        settings.CHANNEL_ID
                                    ),
                                    video=video_file,
                                    caption=text,
                                    supports_streaming=True,
                                    read_timeout=UPLOAD_TIMEOUT,
                                    write_timeout=UPLOAD_TIMEOUT,
                                    connect_timeout=30,
                                    pool_timeout=30,
                                )

                            logger.info(
                                "Published (watermarked video) "
                                "to Telegram: %s",
                                title[:70],
                            )

                            return True

                    else:

                        logger.warning(
                            "VIDEO WATERMARK RETURNED NONE | "
                            "title=%s",
                            title[:70],
                        )

                except (
                    BadRequest,
                    TelegramError,
                    OSError,
                    ValueError,
                    TypeError,
                    RuntimeError,
                ) as exc:

                    logger.warning(
                        "VIDEO WATERMARK FAILED | "
                        "title=%s | error=%s",
                        title[:70],
                        exc,
                    )

                finally:

                    if video_path:

                        try:

                            cleanup_watermarked_video(
                                video_path
                            )

                        except Exception as cleanup_error:

                            logger.warning(
                                "Video cleanup failed: %s",
                                cleanup_error,
                            )

                    video_path = None

                # ==================================================
                # مرحله دوم:
                # ارسال ویدئوی اصلی بدون واترمارک
                #
                # این fallback عمداً قبل از عکس است.
                # اگر واترمارک شکست خورد، ویدئو را از دست ندهیم.
                # ==================================================

                if len(text) <= CAPTION_LIMIT:

                    logger.warning(
                        "VIDEO FALLBACK DIRECT | "
                        "title=%s | url=%s",
                        title[:70],
                        video_url[:180],
                    )

                    try:

                        await self.bot.send_video(
                            chat_id=(
                                settings.CHANNEL_ID
                            ),
                            video=video_url,
                            caption=text,
                            supports_streaming=True,
                            read_timeout=UPLOAD_TIMEOUT,
                            write_timeout=UPLOAD_TIMEOUT,
                            connect_timeout=30,
                            pool_timeout=30,
                        )

                        logger.info(
                            "Published (original video) "
                            "to Telegram: %s",
                            title[:70],
                        )

                        return True

                    except (
                        BadRequest,
                        TelegramError,
                        OSError,
                        ValueError,
                        TypeError,
                    ) as exc:

                        logger.warning(
                            "DIRECT VIDEO UPLOAD FAILED | "
                            "title=%s | error=%s",
                            title[:70],
                            exc,
                        )

                else:

                    logger.warning(
                        "DIRECT VIDEO SKIPPED | "
                        "caption too long | "
                        "title=%s | length=%d",
                        title[:70],
                        len(text),
                    )

            else:

                logger.info(
                    "No video URL available; "
                    "trying photo/text: %s",
                    title[:70],
                )

            # ==================================================
            # مرحله سوم:
            # عکس واترمارک‌دار
            # ==================================================

            if (
                image_url
                and len(text) <= CAPTION_LIMIT
            ):

                try:

                    logger.info(
                        "PHOTO CANDIDATE | "
                        "title=%s | url=%s",
                        title[:70],
                        image_url[:180],
                    )

                    image_bytes = (
                        await build_watermarked_image(
                            image_url
                        )
                    )

                    if image_bytes:

                        await self.bot.send_photo(
                            chat_id=(
                                settings.CHANNEL_ID
                            ),
                            photo=image_bytes,
                            caption=text,
                            read_timeout=UPLOAD_TIMEOUT,
                            write_timeout=UPLOAD_TIMEOUT,
                            connect_timeout=30,
                            pool_timeout=30,
                        )

                        logger.info(
                            "Published (photo) "
                            "to Telegram: %s",
                            title[:70],
                        )

                        return True

                    logger.warning(
                        "Image watermarking returned "
                        "no image: %s",
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
                    "No image URL available; "
                    "trying text: %s",
                    title[:70],
                )

            # ==================================================
            # مرحله چهارم:
            # متن ساده
            # ==================================================

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
