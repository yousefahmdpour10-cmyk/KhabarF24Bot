"""
RSS Fetcher

دریافت خبر از منابع RSS، به‌همراه پیدا کردن عکس و ویدئوی هر خبر
(اول از خود RSS، و اگر نبود از صفحه‌ی خبر). تحلیل HTML در
media_extractor.py انجام می‌شود.
"""

import asyncio
import logging
import time
from calendar import timegm
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
from app.fetchers.media_extractor import (
    extract_page_media,
    guess_video_type,
    is_http_url,
    looks_like_image,
    looks_like_video,
)
from app.models.raw_news import RawNews
from app.utils.http_client import HTTPClient

logger = logging.getLogger(__name__)

MAX_ARTICLE_PAGES_PER_FETCH = 30
MAX_CONCURRENT_PAGE_REQUESTS = 5
MAX_HTML_CHARS = 1_500_000

# نتیجه‌ی بررسی صفحه‌ی هر خبر را نگه می‌داریم تا همان خبر در چرخه‌های
# بعد (که RSS هنوز آن را دارد) دوباره دانلود و تحلیل نشود.
MAX_CACHED_ARTICLES = 5000
_ARTICLE_MEDIA_CACHE: Dict[str, Tuple[str, str, str, str]] = {}

BBC_HOSTS = ("bbc.com", "bbc.co.uk", "bbci.co.uk", "bbc.in")

# اگر از یک سایت چند بار پشت‌سرهم خطا گرفتیم (مثلاً ۴۰۱ یا ۴۰۳ چون ربات را
# بلاک کرده یا مقاله پشت پرداخت است)، مدتی سراغ صفحه‌های آن سایت
# نمی‌رویم: هم درخواست بیهوده نمی‌زنیم، هم ریسک بلاک‌شدن IP کمتر می‌شود.
HOST_FAILURE_LIMIT = 5
HOST_COOLDOWN_SECONDS = 30 * 60
_HOST_STATE: Dict[str, List[float]] = {}  # host -> [خطاهای پیاپی, تا چه زمانی متوقف]


