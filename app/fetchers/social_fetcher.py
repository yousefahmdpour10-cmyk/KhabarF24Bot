
"""
Social Fetcher

دریافت خبر از منابع اجتماعی عمومی

فعلاً:
- Telegram Public Channels

ساختار طوری نوشته شده که در آینده بتوانیم:
- X
- سایر شبکه‌های اجتماعی
را بدون تغییر معماری اصلی اضافه کنیم.
"""

from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.logger import logger


class SocialFetcher(BaseFetcher):
    """دریافت خبر از منابع اجتماعی عمومی."""

    MAX_POSTS = 20

    def __init__(self, source):
        super().__init__(source)

        self.timeout = aiohttp.ClientTimeout(total=20)

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/153.0 Mobile Safari/537.36"
            )
        }

    async def fetch(self) -> List[RawNews]:
        """دریافت پست‌های منبع اجتماعی."""

        source_type = (
            getattr(self.source, "source_type", "") or ""
        ).lower().strip()

        if source_type != "social":
            logger.warning(
                "SocialFetcher received invalid source type: %s",
                self.source.name,
            )
            return []

        platform = (
            getattr(self.source, "social_platform", "") or ""
        ).lower().strip()

        if platform == "telegram":
            return await self._fetch_telegram()

        logger.warning(
            "Unsupported social platform for %s: %s",
            self.source.name,
            platform,
        )
        return []

    # ==================================================
    # Telegram
    # ==================================================

    async def _fetch_telegram(self) -> List[RawNews]:
        """دریافت پست‌های یک کانال عمومی تلگرام."""

        channel_url = self._get_telegram_url()

        if not channel_url:
            logger.warning(
                "Telegram URL is missing: %s",
                self.source.name,
            )
            return []

        logger.info(
            "Fetching Telegram: %s | url=%s",
            self.source.name,
            channel_url,
        )

        html = await self._download(channel_url)

        # تغییر تشخیصی: ثبت دقیق شکست دریافت صفحه
        if not html:
            logger.warning(
                "TELEGRAM_FETCH_EMPTY | source=%s | url=%s",
                self.source.name,
                channel_url,
            )
            return []

        # تغییر تشخیصی: تأیید دریافت HTML
        logger.info(
            "TELEGRAM_HTML_RECEIVED | source=%s | html_length=%d",
            self.source.name,
            len(html),
        )

        try:
            soup = BeautifulSoup(html, "lxml")

            messages = soup.select(
                ".tgme_widget_message_wrap"
            )

            # تغییر تشخیصی: بررسی ساختار صفحه تلگرام
            if not messages:
                page_title = (
                    soup.title.get_text(" ", strip=True)
                    if soup.title
                    else "NO_TITLE"
                )

                logger.warning(
                    "TELEGRAM_NO_POSTS | source=%s | url=%s | "
                    "html_length=%d | page_title=%s",
                    self.source.name,
                    channel_url,
                    len(html),
                    page_title,
                )
                return []

            news_list: List[RawNews] = []

            # از جدیدترین پست‌های موجود در HTML شروع می‌کنیم.
            for message in messages[-self.MAX_POSTS:]:
                try:
                    news = self._parse_telegram_post(message)

                    if news:
                        news_list.append(news)

                except Exception as error:
                    logger.exception(
                        "Telegram post parse error | source=%s | error=%s",
                        self.source.name,
                        error,
                    )

            logger.info(
                "TELEGRAM_POSTS_PARSED | source=%s | "
                "html_posts=%d | parsed_posts=%d",
                self.source.name,
                len(messages),
                len(news_list),
            )

            return news_list

        except Exception as error:
            logger.exception(
                "Telegram parsing error | source=%s | error=%s",
                self.source.name,
                error,
            )
            return []

    # ==================================================
    # Telegram URL
    # ==================================================

    def _get_telegram_url(self) -> Optional[str]:
        """ساخت URL عمومی تلگرام از تنظیمات منبع."""

        social_url = (
            getattr(self.source, "social_url", None) or ""
        ).strip()

        website_url = (
            getattr(self.source, "website_url", None) or ""
        ).strip()

        source_url = (
            getattr(self.source, "url", None) or ""
        ).strip()

        url = social_url or website_url or source_url

        if not url:
            return None

        if not url.startswith(("http://", "https://")):
            username = url.lstrip("@").strip("/")

            if username:
                return f"https://t.me/s/{username}"

            return None

        if "t.me/" in url:
            username = url.rstrip("/").split("t.me/", 1)[-1]

            if username.startswith("s/"):
                return "https://t.me/" + username

            username = username.split("/", 1)[0]

            if username:
                return f"https://t.me/s/{username}"

        return url

    # ==================================================
    # Download
    # ==================================================

    async def _download(self, url: str) -> Optional[str]:
        """دانلود HTML صفحه."""

        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers,
            ) as session:
                async with session.get(
                    url,
                    allow_redirects=True,
                ) as response:
                    if response.status != 200:
                        logger.warning(
                            "Social request failed | source=%s | "
                            "status=%d | url=%s",
                            self.source.name,
                            response.status,
                            url,
                        )
                        return None

                    content_type = response.headers.get(
                        "Content-Type", ""
                    ).lower()

                    if (
                        "text/html" not in content_type
                        and "application/xhtml" not in content_type
                    ):
                        logger.warning(
                            "Social response is not HTML | source=%s | "
                            "content_type=%s",
                            self.source.name,
                            content_type,
                        )
                        return None

                    return await response.text(
                        encoding="utf-8",
                        errors="ignore",
                    )

        except (aiohttp.ClientError, TimeoutError) as error:
            logger.warning(
                "Social download error | source=%s | url=%s | error=%s",
                self.source.name,
                url,
                error,
            )
            return None

        except Exception as error:
            logger.exception(
                "Unexpected social download error | source=%s | error=%s",
                self.source.name,
                error,
            )
            return None

    # ==================================================
    # Parse Telegram Post
    # ==================================================

    def _parse_telegram_post(self, message) -> Optional[RawNews]:
        """تبدیل یک پست تلگرام به RawNews."""

        text_element = message.select_one(
            ".tgme_widget_message_text"
        )

        content = (
            text_element.get_text("\n", strip=True)
            if text_element
            else ""
        )

        # فعلاً پست‌های بدون متن رد می‌شوند.
        if not content:
            return None

        post_link_element = message.select_one(
            ".tgme_widget_message_date"
        )

        post_link = (
            post_link_element.get("href", "")
            if post_link_element
            else ""
        )

        published_at = self._extract_datetime(message)
        image_url = self._extract_image(message)

        related_urls = []

        for link in message.select(
            ".tgme_widget_message_text a"
        ):
            href = link.get("href")

            if href:
                related_urls.append(
                    urljoin("https://t.me/", href)
                )

        title = self._build_title(content)

        categories = (
            getattr(self.source, "categories", None) or []
        )

        news = RawNews(
            source_id=self.source.id,
            source=self.source.name,
            title=title,
            content=content,
            summary=content,
            url=post_link,
            image_url=image_url or "",
            published_at=published_at,
            language=getattr(self.source, "language", ""),
            country=getattr(self.source, "country", ""),
            category=categories[0] if categories else "sport",
            related_urls=related_urls,
            raw_data={
                "platform": "telegram",
                "channel": self.source.name,
                "channel_url": self._get_telegram_url(),
            },
        )

        return news

    # ==================================================
    # Image
    # ==================================================

    @staticmethod
    def _extract_image(message) -> Optional[str]:
        """استخراج تصویر پست تلگرام."""

        photo = message.select_one(
            ".tgme_widget_message_photo_wrap"
        )

        if not photo:
            return None

        style = photo.get("style", "")

        if "background-image" not in style:
            return None

        for quote in ('"', "'"):
            marker = f"url({quote}"
            start = style.find(marker)

            if start != -1:
                start += len(marker)
                end = style.find(quote, start)

                if end != -1:
                    return style[start:end]

        return None

    # ==================================================
    # Date
    # ==================================================

    @staticmethod
    def _extract_datetime(message) -> Optional[datetime]:
        """استخراج زمان انتشار پست."""

        time_element = message.select_one("time")

        if not time_element:
            return None

        datetime_value = time_element.get("datetime")

        if not datetime_value:
            return None

        try:
            return datetime.fromisoformat(
                datetime_value.replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            return None

    # ==================================================
    # Title
    # ==================================================

    @staticmethod
    def _build_title(content: str) -> str:
        """ساخت عنوان اولیه از متن پست."""

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        if not lines:
            return ""

        title = lines[0]

        if len(title) > 180:
            title = title[:177] + "..."

        return title
