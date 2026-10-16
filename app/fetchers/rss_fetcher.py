"""
RSS Fetcher
دریافت اخبار از RSS و تلاش برای استخراج تصویر و ویدئو از صفحه خبر.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import feedparser
from bs4 import BeautifulSoup

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.http_client import HTTPClient


logger = logging.getLogger(__name__)

# برای جلوگیری از درخواست بیش از حد به سایت‌های خبری
MAX_ARTICLE_PAGES_PER_FETCH = 12
MAX_CONCURRENT_PAGE_REQUESTS = 4

VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
    ".m3u8",
    ".mpd",
)

VIDEO_MIME_TYPES = (
    "video/mp4",
    "video/webm",
    "video/quicktime",
    "application/vnd.apple.mpegurl",
    "application/x-mpegurl",
    "application/dash+xml",
)

VIDEO_URL_PATTERN = re.compile(
    r"""https?://[^\s"'<>\\]+?\.(?:mp4|webm|mov|m4v|m3u8|mpd)
    (?:\?[^\s"'<>\\]*)?""",
    re.IGNORECASE | re.VERBOSE,
)


class RSSFetcher(BaseFetcher):
    """دریافت خبر از RSS و استخراج رسانه از صفحه خبر."""

    def __init__(self, source):
        super().__init__(source)
        self.http = HTTPClient(timeout=20, retries=2)

    async def fetch(self) -> List[RawNews]:
        news_list: List[RawNews] = []

        rss_url = (
            getattr(self.source, "rss_url", None)
            or getattr(self.source, "url", None)
        )

        if not rss_url:
            logger.warning("RSS URL MISSING: %s", self.source.name)
            return news_list

        try:
            xml = await self.http.get(rss_url)
        except Exception:
            logger.exception("RSS FETCH ERROR: %s", self.source.name)
            return news_list

        if not xml:
            logger.warning(
                "RSS FETCH FAILED: %s | url=%s",
                self.source.name,
                rss_url,
            )
            return news_list

        try:
            feed = feedparser.parse(xml)
        except Exception:
            logger.exception("RSS PARSE ERROR: %s", self.source.name)
            return news_list

        if getattr(feed, "bozo", False):
            logger.warning(
                "RSS PARSE WARNING: %s | %s",
                self.source.name,
                getattr(feed, "bozo_exception", "unknown error"),
            )

        source_categories = list(
            getattr(self.source, "categories", None) or []
        )

        logger.info(
            "RSS RESULT: %s | entries=%s",
            self.source.name,
            len(feed.entries),
        )

        entries_to_check = []

        for entry in feed.entries:
            try:
                video_url, video_type = self._extract_video(entry)
                image_url = self._extract_image_url(entry)

                news = RawNews(
                    source_id=self.source.id,
                    source=self.source.name,
                    source_category_hint=source_categories,
                    title=getattr(entry, "title", "") or "",
                    content=self._extract_content(entry),
                    summary=getattr(entry, "summary", "") or "",
                    url=getattr(entry, "link", "") or "",
                    published_at=self._extract_published_at(entry),
                    language=getattr(self.source, "language", "") or "",
                    category=(
                        source_categories[0]
                        if source_categories
                        else ""
                    ),
                    image_url=image_url or "",
                    video_url=video_url or "",
                    video_content_type=video_type or "",
                    raw_data=dict(entry),
                    tags=list(getattr(entry, "tags", []) or []),
                )

                if not news.title and not news.content and not news.url:
                    continue

                news_list.append(news)

                # صفحه خبر فقط وقتی بررسی می‌شود که RSS ویدئو نداده باشد.
                if news.url and not news.video_url:
                    entries_to_check.append(news)

            except Exception:
                logger.exception(
                    "RSS ENTRY ERROR: %s",
                    self.source.name,
                )

        # بررسی محدود و هم‌زمان صفحات خبر
        pages = entries_to_check[:MAX_ARTICLE_PAGES_PER_FETCH]

        if pages:
            semaphore = asyncio.Semaphore(
                MAX_CONCURRENT_PAGE_REQUESTS
            )

            await asyncio.gather(
                *[
                    self._enrich_from_article(news, semaphore)
                    for news in pages
                ],
                return_exceptions=True,
            )

        for news in news_list:
            logger.info(
                "MEDIA CHECK: %s | image=%s | video=%s | title=%s",
                news.source,
                bool(news.image_url),
                bool(news.video_url),
                news.title[:60],
            )

        logger.info(
            "RSS PARSED: %s | news=%s | article_pages_checked=%s",
            self.source.name,
            len(news_list),
            len(pages),
        )

        return news_list

    async def _enrich_from_article(
        self,
        news: RawNews,
        semaphore: asyncio.Semaphore,
    ) -> None:
        """استخراج ویدئو و تصویر احتمالی از صفحه اصلی خبر."""

        async with semaphore:
            try:
                html = await self.http.get(news.url)

                if not html:
                    logger.debug(
                        "ARTICLE PAGE UNAVAILABLE: %s",
                        news.url,
                    )
                    return

                video_url, video_type, image_url = (
                    self._extract_page_media(html, news.url)
                )

                if video_url and not news.video_url:
                    news.video_url = video_url
                    news.video_content_type = video_type or ""

                    logger.info(
                        "ARTICLE VIDEO FOUND: %s | %s",
                        self.source.name,
                        video_url[:180],
                    )

                if image_url and not news.image_url:
                    news.image_url = image_url

                if not video_url:
                    logger.debug(
                        "ARTICLE VIDEO NOT FOUND: %s",
                        news.url,
                    )

            except Exception:
                logger.exception(
                    "ARTICLE MEDIA ERROR: %s",
                    news.url,
                )

    @staticmethod
    def _extract_content(entry) -> str:
        content = getattr(entry, "content", None)

        if content:
            for item in content:
                if isinstance(item, dict):
                    value = item.get("value", "")
                    if value:
                        return value

        return getattr(entry, "summary", "") or ""

    @staticmethod
    def _extract_published_at(
        entry,
    ) -> Optional[datetime]:
        parsed_time = getattr(entry, "published_parsed", None)

        if not parsed_time:
            parsed_time = getattr(entry, "updated_parsed", None)

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
    def _is_video_url(url: str, media_type: str = "") -> bool:
        if not url:
            return False

        media_type = (media_type or "").lower().split(";")[0].strip()

        if media_type in VIDEO_MIME_TYPES:
            return True

        path = urlparse(url).path.lower()

        if path.endswith(VIDEO_EXTENSIONS):
            return True

        return False

    @classmethod
    def _extract_image_url(cls, entry) -> Optional[str]:
        for field in ("media_thumbnail", "media_content"):
            items = getattr(entry, field, None) or []

            for item in items:
                if not isinstance(item, dict):
                    continue

                url = item.get("url")
                media_type = str(item.get("type", "")).lower()
                medium = str(item.get("medium", "")).lower()

                if not url:
                    continue

                if cls._is_video_url(url, media_type) or medium == "video":
                    continue

                if (
                    field == "media_thumbnail"
                    or media_type.startswith("image/")
                ):
                    return url

        for link in getattr(entry, "links", []) or []:
            rel = str(link.get("rel", "")).lower()
            media_type = str(link.get("type", "")).lower()
            href = link.get("href")

            if (
                href
                and rel == "enclosure"
                and media_type.startswith("image/")
            ):
                return href

        return None

    @classmethod
    def _extract_video(
        cls,
        entry,
    ) -> Tuple[Optional[str], Optional[str]]:
        candidates = []

        for field in ("media_content",):
            items = getattr(entry, field, None) or []

            for item in items:
                if isinstance(item, dict):
                    candidates.append(item)

        for link in getattr(entry, "links", []) or []:
            candidates.append(link)

        for item in candidates:
            url = item.get("url") or item.get("href")
            media_type = str(item.get("type", "")).lower()
            medium = str(item.get("medium", "")).lower()
            rel = str(item.get("rel", "")).lower()

            if not url:
                continue

            if (
                media_type.startswith("video/")
                or medium == "video"
                or cls._is_video_url(url, media_type)
                or (
                    rel == "enclosure"
                    and media_type in VIDEO_MIME_TYPES
                )
            ):
                return url, media_type or None

        return None, None

    @classmethod
    def _extract_page_media(
        cls,
        html: str,
        page_url: str,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        بررسی HTML، تگ‌های video/source، متادیتا و JSON-LD.
        خروجی: video_url, video_content_type, image_url
        """

        soup = BeautifulSoup(html, "html.parser")

        video_candidates = []
        image_candidates = []

        # تگ‌های استاندارد HTML
        for tag in soup.find_all(["video", "source"]):
            src = tag.get("src")

            if not src:
                continue

            absolute_url = urljoin(page_url, src)
            media_type = str(tag.get("type", "")).lower()

            if (
                tag.name == "video"
                or cls._is_video_url(absolute_url, media_type)
                or media_type.startswith("video/")
            ):
                video_candidates.append(
                    (absolute_url, media_type or None)
                )

        # متادیتای Open Graph و Twitter
        for tag in soup.find_all("meta"):
            key = (
                tag.get("property")
                or tag.get("name")
                or tag.get("itemprop")
                or ""
            ).lower()

            value = tag.get("content", "").strip()

            if not value:
                continue

            absolute_url = urljoin(page_url, value)

            if key in (
                "og:video",
                "og:video:url",
                "og:video:secure_url",
                "twitter:player:stream",
                "contenturl",
                "content_url",
            ):
                if (
                    cls._is_video_url(absolute_url)
                    or key in (
                        "og:video",
                        "og:video:url",
                        "og:video:secure_url",
                        "twitter:player:stream",
                        "contenturl",
                        "content_url",
                    )
                ):
                    # لینک صفحه پلیر را به‌عنوان فایل مستقیم قبول نکن.
                    if cls._is_video_url(absolute_url):
                        video_candidates.append(
                            (absolute_url, None)
                        )

            elif key in (
                "og:image",
                "og:image:url",
                "twitter:image",
                "twitter:image:src",
            ):
                image_candidates.append(absolute_url)

        # JSON-LD، از جمله Schema.org VideoObject
        for script in soup.find_all(
            "script",
            attrs={"type": "application/ld+json"},
        ):
            raw_json = script.string or script.get_text()

            if not raw_json:
                continue

            try:
                data = json.loads(raw_json)
            except (json.JSONDecodeError, TypeError):
                continue

            cls._scan_json_media(
                data,
                page_url,
                video_candidates,
                image_candidates,
            )

        # لینک‌های مستقیم ویدئو که در کد صفحه جاسازی شده‌اند
        if not video_candidates:
            for match in VIDEO_URL_PATTERN.findall(html):
                cleaned = match.rstrip(".,);]")
                video_candidates.append(
                    (urljoin(page_url, cleaned), None)
                )

        # حذف موارد تکراری و لینک‌های غیرمستقیم
        seen = set()

        for url, media_type in video_candidates:
            if not url or url in seen:
                continue

            seen.add(url)

            if cls._is_video_url(url, media_type or ""):
                return url, media_type, (
                    image_candidates[0]
                    if image_candidates
                    else None
                )

        return (
            None,
            None,
            image_candidates[0] if image_candidates else None,
        )

    @classmethod
    def _scan_json_media(
        cls,
        value,
        page_url: str,
        video_candidates: list,
        image_candidates: list,
    ) -> None:
        """جست‌وجوی بازگشتی آدرس رسانه‌ها در JSON."""

        if isinstance(value, dict):
            type_value = value.get("@type", "")
            if isinstance(type_value, list):
                type_value = " ".join(str(x) for x in type_value)

            is_video_object = "videoobject" in str(type_value).lower()

            for key, item in value.items():
                key_lower = str(key).lower()

                if isinstance(item, str):
                    absolute_url = urljoin(page_url, item.strip())

                    if key_lower in (
                        "contenturl",
                        "content_url",
                        "videourl",
                        "video_url",
                        "streamurl",
                        "stream_url",
                    ):
                        if (
                            cls._is_video_url(absolute_url)
                            or is_video_object
                        ):
                            if cls._is_video_url(absolute_url):
                                video_candidates.append(
                                    (absolute_url, None)
                                )

                    elif key_lower in (
                        "thumbnailurl",
                        "thumbnail_url",
                    ):
                        if item.strip():
                            image_candidates.append(absolute_url)

                    elif key_lower == "url" and is_video_object:
                        if cls._is_video_url(absolute_url):
                            video_candidates.append(
                                (absolute_url, None)
                            )

                elif isinstance(item, (dict, list)):
                    cls._scan_json_media(
                        item,
                        page_url,
                        video_candidates,
                        image_candidates,
                    )

        elif isinstance(value, list):
            for item in value:
                cls._scan_json_media(
                    item,
                    page_url,
                    video_candidates,
                    image_candidates,
                )