class RSSFetcher(BaseFetcher):
    """Fetch RSS news and discover related article media."""

    def __init__(self, source):
        super().__init__(source)
        self.http = HTTPClient()

    # ------------------------------------------------------------------
    # دریافت فید
    # ------------------------------------------------------------------

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

        news_items: List[RawNews] = []
        article_jobs = []

        for entry in list(getattr(feed, "entries", []) or []):
            try:
                news = self._build_news(entry, feed_url)

                if news is None:
                    continue

                news_items.append(news)

                # فقط وقتی RSS خودش ویدئوی مستقیم نداده، صفحه‌ی خبر را
                # بررسی می‌کنیم.
                if news.video_url or not is_http_url(news.url):
                    continue

                cached = _ARTICLE_MEDIA_CACHE.get(news.url)

                if cached is not None:
                    self._apply_page_media(news, *cached)
                elif len(article_jobs) < MAX_ARTICLE_PAGES_PER_FETCH:
                    article_jobs.append((news, news.url))

            except Exception:
                logger.exception(
                    "RSS_ENTRY_ERROR | source=%s",
                    self.source_name,
                )

        await self._inspect_articles(article_jobs)

        logger.info(
            "RSS_PARSED | source=%s | entries=%s | "
            "article_pages_checked=%s | videos=%s | images=%s",
            self.source_name,
            len(news_items),
            len(article_jobs),
            sum(bool(item.video_url) for item in news_items),
            sum(bool(item.image_url) for item in news_items),
        )

        return news_items

    def _build_news(self, entry: Any, feed_url: str) -> Optional[RawNews]:
        title = self._clean_text(self._entry_value(entry, "title", ""))

        if not title:
            return None

        article_url = self._normalize_url(
            self._entry_value(entry, "link", "")
            or self._entry_value(entry, "id", ""),
            feed_url,
        )

        video_url, video_type = self._extract_video(entry)

        return RawNews(
            title=title,
            content=self._extract_content(entry),
            summary=self._clean_text(self._entry_value(entry, "summary", "")),
            url=article_url or "",
            image_url=self._extract_image_url(entry) or "",
            video_url=video_url or "",
            video_content_type=video_type or "",
            author=self._extract_author(entry),
            published_at=self._extract_published_at(entry),
            source=self.source_name,
            source_id=getattr(self.source, "id", "") or "",
            # دسته‌هایی که برای این منبع در sources.json تعریف شده؛
            # CategoryDetector اگر کلیدواژه‌ها ضعیف بود از آن استفاده
            # می‌کند (فقط وقتی منبع یک دسته دارد).
            source_category_hint=list(
                getattr(self.source, "categories", []) or []
            ),
            country=getattr(self.source, "country", "") or "",
            language=getattr(self.source, "language", "") or "",
            category=self._extract_category(entry),
            raw_data=dict(entry),
        )

    # ------------------------------------------------------------------
    # بررسی صفحه‌ی خبر
    # ------------------------------------------------------------------

    async def _inspect_articles(self, article_jobs: list) -> None:
        if not article_jobs:
            return

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGE_REQUESTS)

        async def inspect_limited(news: RawNews, url: str):
            async with semaphore:
                await self._inspect_article(news, url)

        await asyncio.gather(
            *[inspect_limited(news, url) for news, url in article_jobs],
            return_exceptions=True,
        )

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

    @staticmethod
    def _host_paused(host: str) -> bool:
        state = _HOST_STATE.get(host)
        return bool(state) and time.monotonic() < state[1]

    @staticmethod
    def _note_host_failure(host: str) -> None:
        state = _HOST_STATE.setdefault(host, [0, 0.0])
        state[0] += 1

        if state[0] >= HOST_FAILURE_LIMIT:
            state[0] = 0
            state[1] = time.monotonic() + HOST_COOLDOWN_SECONDS

            logger.warning(
                "ARTICLE_HOST_PAUSED | host=%s | minutes=%s",
                host,
                HOST_COOLDOWN_SECONDS // 60,
            )

    @staticmethod
    def _note_host_success(host: str) -> None:
        _HOST_STATE.pop(host, None)

    async def _inspect_article(
        self,
        news: RawNews,
        article_url: str,
    ) -> None:
        """Inspect an article page for video and image media."""

        host = (urlparse(article_url).hostname or "").lower()

        if self._host_paused(host):
            # عمداً در حافظه ثبت نمی‌شود تا بعد از پایان مکث دوباره امتحان شود
            return

        try:
            html = await self.http.get(article_url)

            # BBC گاهی با پارامتر clips اطلاعات کلیپ را هم برمی‌گرداند؛
            # فقط وقتی صفحه‌ی عادی جواب نداد امتحانش می‌کنیم.
            if not html and self._is_bbc_url(article_url):
                alternate_url = self._bbc_clips_url(article_url)
                if alternate_url != article_url:
                    html = await self.http.get(alternate_url)

            if not html:
                self._note_host_failure(host)
                self._remember_article(article_url, ("", "", "", ""))
                return

            self._note_host_success(host)

            # تحلیل HTML کار CPU است؛ در thread جدا اجرا می‌شود تا
            # بقیه‌ی دانلودها متوقف نشوند.
            media = await asyncio.to_thread(
                extract_page_media,
                html[:MAX_HTML_CHARS],
                article_url,
            )

            self._remember_article(article_url, media)

            if media[0]:
                logger.info(
                    "ARTICLE_VIDEO_FOUND | source=%s | title=%s | video=%s",
                    self.source_name,
                    news.title[:100],
                    media[0],
                )
            else:
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
    def _entry_value(entry: Any, key: str, default: Any = None) -> Any:
        try:
            return entry.get(key, default)
        except (AttributeError, TypeError):
            return default

    @staticmethod
    def _clean_text(value: Any) -> str:
        if value is None or isinstance(value, (dict, list, tuple)):
            return ""

        soup = BeautifulSoup(str(value), "html.parser")
        return " ".join(soup.get_text(" ", strip=True).split())

    @staticmethod
    def _is_http_url(url: str) -> bool:
        return is_http_url(url)

    @staticmethod
    def _normalize_url(url: str, base_url: str = "") -> str:
        if not url:
            return ""

        url = str(url).strip().replace("&amp;", "&")

        if base_url:
            url = urljoin(base_url, url)

        return url if is_http_url(url) else ""

    def _base_url(self, entry: Any) -> str:
        return (
            self._entry_value(entry, "link", "")
            or getattr(self.source, "url", "")
            or ""
        )

    def _html_parts(self, entry: Any) -> List[str]:
        """HTML داخل summary و content:encoded."""

        parts = [self._entry_value(entry, "summary", "") or ""]
        contents = self._entry_value(entry, "content", []) or []

        if isinstance(contents, list):
            parts.extend(
                item.get("value", "")
                for item in contents
                if isinstance(item, dict)
            )

        return parts

    def _extract_content(self, entry: Any) -> str:
        contents = self._entry_value(entry, "content", []) or []
        content_parts = []

        if isinstance(contents, list):
            for item in contents:
                if isinstance(item, dict):
                    cleaned = self._clean_text(item.get("value", ""))
                    if cleaned:
                        content_parts.append(cleaned)

        if content_parts:
            return "\n\n".join(content_parts)

        return self._clean_text(self._entry_value(entry, "summary", ""))

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

    def _extract_published_at(self, entry: Any) -> Optional[datetime]:
        parsed = self._entry_value(entry, "published_parsed")

        if parsed:
            try:
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
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)

            return parsed_date.astimezone(timezone.utc)

        except (ValueError, TypeError, OverflowError):
            return None

    def _extract_category(self, entry: Any) -> str:
        for tag in self._entry_value(entry, "tags", []) or []:
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
        base_url = self._base_url(entry)

        # RSS media:thumbnail
        for thumbnail in self._entry_value(entry, "media_thumbnail", []) or []:
            if isinstance(thumbnail, dict):
                url = self._normalize_url(thumbnail.get("url", ""), base_url)
                if url and looks_like_image(url):
                    return url

        # RSS media:content
        for media in self._entry_value(entry, "media_content", []) or []:
            if not isinstance(media, dict):
                continue

            url = self._normalize_url(media.get("url", ""), base_url)
            media_type = str(media.get("type", "")).lower()

            if url and (
                media_type.startswith("image/") or looks_like_image(url)
            ):
                return url

        # RSS enclosures and links
        for link in self._entry_value(entry, "links", []) or []:
            if not isinstance(link, dict):
                continue

            url = self._normalize_url(link.get("href", ""), base_url)
            media_type = str(link.get("type", "")).lower()
            rel = str(link.get("rel", "")).lower()

            if not url:
                continue

            if media_type.startswith("image/"):
                return url

            if rel == "enclosure" and looks_like_image(url):
                return url

        # بعضی فیدها عکس را داخل HTML توضیح می‌گذارند.
        for html in self._html_parts(entry):
            soup = BeautifulSoup(str(html), "html.parser")

            for tag in soup.find_all(["img", "source"]):
                src = (
                    tag.get("src")
                    or tag.get("data-src")
                    or tag.get("data-original")
                    or tag.get("srcset", "").split(",")[0].strip()
                )

                if src:
                    url = self._normalize_url(src.split(" ")[0], base_url)

                    if url and looks_like_image(url):
                        return url

        return ""

    # ------------------------------------------------------------------
    # ویدئو (داخل خود RSS)
    # ------------------------------------------------------------------

    def _extract_video(self, entry: Any) -> Tuple[str, str]:
        base_url = self._base_url(entry)

        # media:content، از جمله medium=video که بعضی فیدها می‌گذارند
        # حتی وقتی آدرس پسوند ندارد.
        for media in self._entry_value(entry, "media_content", []) or []:
            if not isinstance(media, dict):
                continue

            url = self._normalize_url(media.get("url", ""), base_url)
            media_type = str(media.get("type", "")).lower()
            medium = str(media.get("medium", "")).lower()

            if url and (
                medium == "video" or looks_like_video(url, media_type)
            ):
                return url, media_type or guess_video_type(url)

        # enclosure
        for link in self._entry_value(entry, "links", []) or []:
            if not isinstance(link, dict):
                continue

            url = self._normalize_url(link.get("href", ""), base_url)
            media_type = str(link.get("type", "")).lower()
            rel = str(link.get("rel", "")).lower()

            is_video_enclosure = (
                rel == "enclosure" and media_type.startswith("video/")
            )

            if url and (looks_like_video(url, media_type) or is_video_enclosure):
                return url, media_type or guess_video_type(url)

        # HTML داخل summary یا content:encoded
        for html in self._html_parts(entry):
            video_url, video_type, _, _ = extract_page_media(
                str(html),
                base_url,
            )

            if video_url:
                return video_url, video_type

        return "", ""

    # ------------------------------------------------------------------
    # نام‌های قدیمی (برای کدهایی که ممکن است مستقیم صدایشان بزنند)
    # ------------------------------------------------------------------

    @staticmethod
    def _looks_like_image(url: str) -> bool:
        return looks_like_image(url)

    @staticmethod
    def _looks_like_video(url: str, media_type: str = "") -> bool:
        return looks_like_video(url, media_type)

    @staticmethod
    def _guess_video_type(url: str) -> str:
        return guess_video_type(url)

    def _extract_page_media(
        self,
        html: str,
        page_url: str,
    ) -> Tuple[str, str, str, str]:
        return extract_page_media(html, page_url)

    # ------------------------------------------------------------------
    # BBC
    # ------------------------------------------------------------------

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
            query = dict(parse_qsl(parts.query, keep_blank_values=True))

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
