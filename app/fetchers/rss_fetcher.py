"""
RSS Fetcher

دریافت خبر از منابع RSS، به‌همراه پیدا کردن عکس و ویدئوی هر خبر
(اول از خود RSS، و اگر نبود از صفحه‌ی خبر).
"""

import asyncio
import json
import logging
import re

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlparse,
    urlsplit,
    urlunsplit,
)

import feedparser
from bs4 import BeautifulSoup

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.http_client import HTTPClient


logger = logging.getLogger(__name__)

MAX_ARTICLE_PAGES_PER_FETCH = 30
MAX_CONCURRENT_PAGE_REQUESTS = 5
MAX_HTML_CHARS = 1_500_000

# نتیجه‌ی بررسی صفحه‌ی هر خبر را نگه می‌داریم تا همان خبر در چرخه‌های بعد
# (که RSS هنوز آن را دارد) دوباره دانلود و تحلیل نشود.
MAX_CACHED_ARTICLES = 5000
_ARTICLE_MEDIA_CACHE: Dict[str, Tuple[str, str, str, str]] = {}

VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
    ".m3u8",
    ".mpd",
)

# این دو قالب «پلی‌لیست» هستند، نه فایل ویدئو؛ مستقیم دانلود نمی‌شوند.
STREAM_EXTENSIONS = (".m3u8", ".mpd")

VIDEO_MIME_TYPES = (
    "video/",
    "application/vnd.apple.mpegurl",
    "application/x-mpegurl",
    "application/dash+xml",
)

VIDEO_KEYS = {
    "contenturl",
    "content_url",
    "videourl",
    "video_url",
    "video",
    "video_src",
    "videosrc",
    "playbackurl",
    "playback_url",
    "streamurl",
    "stream_url",
    "mediacontent",
    "media_content_url",
    "mediaurl",
    "media_url",
    "fileurl",
    "file_url",
    "downloadurl",
    "download_url",
}

IMAGE_KEYS = {
    "thumbnailurl",
    "thumbnail_url",
    "image",
    "imageurl",
    "image_url",
    "thumbnail",
    "poster",
    "posterurl",
    "poster_url",
}

VIDEO_URL_RE = re.compile(
    r"""https?://[^\s"'<>\\]+""",
    re.IGNORECASE,
)

BBC_HOSTS = (
    "bbc.com",
    "bbc.co.uk",
    "bbci.co.uk",
    "bbc.in",
)

PLAYER_PATH_MARKERS = (
    "/av/embed/",
    "/iplayer/",
    "/video/",
    "/player/",
    "/embed/",
)

EMBED_HOSTS = (
    "youtube.com",
    "youtu.be",
    "player.vimeo.com",
)


def _make_soup(markup: str) -> BeautifulSoup:
    """lxml چند برابر سریع‌تر است؛ اگر نبود به html.parser برمی‌گردیم."""
    try:
        return BeautifulSoup(markup, "lxml")
    except Exception:
        return BeautifulSoup(markup, "html.parser")


