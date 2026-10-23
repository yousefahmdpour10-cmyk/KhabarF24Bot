"""
Social Fetcher

دریافت خبر از منابع اجتماعی عمومی.

فعلاً:
- Telegram Public Channels

ساختار برای افزودن شبکه‌های اجتماعی دیگر در آینده آماده است.
"""

import re
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, urlparse

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

        self.timeout = aiohttp.ClientTimeout(
            total=20,
            connect=5,
            sock_read=15,
        )

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

        source_type = str(
            getattr(self.source, "source_type", "") or ""
        ).lower().strip()

        if source_type != "social":
            logger.warning(
                "SocialFetcher received invalid source type: %s",
                self.source.name,
            )
            return []

        platform = str(
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

        if not html:
            logger.warning(
                "TELEGRAM_FETCH_EMPTY | source=%s | url=%s",
                self.source.name,
                channel_url,
            )
            return []

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
            seen_urls = set()

            # HTML کانال عمومی معمولاً جدیدترین پست‌ها را دارد.
            for message in messages[-self.MAX_POSTS:]:
                try:
                    news = self._parse_telegram_post(message)

                    if not news:
                        continue

                    if news.url and news.url in seen_urls:
                        continue

                    if news.url:
                        seen_urls.add(news.url)

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

        candidates = (
            getattr(self.source, "social_url", None),
            getattr(self.source, "website_url", None),
            getattr(self.source, "url", None),
        )

        url = next(
            (
                str(value).strip()
                for value in candidates
                if value and str(value).strip()
            ),
            "",
        )

        if not url:
            return None

        if not url.startswith(("http://", "https://")):
            username = url.lstrip("@").strip("/")

            if not username or "/" in username:
                return None

            return f"https://t.me/s/{username}"

        parsed = urlparse(url)

        if parsed.netloc.lower() not in ("t.me", "www.t.me"):
            return url

        parts = parsed.path.strip("/").split("/")

        if not parts or not parts[0]:
            return None

        if parts[0] == "s":
            if len(parts) < 2:
                return None
            username = parts[1]
        else:
            username = parts[0]

        # لینک‌های خصوصی یا شناسه‌های داخلی را تغییر نده.
        if username.startswith("+") or username == "c":
            return url

        return f"https://t.me/s/{username}"

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

        post_link_element = message.select_one(
            ".tgme_widget_message_date"
        )

        post_link = (
            post_link_element.get("href", "")
            if post_link_element
            else ""
        )

        if post_link:
            post_link = urljoin("https://t.me/", post_link)

        published_at = self._extract_datetime(message)
        image_url = self._extract_image(message)
        video_url = self._extract_video(message)

        related_urls = []

        if text_element:
            for link in text_element.select("a[href]"):
                href = link.get("href")

                if not href:
                    continue

                absolute_url = urljoin("https://t.me/", href)

                if absolute_url not in related_urls:
                    related_urls.append(absolute_url)

        # اگر پست متن، عکس و ویدئو ندارد، خبر قابل استفاده‌ای نیست.
        if not content.strip() and not image_url and not video_url:
            return None

        # پست رسانه‌ای بدون متن نیز حفظ می‌شود.
        title = self._build_title(content)

        if not title:
            if video_url:
                title = "ویدئوی جدید از " + self.source.name
            elif image_url:
                title = "تصویر جدید از " + self.source.name
            else:
                return None

        categories = (
            getattr(self.source, "categories", None) or []
        )

        category = (
            categories[0]
            if categories
            else "sport"
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
            category=category,
            related_urls=related_urls,
            raw_data={
                "platform": "telegram",
                "channel": self.source.name,
                "channel_url": self._get_telegram_url(),
                "video_url": video_url or "",
                "has_video": bool(video_url),
                "has_image": bool(image_url),
            },
        )

        logger.info(
            "TELEGRAM_MEDIA_PARSED | source=%s | "
            "image=%s | video=%s | text_length=%d",
            self.source.name,
            bool(image_url),
            bool(video_url),
            len(content),
        )

        return news

    # ==================================================
    # Image
    # ==================================================

    @staticmethod
    def _extract_image(message) -> Optional[str]:
        """استخراج تصویر یا تصویر پیش‌نمایش از پست تلگرام."""

        photo = message.select_one(
            ".tgme_widget_message_photo_wrap"
        )

        if photo:
            style = photo.get("style", "")

            match = re.search(
                r"""background-image\s*:\s*url\(\s*(['"]?)(.*?)\1\s*\)""",
                style,
                re.IGNORECASE,
            )

            if match:
                value = match.group(2).strip()

                if value.startswith(("http://", "https://")):
                    return value

        # بعضی قالب‌ها تصویر را در img قرار می‌دهند.
        image = message.select_one(
            ".tgme_widget_message_video img, "
            ".tgme_widget_message_photo img, "
            ".tgme_widget_message img"
        )

        if image:
            for attribute in (
                "src",
                "data-src",
                "data-original",
            ):
                value = image.get(attribute)

                if value and value.startswith(
                    ("http://", "https://")
                ):
                    return value

        return None

    # ==================================================
    # Video
    # ==================================================

    @staticmethod
    def _extract_video(message) -> Optional[str]:
        """
        استخراج URL مستقیم ویدئو، اگر در HTML عمومی موجود باشد.

        صفحه عمومی تلگرام ممکن است فایل ویدئو را نمایش ندهد.
        """

        video = message.select_one(
            ".tgme_widget_message_video video, "
            ".tgme_widget_message_video source, "
            ".tgme_widget_message video, "
            ".tgme_widget_message source"
        )

        if not video:
            return None

        for attribute in ("src", "data-src"):
            value = video.get(attribute)

            if value and value.startswith(
                ("http://", "https://")
            ):
                return value

        parent = video.find_parent("video")

        if parent:
            value = parent.get("src")

            if value and value.startswith(
                ("http://", "https://")
            ):
                return value

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

        if not content:
            return ""

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
