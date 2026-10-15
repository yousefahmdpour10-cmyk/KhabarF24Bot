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
    """
    دریافت خبر از منابع اجتماعی عمومی.
    """

    MAX_POSTS = 20

    def __init__(self, source):
        super().__init__(source)

        self.timeout = aiohttp.ClientTimeout(
            total=20
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
        """
        دریافت پست‌های منبع اجتماعی.
        """

        source_type = (
            getattr(self.source, "source_type", "")
            or ""
        ).lower().strip()

        if source_type != "social":
            logger.warning(
                f"SocialFetcher received invalid source type: "
                f"{self.source.name}"
            )
            return []

        platform = (
            getattr(self.source, "social_platform", "")
            or ""
        ).lower().strip()

        # ----------------------------------------------
        # Telegram
        # ----------------------------------------------

        if platform == "telegram":
            return await self._fetch_telegram()

        logger.warning(
            f"Unsupported social platform for "
            f"{self.source.name}: {platform}"
        )

        return []

    # ==================================================
    # Telegram
    # ==================================================

    async def _fetch_telegram(self) -> List[RawNews]:
        """
        دریافت پست‌های یک کانال عمومی Telegram.

        منبع:
        https://t.me/s/<channel>
        """

        channel_url = self._get_telegram_url()

        if not channel_url:
            logger.warning(
                f"Telegram URL is missing: {self.source.name}"
            )
            return []

        logger.info(
            f"Fetching Telegram: {self.source.name}"
        )

        html = await self._download(channel_url)

        if not html:
            return []

        try:
            soup = BeautifulSoup(
                html,
                "lxml",
            )

            messages = soup.select(
                ".tgme_widget_message_wrap"
            )

            if not messages:
                logger.warning(
                    f"No Telegram posts found: "
                    f"{self.source.name}"
                )
                return []

            news_list: List[RawNews] = []

            # از جدیدترین پست‌ها شروع می‌کنیم
            for message in messages[-self.MAX_POSTS:]:
                try:
                    news = self._parse_telegram_post(
                        message
                    )

                    if news:
                        news_list.append(news)

                except Exception as e:
                    logger.error(
                        f"Telegram post parse error "
                        f"({self.source.name}): {e}"
                    )

            logger.info(
                f"Telegram: {self.source.name} -> "
                f"{len(news_list)} posts"
            )

            return news_list

        except Exception as e:
            logger.exception(
                f"Telegram parsing error "
                f"({self.source.name}): {e}"
            )
            return []

    # ==================================================
    # Telegram URL
    # ==================================================

    def _get_telegram_url(self) -> Optional[str]:
        """
        ساخت URL عمومی Telegram.
        """

        social_url = (
            getattr(self.source, "social_url", None)
            or ""
        ).strip()

        website_url = (
            getattr(self.source, "website_url", None)
            or ""
        ).strip()

        source_url = (
            getattr(self.source, "url", None)
            or ""
        ).strip()

        url = (
            social_url
            or website_url
            or source_url
        )

        if not url:
            return None

        # اگر لینک به صورت username داده شده باشد
        if not url.startswith("http"):
            username = url.lstrip("@").strip("/")

            if username:
                return (
                    f"https://t.me/s/{username}"
                )

            return None

        # t.me/channel
        if "t.me/" in url:

            username = url.rstrip("/").split(
                "t.me/",
                1
            )[-1]

            # اگر از قبل /s/ دارد
            if username.startswith("s/"):
                return (
                    "https://t.me/"
                    + username
                )

            username = username.split("/", 1)[0]

            if username:
                return (
                    f"https://t.me/s/{username}"
                )

        return url

    # ==================================================
    # Download
    # ==================================================

    async def _download(
        self,
        url: str,
    ) -> Optional[str]:
        """
        دانلود HTML صفحه.
        """

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
                            f"Social request failed: "
                            f"{response.status} - {url}"
                        )
                        return None

                    return await response.text(
                        encoding="utf-8",
                        errors="ignore",
                    )

        except Exception as e:

            logger.error(
                f"Social download error "
                f"({self.source.name}): {e}"
            )

            return None

    # ==================================================
    # Parse Telegram Post
    # ==================================================

    def _parse_telegram_post(
        self,
        message,
    ) -> Optional[RawNews]:
        """
        تبدیل یک پست Telegram به RawNews.
        """

        text_element = message.select_one(
            ".tgme_widget_message_text"
        )

        if text_element:

            content = text_element.get_text(
                "\n",
                strip=True,
            )

        else:
            content = ""

        # ----------------------------------------------
        # اگر پست هیچ متنی نداشت، فعلاً رد می‌شود.
        # ----------------------------------------------

        if not content:
            return None

        # ----------------------------------------------
        # لینک پست
        # ----------------------------------------------

        post_link = ""

        post_link_element = message.select_one(
            ".tgme_widget_message_date"
        )

        if post_link_element:
            post_link = (
                post_link_element.get("href", "")
                or ""
            )

        # ----------------------------------------------
        # زمان انتشار
        # ----------------------------------------------

        published_at = self._extract_datetime(
            message
        )

        # ----------------------------------------------
        # تصویر
        # ----------------------------------------------

        image_url = self._extract_image(
            message
        )

        # ----------------------------------------------
        # لینک‌های داخل متن
        # ----------------------------------------------

        related_urls = []

        for link in message.select(
            ".tgme_widget_message_text a"
        ):

            href = link.get("href")

            if href:
                related_urls.append(
                    urljoin(
                        "https://t.me/",
                        href,
                    )
                )

        # ----------------------------------------------
        # عنوان
        # ----------------------------------------------

        title = self._build_title(
            content
        )

        # ----------------------------------------------
        # RawNews
        # ----------------------------------------------

        news = RawNews(
            source_id=self.source.id,
            source=self.source.name,
            title=title,
            content=content,
            summary=content,
            url=post_link,
            image_url=image_url or "",
            published_at=published_at,
            language=self.source.language,
            country=self.source.country,
            category=(
                self.source.categories[0]
                if getattr(
                    self.source,
                    "categories",
                    None,
                )
                else "sport"
            ),
            related_urls=related_urls,
            raw_data={
                "platform": "telegram",
                "channel": self.source.name,
                "channel_url": (
                    self._get_telegram_url()
                ),
            },
        )

        return news

    # ==================================================
    # Image
    # ==================================================

    @staticmethod
    def _extract_image(
        message,
    ) -> Optional[str]:
        """
        استخراج تصویر پست Telegram.
        """

        photo = message.select_one(
            ".tgme_widget_message_photo_wrap"
        )

        if not photo:
            return None

        style = photo.get(
            "style",
            "",
        )

        # Telegram معمولاً تصویر را در
        # background-image قرار می‌دهد.
        if "background-image" in style:

            start = style.find(
                'url("'
            )

            if start != -1:

                start += 5

                end = style.find(
                    '"',
                    start,
                )

                if end != -1:
                    return style[
                        start:end
                    ]

            start = style.find(
                "url('"
            )

            if start != -1:

                start += 5

                end = style.find(
                    "'",
                    start,
                )

                if end != -1:
                    return style[
                        start:end
                    ]

        return None

    # ==================================================
    # Date
    # ==================================================

    @staticmethod
    def _extract_datetime(
        message,
    ) -> Optional[datetime]:
        """
        استخراج تاریخ پست.
        """

        time_element = message.select_one(
            "time"
        )

        if not time_element:
            return None

        datetime_value = time_element.get(
            "datetime"
        )

        if not datetime_value:
            return None

        try:
            return datetime.fromisoformat(
                datetime_value.replace(
                    "Z",
                    "+00:00",
                )
            )

        except Exception:
            return None

    # ==================================================
    # Title
    # ==================================================

    @staticmethod
    def _build_title(
        content: str,
    ) -> str:
        """
        ساخت عنوان اولیه از متن پست.

        عنوان نهایی بعداً توسط ContentGenerator
        ساخته خواهد شد.
        """

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        if not lines:
            return ""

        title = lines[0]

        # جلوگیری از عنوان بیش از حد طولانی
        if len(title) > 180:
            title = title[:177] + "..."

        return title