class RSSFetcher(BaseFetcher):
    """Fetch RSS news and discover related article media."""

    def __init__(self, source):
        super().__init__(source)
        self.http = HTTPClient()

    async def fetch(self) -> List[RawNews]:
        feed_url = getattr(self.source, "url", None)

        if not feed_url:
            logger.warning(
                "RSS_FETCH | source=%s | missing feed URL",
                self.source_name,
            )
            return []

        feed_text = await self.http.get(feed_url)

        if not feed_text:
            logger.warning(
                "RSS_FETCH | source=%s | feed download failed",
                self.source_name,
            )
            return []

        try:
            feed = await asyncio.to_thread(feedparser.parse, feed_text)
        except Exception:
            logger.exception(
                "RSS_FETCH | source=%s | feed parsing failed",
                self.source_name,
            )
            return []

        entries = list(getattr(feed, "entries", []) or [])
        news_items: List[RawNews] = []
        article_jobs = []

        for entry in entries:
            try:
                title = self._clean_text(
                    self._entry_value(entry, "title", "")
                )

                article_url = (
                    self._entry_value(entry, "link", "")
                    or self._entry_value(entry, "id", "")
                )

                article_url = self._normalize_url(
                    article_url,
                    feed_url,
                )

                if not title:
                    continue

                content = self._extract_content(entry)
                summary = self._clean_text(
                    self._entry_value(entry, "summary", "")
                )

                image_url = self._extract_image_url(entry)
                video_url, video_type = self._extract_video(entry)

                published_at = self._extract_published_at(entry)
                category = self._extract_category(entry)

                raw_data = dict(entry)

                news = RawNews(
                    title=title,
                    content=content,
                    summary=summary,
                    url=article_url or "",
                    image_url=image_url or "",
                    video_url=video_url or "",
                    video_content_type=video_type or "",
                    author=self._extract_author(entry),
                    published_at=published_at,
                    source=self.source_name,
                    source_id=getattr(self.source, "id", "") or "",
                    # دسته‌هایی که برای این منبع در sources.json تعریف
                    # شده؛ CategoryDetector اگر کلیدواژه‌ها ضعیف بود از
                    # آن استفاده می‌کند (فقط وقتی منبع یک دسته دارد).
                    source_category_hint=list(
                        getattr(self.source, "categories", []) or []
                    ),
                    country=getattr(self.source, "country", "") or "",
                    language=getattr(self.source, "language", "") or "",
                    category=category,
                    raw_data=raw_data,
                )

                news_items.append(news)

                # فقط وقتی RSS خودش ویدئوی مستقیم نداده، صفحه‌ی خبر را
                # بررسی می‌کنیم.
                if (
                    not news.video_url
                    and article_url
                    and self._is_http_url(article_url)
                ):
                    cached = _ARTICLE_MEDIA_CACHE.get(article_url)

                    if cached is not None:
                        self._apply_page_media(news, *cached)

                    elif len(article_jobs) < MAX_ARTICLE_PAGES_PER_FETCH:
                        article_jobs.append((news, article_url))

            except Exception:
                logger.exception(
                    "RSS_ENTRY_ERROR | source=%s",
                    self.source_name,
                )

        if article_jobs:
            semaphore = asyncio.Semaphore(
                MAX_CONCURRENT_PAGE_REQUESTS
            )

            async def inspect_limited(news: RawNews, url: str):
                async with semaphore:
                    await self._inspect_article(news, url)

            await asyncio.gather(
                *[
                    inspect_limited(news, url)
                    for news, url in article_jobs
                ],
                return_exceptions=True,
            )

        video_count = sum(bool(item.video_url) for item in news_items)
        image_count = sum(bool(item.image_url) for item in news_items)

        logger.info(
            "RSS_PARSED | source=%s | entries=%s | "
            "article_pages_checked=%s | videos=%s | images=%s",
            self.source_name,
            len(news_items),
            len(article_jobs),
            video_count,
            image_count,
        )

        return news_items

    # ------------------------------------------------------------------
    # بررسی صفحه‌ی خبر
    # ------------------------------------------------------------------

    @staticmethod
    def _remember_article(
        article_url: str,
        media: Tuple[str, str, str, str],
    ) -> None:
        if len(_ARTICLE_MEDIA_CACHE) >= MAX_CACHED_ARTICLES:
            # قدیمی‌ترین ورودی (به ترتیب درج) را حذف می‌کنیم
            _ARTICLE_MEDIA_CACHE.pop(next(iter(_ARTICLE_MEDIA_CACHE)))

        _ARTICLE_MEDIA_CACHE[article_url] = media

    @staticmethod
    def _apply_page_media(
        news: RawNews,
        video_url: str,
        video_type: str,
        image_url: str,
        embed_url: str,
    ) -> None:
        if video_url and not news.video_url:
            news.video_url = video_url
            news.video_content_type = video_type or ""

        if image_url and not news.image_url:
            news.image_url = image_url

        news.raw_data = news.raw_data or {}

        # آدرس player یا پلی‌لیست فقط برای عیب‌یابی نگه داشته می‌شود؛
        # فایل ویدئوی قابل دانلود نیست.
        if embed_url:
            news.raw_data["video_embed_url"] = embed_url

        news.raw_data["article_media_checked"] = True

    async def _inspect_article(
        self,
        news: RawNews,
        article_url: str,
    ) -> None:
        """Inspect an article page for video and image media."""

        try:
            html = await self.http.get(article_url)

            # BBC گاهی با پارامتر clips اطلاعات کلیپ را هم برمی‌گرداند؛
            # فقط وقتی صفحه‌ی عادی جواب نداد امتحانش می‌کنیم.
            if not html and self._is_bbc_url(article_url):
                alternate_url = self._bbc_clips_url(article_url)
                if alternate_url != article_url:
                    html = await self.http.get(alternate_url)

            if not html:
                logger.debug(
                    "ARTICLE_MEDIA | source=%s | page_unavailable=%s",
                    self.source_name,
                    article_url,
                )
                self._remember_article(article_url, ("", "", "", ""))
                return

            # تحلیل HTML کار CPU است؛ در thread جدا اجرا می‌شود تا
            # بقیه‌ی دانلودها متوقف نشوند.
            media = await asyncio.to_thread(
                self._extract_page_media,
                html[:MAX_HTML_CHARS],
                article_url,
            )

            self._remember_article(article_url, media)

            video_url = media[0]

            if video_url and not news.video_url:
                logger.info(
                    "ARTICLE_VIDEO_FOUND | source=%s | title=%s | "
                    "video=%s",
                    self.source_name,
                    news.title[:100],
                    video_url,
                )

            elif not news.video_url:
                logger.info(
                    "ARTICLE_VIDEO_NOT_FOUND | source=%s | title=%s",
                    self.source_name,
                    news.title[:100],
                )

            self._apply_page_media(news, *media)

        except Exception:
            logger.exception(
                "ARTICLE_MEDIA_ERROR | source=%s | url=%s",
                self.source_name,
                article_url,
            )

    # ------------------------------------------------------------------
    # ابزارهای کمکی
    # ------------------------------------------------------------------

    @staticmethod
    def _entry_value(
        entry: Any,
        key: str,
        default: Any = None,
    ) -> Any:
        try:
            return entry.get(key, default)
        except (AttributeError, TypeError):
            return default

    @staticmethod
    def _clean_text(value: Any) -> str:
        if value is None:
            return ""

        if isinstance(value, (dict, list, tuple)):
            return ""

        text = str(value)
        soup = BeautifulSoup(text, "html.parser")
        return " ".join(soup.get_text(" ", strip=True).split())

    @staticmethod
    def _is_http_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and bool(
                parsed.netloc
            )
        except Exception:
            return False

    @staticmethod
    def _normalize_url(
        url: str,
        base_url: str = "",
    ) -> str:
        if not url:
            return ""

        url = str(url).strip().replace("&amp;", "&")

        if base_url:
            url = urljoin(base_url, url)

        if not RSSFetcher._is_http_url(url):
            return ""

        return url

    def _extract_content(self, entry: Any) -> str:
        content_parts = []

        contents = self._entry_value(entry, "content", []) or []

        if isinstance(contents, list):
            for item in contents:
                if isinstance(item, dict):
                    value = item.get("value", "")
                    cleaned = self._clean_text(value)

                    if cleaned:
                        content_parts.append(cleaned)

        if content_parts:
            return "\n\n".join(content_parts)

        summary = self._entry_value(entry, "summary", "")
        return self._clean_text(summary)

    def _extract_author(self, entry: Any) -> str:
        author = self._entry_value(entry, "author", "")

        if author:
            return self._clean_text(author)

        authors = self._entry_value(entry, "authors", []) or []

        if isinstance(authors, list):
            names = [
                self._clean_text(item.get("name", ""))
                for item in authors
                if isinstance(item, dict)
            ]
            return ", ".join(name for name in names if name)

        return ""

    def _extract_published_at(
        self,
        entry: Any,
    ) -> Optional[datetime]:
        parsed = self._entry_value(entry, "published_parsed")

        if parsed:
            try:
                from calendar import timegm

                # published_parsed در feedparser همیشه UTC است
                return datetime.fromtimestamp(
                    timegm(parsed),
                    tz=timezone.utc,
                )
            except (ValueError, TypeError, OverflowError):
                pass

        value = (
            self._entry_value(entry, "published")
            or self._entry_value(entry, "updated")
            or self._entry_value(entry, "created")
        )

        if not value:
            return None

        try:
            parsed_date = parsedate_to_datetime(str(value))

            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(
                    tzinfo=timezone.utc
                )

            return parsed_date.astimezone(timezone.utc)

        except (ValueError, TypeError, OverflowError):
            return None

    def _extract_category(self, entry: Any) -> str:
        tags = self._entry_value(entry, "tags", []) or []

        for tag in tags:
            if not isinstance(tag, dict):
                continue

            term = self._clean_text(tag.get("term", ""))

            if term:
                return term.lower()

        return ""

    # ------------------------------------------------------------------
    # عکس
    # ------------------------------------------------------------------

    def _extract_image_url(self, entry: Any) -> str:
        base_url = (
            self._entry_value(entry, "link", "")
            or getattr(self.source, "url", "")
            or ""
        )

        # RSS media:thumbnail
        thumbnails = self._entry_value(
            entry,
            "media_thumbnail",
            [],
        ) or []

        for thumbnail in thumbnails:
            if isinstance(thumbnail, dict):
                url = self._normalize_url(
                    thumbnail.get("url", ""),
                    base_url,
                )
                if url and self._looks_like_image(url):
                    return url

        # RSS media:content
        media_content = self._entry_value(
            entry,
            "media_content",
            [],
        ) or []

        for media in media_content:
            if not isinstance(media, dict):
                continue

            url = self._normalize_url(
                media.get("url", ""),
                base_url,
            )
            media_type = str(media.get("type", "")).lower()

            if url and (
                media_type.startswith("image/")
                or self._looks_like_image(url)
            ):
                return url

        # RSS enclosures and links
        links = self._entry_value(entry, "links", []) or []

        for link in links:
            if not isinstance(link, dict):
                continue

            url = self._normalize_url(
                link.get("href", ""),
                base_url,
            )
            media_type = str(link.get("type", "")).lower()
            rel = str(link.get("rel", "")).lower()

            if not url:
                continue

            if media_type.startswith("image/"):
                return url

            if rel == "enclosure" and self._looks_like_image(url):
                return url

        # بعضی فیدها عکس را داخل HTML توضیح می‌گذارند.
        html_parts = [
            self._entry_value(entry, "summary", "") or ""
        ]

        contents = self._entry_value(entry, "content", []) or []
        if isinstance(contents, list):
            html_parts.extend(
                item.get("value", "")
                for item in contents
                if isinstance(item, dict)
            )

        for html in html_parts:
            soup = BeautifulSoup(str(html), "html.parser")

            for tag in soup.find_all(["img", "source"]):
                src = (
                    tag.get("src")
                    or tag.get("data-src")
                    or tag.get("data-original")
                    or tag.get("srcset", "").split(",")[0].strip()
                )

                if src:
                    src = src.split(" ")[0]
                    url = self._normalize_url(src, base_url)

                    if url and self._looks_like_image(url):
                        return url

        return ""

    @staticmethod
    def _looks_like_image(url: str) -> bool:
        path = urlparse(url).path.lower()

        return path.endswith(
            (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")
        )

    # ------------------------------------------------------------------
    # ویدئو (داخل خود RSS)
    # ------------------------------------------------------------------

    def _extract_video(
        self,
        entry: Any,
    ) -> Tuple[str, str]:
        base_url = (
            self._entry_value(entry, "link", "")
            or getattr(self.source, "url", "")
            or ""
        )

        # media:content، از جمله medium=video که بعضی فیدها می‌گذارند
        # حتی وقتی آدرس پسوند ندارد.
        media_content = self._entry_value(
            entry,
            "media_content",
            [],
        ) or []

        for media in media_content:
            if not isinstance(media, dict):
                continue

            url = self._normalize_url(
                media.get("url", ""),
                base_url,
            )
            media_type = str(media.get("type", "")).lower()
            medium = str(media.get("medium", "")).lower()

            if url and (
                medium == "video"
                or self._looks_like_video(url, media_type)
            ):
                return url, media_type or self._guess_video_type(url)

        # enclosure
        links = self._entry_value(entry, "links", []) or []

        for link in links:
            if not isinstance(link, dict):
                continue

            url = self._normalize_url(
                link.get("href", ""),
                base_url,
            )
            media_type = str(link.get("type", "")).lower()
            rel = str(link.get("rel", "")).lower()

            if url and (
                self._looks_like_video(url, media_type)
                or (
                    rel == "enclosure"
                    and media_type.startswith("video/")
                )
            ):
                return url, media_type or self._guess_video_type(url)

        # HTML داخل summary یا content:encoded
        html_parts = [
  self._entry_value(entry, "summary", "") or ""
        ]
 
        contents = self._entry_value(entry, "content", []) or []
        if isinstance(contents, list):
            html_parts.extend(
                item.get("value", "")
                for item in contents
                if isinstance(item, dict)
            )
 
        for html in html_parts:
            video_url, video_type, _, _ = self._extract_page_media(
                str(html),
                base_url,
            )
 
            if video_url:
                return video_url, video_type
 
        return "", ""
 
    @staticmethod
    def _looks_like_video(
        url: str,
        media_type: str = "",
    ) -> bool:
        media_type = (media_type or "").lower()
 
        if any(media_type.startswith(t) for t in VIDEO_MIME_TYPES):
            return True
 
        path = urlparse(url).path.lower()
 
        return path.endswith(VIDEO_EXTENSIONS)
 
    @staticmethod
    def _guess_video_type(url: str) -> str:
        path = urlparse(url).path.lower()
 
        if path.endswith(".m3u8"):
            return "application/vnd.apple.mpegurl"
 
        if path.endswith(".mpd"):
            return "application/dash+xml"
 
        if path.endswith(".webm"):
            return "video/webm"
 
        if path.endswith(".mov"):
            return "video/quicktime"
 
        if path.endswith(".m4v"):
            return "video/x-m4v"
 
        if path.endswith(".mp4"):
            return "video/mp4"
 
        return ""
 
    @staticmethod
    def _is_bbc_url(url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
 
        return any(
            host == domain or host.endswith("." + domain)
            for domain in BBC_HOSTS
        )
 
    @staticmethod
    def _bbc_clips_url(url: str) -> str:
        """Build a bounded BBC clip-discovery URL variant."""
 
        try:
            parts = urlsplit(url)
            query = dict(
                parse_qsl(parts.query, keep_blank_values=True)
            )
 
            query.setdefault("clips", "1")
            query.setdefault("clip_format", "link")
 
            return urlunsplit(
                (
                    parts.scheme,
                    parts.netloc,
                    parts.path,
                    urlencode(query),
                    parts.fragment,
                )
            )
        except Exception:
            return url
 
    # ------------------------------------------------------------------
    # ویدئو و عکس داخل HTML
    # ------------------------------------------------------------------
 
    def _extract_page_media(
        self,
        html: str,
        page_url: str,
    ) -> Tuple[str, str, str, str]:
        """
        Return:
            direct_video_url,
            video_content_type,
            image_url,
            embedded_player_url
 
        هر مقدار پیدا نشد، رشته‌ی خالی برمی‌گردد (نه None).
        """
 
        soup = _make_soup(html)
 
        direct_candidates: List[Tuple[str, str]] = []
        weak_candidates: List[Tuple[str, str]] = []
        embed_candidates: List[str] = []
        image_candidates: List[str] = []
 
        def absolute(url: Any) -> str:
            if not isinstance(url, str) or not url.strip():
                return ""
 
            url = urljoin(
                page_url,
                url.strip().replace("&amp;", "&"),
            )
 
            return url if self._is_http_url(url) else ""
 
        def is_player_page(url: str) -> bool:
            parsed = urlparse(url)
            path = parsed.path.lower()
            host = (parsed.hostname or "").lower()
 
            return any(
                marker in path for marker in PLAYER_PATH_MARKERS
            ) or any(
                host == h or host.endswith("." + h)
                for h in EMBED_HOSTS
            )
            
