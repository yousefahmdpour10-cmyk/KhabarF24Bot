"""
Social Fetcher

دریافت خبر از منابع اجتماعی عمومی.

فعلاً:
- Telegram Public Channels

ویژگی‌ها:
- استخراج متن پست
- استخراج تصویر واقعی خود پست
- جلوگیری از انتخاب avatar کانال به‌عنوان تصویر خبر
- استخراج ویدئو در صورت وجود URL قابل‌دسترسی در HTML عمومی
- ثبت مستقیم video_url در RawNews
- نگهداری اطلاعات رسانه در raw_data
- ساختار آماده برای افزودن شبکه‌های اجتماعی دیگر
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

    # ==================================================
    # Main
    # ==================================================

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

            # HTML عمومی کانال معمولاً جدیدترین پست‌ها را دارد.
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
                        "Content-Type",
                        "",
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
            post_link = urljoin(
                "https://t.me/",
                post_link,
            )

        published_at = self._extract_datetime(message)

        image_url = self._extract_image(message)
        video_url = self._extract_video(message)

        video_content_type = self._extract_video_content_type(
            message
        )

        related_urls = []

        if text_element:
            for link in text_element.select("a[href]"):
                href = link.get("href")

                if not href:
                    continue

                absolute_url = urljoin(
                    "https://t.me/",
                    href,
                )

                if absolute_url not in related_urls:
                    related_urls.append(absolute_url)

        # اگر پست متن، عکس و ویدئو ندارد، خبر قابل استفاده‌ای نیست.
        if (
            not content.strip()
            and not image_url
            and not video_url
        ):
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

        # --------------------------------------------------
        # RawNews
        # --------------------------------------------------
        #
        # مهم:
        # video_url مستقیماً داخل مدل RawNews قرار می‌گیرد
        # تا Publisher مجبور نباشد فقط به raw_data وابسته باشد.
        #
        news = RawNews(
            source_id=self.source.id,
            source=self.source.name,
            title=title,
            content=content,
            summary=content,
            url=post_link,
            image_url=image_url or "",

            # رسانه
            video_url=video_url or "",
            video_content_type=video_content_type or "",

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
                "video_content_type": video_content_type or "",
                "has_video": bool(video_url),

                "image_url": image_url or "",
                "has_image": bool(image_url),

                "post_url": post_link or "",
            },
        )

        logger.info(
            "TELEGRAM_MEDIA_PARSED | source=%s | "
            "image=%s | video=%s | video_type=%s | text_length=%d",
            self.source.name,
            bool(image_url),
            bool(video_url),
            video_content_type or "-",
            len(content),
        )

        return news

    # ==================================================
    # Image
    # ==================================================

    @staticmethod
    def _extract_image(message) -> Optional[str]:
        """
        استخراج تصویر واقعی خود پست تلگرام.

        اولویت:
        1. تصویر اصلی داخل photo_wrap
        2. تصویر داخل photo container
        3. تصویر داخل media container

        عمداً از selector عمومی
        '.tgme_widget_message img'
        استفاده نمی‌شود؛ چون ممکن است avatar کانال
        به‌عنوان تصویر خبر انتخاب شود.
        """

        # --------------------------------------------------
        # 1) تصویر اصلی پست
        # --------------------------------------------------

        photo = message.select_one(
            ".tgme_widget_message_photo_wrap"
        )

        if photo:
            # Telegram معمولاً URL تصویر را داخل style
            # به‌صورت background-image قرار می‌دهد.
            style = photo.get("style", "")

            match = re.search(
                r"""background-image\s*:\s*url\(\s*(['"]?)(.*?)\1\s*\)""",
                style,
                re.IGNORECASE,
            )

            if match:
                value = match.group(2).strip()

                value = SocialFetcher._clean_media_url(
                    value
                )

                if value:
                    return value

            # بعضی نسخه‌های HTML ممکن است تصویر را
            # به‌صورت data attribute نگه دارند.
            for attribute in (
                "data-src",
                "data-original",
                "src",
            ):
                value = photo.get(attribute)

                value = SocialFetcher._clean_media_url(
                    value
                )

                if value:
                    return value

            # اگر خود photo_wrap شامل img باشد،
            # فقط همان container رسانه‌ای را بررسی می‌کنیم.
            image = photo.select_one("img")

            if image:
                for attribute in (
                    "src",
                    "data-src",
                    "data-original",
                ):
                    value = image.get(attribute)

                    value = SocialFetcher._clean_media_url(
                        value
                    )

                    if value:
                        return value

        # --------------------------------------------------
        # 2) photo containerهای جایگزین
        # --------------------------------------------------

        photo_image = message.select_one(
            ".tgme_widget_message_photo img"
        )

        if photo_image:
            for attribute in (
                "src",
                "data-src",
                "data-original",
            ):
                value = photo_image.get(attribute)

                value = SocialFetcher._clean_media_url(
                    value
                )

                if value:
                    return value

        # --------------------------------------------------
        # 3) media container
        # --------------------------------------------------

        media_image = message.select_one(
            ".tgme_widget_message_media img"
        )

        if media_image:
            for attribute in (
                "src",
                "data-src",
                "data-original",
            ):
                value = media_image.get(attribute)

                value = SocialFetcher._clean_media_url(
                    value
                )

                if value:
                    return value

        # --------------------------------------------------
        # 4) fallback بسیار محدود
        # --------------------------------------------------
        #
        # فقط زمانی که عنصر دارای class مربوط به media
        # باشد. هیچ‌وقت کل message را برای img جستجو نمی‌کنیم.
        #
        for selector in (
            '[class*="photo"] img',
            '[class*="media"] img',
        ):
            image = message.select_one(selector)

            if not image:
                continue

            for attribute in (
                "src",
                "data-src",
                "data-original",
            ):
                value = image.get(attribute)

                value = SocialFetcher._clean_media_url(
                    value
                )

                if value:
                    return value

        return None

    # ==================================================
    # Video
    # ==================================================

    @staticmethod
    def _extract_video(message) -> Optional[str]:
        """
        استخراج URL ویدئوی واقعی پست.

        Telegram public widget ممکن است ویدئو را در چند
        ساختار مختلف HTML نمایش دهد.

        اولویت:
        1. video[src]
        2. source[src]
        3. data-src
        4. data-video
        5. لینک مستقیم فایل داخل media container

        اگر URL مستقیم فایل در HTML عمومی موجود نباشد،
        این تابع None برمی‌گرداند؛ چون نباید URL جعلی
        یا URL صفحه پست را به عنوان video_url ثبت کنیم.
        """

        selectors = (
            ".tgme_widget_message_video video",
            ".tgme_widget_message_video source",
            ".tgme_widget_message_media video",
            ".tgme_widget_message_media source",
            ".tgme_widget_message video",
            ".tgme_widget_message source",
        )

        for selector in selectors:
            element = message.select_one(selector)

            if not element:
                continue

            for attribute in (
                "src",
                "data-src",
                "data-video",
            ):
                value = element.get(attribute)

                value = SocialFetcher._clean_media_url(
                    value
                )

                if value:
                    return value

        # بعضی ساختارها URL را روی parent نگه می‌دارند.
        video = message.select_one(
            ".tgme_widget_message_video"
        )

        if video:
            for attribute in (
                "data-src",
                "data-video",
                "src",
            ):
                value = video.get(attribute)

                value = SocialFetcher._clean_media_url(
                    value
                )

                if value:
                    return value

        # بررسی لینک‌های داخل media container.
        media_container = message.select_one(
            ".tgme_widget_message_media"
        )

        if media_container:
            for link in media_container.select(
                "a[href]"
            ):
                href = link.get("href")

                href = SocialFetcher._clean_media_url(
                    href
                )

                if not href:
                    continue

                lower = href.lower()

                # فقط URLهایی که شبیه فایل ویدئو هستند.
                if any(
                    extension in lower
                    for extension in (
                        ".mp4",
                        ".webm",
                        ".mov",
                        ".m4v",
                        ".mkv",
                    )
                ):
                    return href

        return None

    # ==================================================
    # Video Content Type
    # ==================================================

    @staticmethod
    def _extract_video_content_type(
        message,
    ) -> str:
        """استخراج MIME type ویدئو در صورت وجود."""

        selectors = (
            ".tgme_widget_message_video video",
            ".tgme_widget_message_video source",
            ".tgme_widget_message_media video",
            ".tgme_widget_message_media source",
        )

        for selector in selectors:
            element = message.select_one(selector)

            if not element:
                continue

            for attribute in (
                "type",
                "data-type",
            ):
                value = element.get(attribute)

                if value:
                    value = str(value).strip()

                    if value:
                        return value

        return ""

    # ==================================================
    # Media URL Cleanup
    # ==================================================

    @staticmethod
    def _clean_media_url(value) -> Optional[str]:
        """
        پاک‌سازی URL رسانه.

        URLهای نسبی به HTTPS تبدیل می‌شوند.
        URLهای data/blob یا URLهای خالی حذف می‌شوند.
        """

        if not value:
            return None

        value = str(value).strip()

        if not value:
            return None

        # حذف quotationهای اضافه
        value = value.strip("\"'")

        if not value:
            return None

        # URLهایی که برای دانلود مستقیم قابل استفاده نیستند.
        if value.startswith(
            (
                "data:",
                "blob:",
                "javascript:",
            )
        ):
            return None

        if value.startswith("//"):
            value = "https:" + value

        elif value.startswith("/"):
            value = urljoin(
                "https://t.me/",
                value,
            )

        if not value.startswith(
            (
                "http://",
                "https://",
            )
        ):
            return None

        return value

    # ==================================================
    # Date
    # ==================================================

    @staticmethod
    def _extract_datetime(
        message,
    ) -> Optional[datetime]:
        """استخراج زمان انتشار پست."""

        time_element = message.select_one("time")

        if not time_element:
            return None

        datetime_value = time_element.get("datetime")

        if not datetime_value:
            return None

        try:
            return datetime.fromisoformat(
                datetime_value.replace(
                    "Z",
                    "+00:00",
                )
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
