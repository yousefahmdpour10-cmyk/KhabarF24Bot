"""
Watermark Utility

دانلود عکس خبر و چسباندن لوگوی شفاف KhabarF24 (گوشه‌ی پایین‌چپ،
بدون پس‌زمینه‌ی مشکی -- چون خودِ فایل لوگو از قبل PNG شفاف است).
"""

import io
from pathlib import Path
from typing import Optional

import aiohttp
from PIL import Image

from app.utils.logger import logger

LOGO_PATH = Path("assets/khabarf24_header_transparent_final.png")

# عرض لوگو نسبت به عرض عکس خبر
LOGO_WIDTH_RATIO = 0.30
MARGIN_RATIO = 0.04

# عکس‌های خیلی بزرگ منبع قبل از آپلود به تلگرام کوچک می‌شوند
# (آپلود سریع‌تر، خطای Timed out کمتر)
MAX_IMAGE_SIDE = 1600


async def _download_image(url: str) -> Optional[bytes]:

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()

                logger.warning(
                    f"Watermark: دانلود عکس ناموفق، HTTP {response.status} -> {url}"
                )

    except Exception as e:
        logger.warning(f"Watermark: خطا در دانلود عکس -> {e}")

    return None


def _add_watermark(image_bytes: bytes) -> Optional[bytes]:

    try:
        base = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        base.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE), Image.LANCZOS)

        if not LOGO_PATH.exists():
            logger.warning(f"Watermark: فایل لوگو پیدا نشد -> {LOGO_PATH}")
            fallback = io.BytesIO()
            base.convert("RGB").save(fallback, format="JPEG", quality=90)
            return fallback.getvalue()

        logo = Image.open(LOGO_PATH).convert("RGBA")

        logo_width = int(base.width * LOGO_WIDTH_RATIO)
        logo_ratio = logo_width / logo.width
        logo_height = int(logo.height * logo_ratio)
        logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

        margin = int(base.width * MARGIN_RATIO)
        position = (
            margin,
            base.height - logo_height - margin,
        )

        # لوگو خودش کانال آلفا (شفافیت) دارد، پس با mask خودش
        # چسبانده می‌شود -- فقط خطوط واقعی لوگو دیده می‌شوند، نه
        # هیچ پس‌زمینه‌ای.
        base.paste(logo, position, logo)

        output = io.BytesIO()
        base.convert("RGB").save(output, format="JPEG", quality=90)
        return output.getvalue()

    except Exception as e:
        logger.warning(f"Watermark: خطا در ساخت واترمارک -> {e}")
        return None


async def build_watermarked_image(url: str) -> Optional[bytes]:
    """
    عکس خبر را از url دانلود می‌کند و لوگوی KhabarF24 را گوشه‌ی
    پایین‌چپ آن می‌چسباند. اگر هر مرحله شکست بخورد، None برمی‌گرداند
    تا فراخوان بتواند به حالت متن‌ساده برگردد.
    """

    if not url:
        return None

    raw = await _download_image(url)

    if not raw:
        return None

    return _add_watermark(raw)


"""
RSS Fetcher

دریافت خبرها از منابع RSS
"""

import feedparser
from datetime import datetime
from typing import List, Optional

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.http_client import HTTPClient


class RSSFetcher(BaseFetcher):
    """
    دریافت خبر از RSS
    """

    def __init__(self, source):
        super().__init__(source)
        self.http = HTTPClient()

    async def fetch(self) -> List[RawNews]:
        """
        دریافت خبرها از RSS
        """

        news_list: List[RawNews] = []

        rss_url = (
            getattr(self.source, "rss_url", None)
            or self.source.url
        )

        if not rss_url:
            print(
                f"RSS URL MISSING: {self.source.name}"
            )
            return news_list

        try:
            xml = await self.http.get(rss_url)
        except Exception as exc:
            print(
                f"RSS FETCH ERROR: {self.source.name} | "
                f"url={rss_url} | error={exc}"
            )
            return news_list

        if not xml:
            print(
                f"RSS FETCH FAILED: {self.source.name} | "
                f"url={rss_url} | response is empty"
            )
            return news_list

        try:
            feed = feedparser.parse(xml)
        except Exception as exc:
            print(
                f"RSS PARSE ERROR: {self.source.name} | "
                f"error={exc}"
            )
            return news_list

        if feed.bozo:
            print(
                f"RSS PARSE WARNING: {self.source.name} | "
                f"{getattr(feed, 'bozo_exception', 'unknown error')}"
            )

        print(
            f"RSS RESULT: {self.source.name} | "
            f"entries={len(feed.entries)} | "
            f"url={rss_url}"
        )

        source_categories = list(
            getattr(self.source, "categories", None) or []
        )

        for entry in feed.entries:
            try:
                news = RawNews(
                    source_id=self.source.id,
                    source=self.source.name,
                    source_category_hint=source_categories,
                    title=getattr(entry, "title", "") or "",
                    content=self._extract_content(entry),
                    summary=getattr(entry, "summary", "") or "",
                    url=getattr(entry, "link", "") or "",
                    published_at=self._extract_published_at(entry),
                    language=self.source.language,
                    category=(
                        source_categories[0]
                        if source_categories
                        else ""
                    ),
                    image_url=self._extract_image_url(entry),
                    raw_data=dict(entry),
                    tags=list(
                        getattr(entry, "tags", []) or []
                    ),
                )

                if not news.title and not news.content and not news.url:
                    continue

                news_list.append(news)

            except Exception as exc:
                print(
                    f"RSS ENTRY ERROR: {self.source.name} | "
                    f"error={exc}"
                )

        print(
            f"RSS PARSED: {self.source.name} | "
            f"news={len(news_list)}"
        )

        return news_list

    @staticmethod
    def _extract_content(entry) -> str:
        """
        استخراج متن اصلی خبر از RSS.
        """

        content = getattr(entry, "content", None)

        if content:
            try:
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            value = item.get("value", "")
                            if value:
                                return value
            except Exception:
                pass

        return (
            getattr(entry, "summary", "")
            or ""
        )

    @staticmethod
    def _extract_published_at(
        entry,
    ) -> Optional[datetime]:
        """
        تبدیل تاریخ RSS به datetime.
        """

        parsed_time = getattr(
            entry,
            "published_parsed",
            None,
        )

        if not parsed_time:
            parsed_time = getattr(
                entry,
                "updated_parsed",
                None,
            )

        if parsed_time:
            try:
                return datetime(
                    parsed_time.tm_year,
                    parsed_time.tm_mon,
                    parsed_time.tm_mday,
                    parsed_time.tm_hour,
                    parsed_time.tm_min,
                    parsed_time.tm_sec,
                )
            except (ValueError, TypeError, AttributeError):
                pass

        return None

    @staticmethod
    def _extract_image_url(entry) -> Optional[str]:
        """
        استخراج تصویر از media:thumbnail،
        media:content یا enclosure.
        """

        media_thumbnail = getattr(
            entry,
            "media_thumbnail",
            None,
        )

        if media_thumbnail:
            url = media_thumbnail[0].get("url")
            if url:
                return url

        media_content = getattr(
            entry,
            "media_content",
            None,
        )

        if media_content:
            url = media_content[0].get("url")
            if url:
                return url

        for link in getattr(entry, "links", []) or []:
            if (
                link.get("rel") == "enclosure"
                and str(link.get("type", "")).startswith("image")
            ):
                url = link.get("href")
                if url:
                    return url

        return None

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
