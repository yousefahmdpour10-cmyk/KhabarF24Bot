"""
RSS Fetcher

Ø¯Ø±ÛŒØ§ÙØª Ø®Ø¨Ø± Ø§Ø² Ù…Ù†Ø§Ø¨Ø¹ RSSØŒ Ø¨Ù‡â€ŒÙ‡Ù…Ø±Ø§Ù‡ Ù¾ÛŒØ¯Ø§ Ú©Ø±Ø¯Ù† Ø¹Ú©Ø³ Ùˆ ÙˆÛŒØ¯Ø¦ÙˆÛŒ Ù‡Ø± Ø®Ø¨Ø±
(Ø§ÙˆÙ„ Ø§Ø² Ø®ÙˆØ¯ RSSØŒ Ùˆ Ø§Ú¯Ø± Ù†Ø¨ÙˆØ¯ Ø§Ø² ØµÙØ­Ù‡â€ŒÛŒ Ø®Ø¨Ø±). ØªØ­Ù„ÛŒÙ„ HTML Ø¯Ø±
media_extractor.py Ø§Ù†Ø¬Ø§Ù… Ù…ÛŒâ€ŒØ´ÙˆØ¯.
"""

import asyncio
import logging
import re
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
    url_host,
)
from app.models.raw_news import RawNews
from app.utils.http_client import HTTPClient

logger = logging.getLogger(__name__)

MAX_ARTICLE_PAGES_PER_FETCH = 30
MAX_CONCURRENT_PAGE_REQUESTS = 5
MAX_HTML_CHARS = 1_500_000

# Ù†ØªÛŒØ¬Ù‡â€ŒÛŒ Ø¨Ø±Ø±Ø³ÛŒ ØµÙØ­Ù‡â€ŒÛŒ Ù‡Ø± Ø®Ø¨Ø± Ø±Ø§ Ù†Ú¯Ù‡ Ù…ÛŒâ€ŒØ¯Ø§Ø±ÛŒÙ… ØªØ§ Ù‡Ù…Ø§Ù† Ø®Ø¨Ø± Ø¯Ø± Ú†Ø±Ø®Ù‡â€ŒÙ‡Ø§ÛŒ
# Ø¨Ø¹Ø¯ (Ú©Ù‡ RSS Ù‡Ù†ÙˆØ² Ø¢Ù† Ø±Ø§ Ø¯Ø§Ø±Ø¯) Ø¯ÙˆØ¨Ø§Ø±Ù‡ Ø¯Ø§Ù†Ù„ÙˆØ¯ Ùˆ ØªØ­Ù„ÛŒÙ„ Ù†Ø´ÙˆØ¯.
MAX_CACHED_ARTICLES = 5000
_ARTICLE_MEDIA_CACHE: Dict[str, Tuple[str, str, str, str]] = {}

BBC_HOSTS = ("bbc.com", "bbc.co.uk", "bbci.co.uk", "bbc.in")

# Ø§Ú¯Ø± Ø§Ø² ÛŒÚ© Ø³Ø§ÛŒØª Ú†Ù†Ø¯ Ø¨Ø§Ø± Ù¾Ø´Øªâ€ŒØ³Ø±Ù‡Ù… Ø®Ø·Ø§ Ú¯Ø±ÙØªÛŒÙ… (Ù…Ø«Ù„Ø§Ù‹ Û´Û°Û± ÛŒØ§ Û´Û°Û³ Ú†ÙˆÙ† Ø±Ø¨Ø§Øª Ø±Ø§
# Ø¨Ù„Ø§Ú© Ú©Ø±Ø¯Ù‡ ÛŒØ§ Ù…Ù‚Ø§Ù„Ù‡ Ù¾Ø´Øª Ù¾Ø±Ø¯Ø§Ø®Øª Ø§Ø³Øª)ØŒ Ù…Ø¯ØªÛŒ Ø³Ø±Ø§Øº ØµÙØ­Ù‡â€ŒÙ‡Ø§ÛŒ Ø¢Ù† Ø³Ø§ÛŒØª
# Ù†Ù…ÛŒâ€ŒØ±ÙˆÛŒÙ…: Ù‡Ù… Ø¯Ø±Ø®ÙˆØ§Ø³Øª Ø¨ÛŒÙ‡ÙˆØ¯Ù‡ Ù†Ù…ÛŒâ€ŒØ²Ù†ÛŒÙ…ØŒ Ù‡Ù… Ø±ÛŒØ³Ú© Ø¨Ù„Ø§Ú©â€ŒØ´Ø¯Ù† IP Ú©Ù…ØªØ± Ù…ÛŒâ€ŒØ´ÙˆØ¯.
HOST_FAILURE_LIMIT = 5
HOST_COOLDOWN_SECONDS = 30 * 60
_HOST_STATE: Dict[str, List[float]] = {}  # host -> [Ø®Ø·Ø§Ù‡Ø§ÛŒ Ù¾ÛŒØ§Ù¾ÛŒ, ØªØ§ Ú†Ù‡ Ø²Ù…Ø§Ù†ÛŒ Ù…ØªÙˆÙ‚Ù]


class RSSFetcher(BaseFetcher):
    """Fetch RSS news and discover related article media."""

    def __init__(self, source):
        super().__init__(source)
        self.http = HTTPClient()

    # ------------------------------------------------------------------
    # Ø¯Ø±ÛŒØ§ÙØª ÙÛŒØ¯
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

                # ÙÙ‚Ø· ÙˆÙ‚ØªÛŒ RSS Ø®ÙˆØ¯Ø´ ÙˆÛŒØ¯Ø¦ÙˆÛŒ Ù…Ø³ØªÙ‚ÛŒÙ… Ù†Ø¯Ø§Ø¯Ù‡ØŒ ØµÙØ­Ù‡â€ŒÛŒ Ø®Ø¨Ø± Ø±Ø§
                # Ø¨Ø±Ø±Ø³ÛŒ Ù…ÛŒâ€ŒÚ©Ù†ÛŒÙ….
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
            # Ø¯Ø³ØªÙ‡â€ŒÙ‡Ø§ÛŒÛŒ Ú©Ù‡ Ø¨Ø±Ø§ÛŒ Ø§ÛŒÙ† Ù…Ù†Ø¨Ø¹ Ø¯Ø± sources.json ØªØ¹Ø±ÛŒÙ Ø´Ø¯Ù‡Ø›
            # CategoryDetector Ø§Ú¯Ø± Ú©Ù„ÛŒØ¯ÙˆØ§Ú˜Ù‡â€ŒÙ‡Ø§ Ø¶Ø¹ÛŒÙ Ø¨ÙˆØ¯ Ø§Ø² Ø¢Ù† Ø§Ø³ØªÙØ§Ø¯Ù‡
            # Ù…ÛŒâ€ŒÚ©Ù†Ø¯ (ÙÙ‚Ø· ÙˆÙ‚ØªÛŒ Ù…Ù†Ø¨Ø¹ ÛŒÚ© Ø¯Ø³ØªÙ‡ Ø¯Ø§Ø±Ø¯).
            source_category_hint=list(
                getattr(self.source, "categories", []) or []
            ),
            country=getattr(self.source, "country", "") or "",
            language=getattr(self.source, "language", "") or "",
            category=self._extract_category(entry),
            raw_data=dict(entry),
        )

    # ------------------------------------------------------------------
    # Ø¨Ø±Ø±Ø³ÛŒ ØµÙØ­Ù‡â€ŒÛŒ Ø®Ø¨Ø±
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
            # Ù‚Ø¯ÛŒÙ…ÛŒâ€ŒØªØ±ÛŒÙ† ÙˆØ±ÙˆØ¯ÛŒ (Ø¨Ù‡ ØªØ±ØªÛŒØ¨ Ø¯Ø±Ø¬) Ø±Ø§ Ø­Ø°Ù Ù…ÛŒâ€ŒÚ©Ù†ÛŒÙ…
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

        # Ø¢Ø¯Ø±Ø³ player ÛŒØ§ Ù¾Ù„ÛŒâ€ŒÙ„ÛŒØ³Øª ÙÙ‚Ø· Ø¨Ø±Ø§ÛŒ Ø¹ÛŒØ¨â€ŒÛŒØ§Ø¨ÛŒ Ù†Ú¯Ù‡ Ø¯Ø§Ø´ØªÙ‡ Ù…ÛŒâ€ŒØ´ÙˆØ¯Ø›
        # ÙØ§ÛŒÙ„ ÙˆÛŒØ¯Ø¦ÙˆÛŒ Ù‚Ø§Ø¨Ù„ Ø¯Ø§Ù†Ù„ÙˆØ¯ Ù†ÛŒØ³Øª.
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

    @staticmethod
    def _extract_article_text(html: str) -> str:
        """Ø§Ø³ØªØ®Ø±Ø§Ø¬ Ù…ØªÙ† Ù…Ù‚Ø§Ù„Ù‡ Ø§Ø² HTML Ø¨Ø§ Ø­Ø°Ù Ø¨Ø®Ø´â€ŒÙ‡Ø§ÛŒ ØºÛŒØ±Ù…Ù‚Ø§Ù„Ù‡â€ŒØ§ÛŒ."""
        soup = BeautifulSoup(html or "", "lxml")

        for element in soup.find_all([
            "script", "style", "noscript", "nav", "footer", "header",
            "aside", "form", "button", "svg", "iframe",
        ]):
            element.decompose()

        article = (
            soup.find("article")
            or soup.find(attrs={"itemprop": "articleBody"})
            or soup.find("main")
        )

        if article:
            text = " ".join(article.get_text(" ", strip=True).split())
            if len(text) >= 200:
                return text

        paragraphs = []
        for paragraph in soup.find_all("p"):
            text = " ".join(paragraph.get_text(" ", strip=True).split())
            if len(text) >= 40:
                paragraphs.append(text)

        unique = list(dict.fromkeys(paragraphs))
        return " ".join(unique)[:12000]

    async def _inspect_article(
        self,
        news: RawNews,
        article_url: str,
    ) -> None:
        """Inspect an article page for video and image media."""

        host = url_host(article_url)

        if self._host_paused(host):
            # Ø¹Ù…Ø¯Ø§Ù‹ Ø¯Ø± Ø­Ø§ÙØ¸Ù‡ Ø«Ø¨Øª Ù†Ù…ÛŒâ€ŒØ´ÙˆØ¯ ØªØ§ Ø¨Ø¹Ø¯ Ø§Ø² Ù¾Ø§ÛŒØ§Ù† Ù…Ú©Ø« Ø¯ÙˆØ¨Ø§Ø±Ù‡ Ø§Ù…ØªØ­Ø§Ù† Ø´ÙˆØ¯
            return

        try:
            html = await self.http.get(article_url)

            # BBC Ú¯Ø§Ù‡ÛŒ Ø¨Ø§ Ù¾Ø§Ø±Ø§Ù…ØªØ± clips Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ú©Ù„ÛŒÙ¾ Ø±Ø§ Ù‡Ù… Ø¨Ø±Ù…ÛŒâ€ŒÚ¯Ø±Ø¯Ø§Ù†Ø¯Ø›
            # ÙÙ‚Ø· ÙˆÙ‚ØªÛŒ ØµÙØ­Ù‡â€ŒÛŒ Ø¹Ø§Ø¯ÛŒ Ø¬ÙˆØ§Ø¨ Ù†Ø¯Ø§Ø¯ Ø§Ù…ØªØ­Ø§Ù†Ø´ Ù…ÛŒâ€ŒÚ©Ù†ÛŒÙ….
            if not html and self._is_bbc_url(article_url):
                alternate_url = self._bbc_clips_url(article_url)
                if alternate_url != article_url:
                    html = await self.http.get(alternate_url)

            if not html:
                self._note_host_failure(host)
                self._remember_article(article_url, ("", "", "", ""))
                return

            self._note_host_success(host)

            # Ù…ØªÙ† Ù…Ù‚Ø§Ù„Ù‡ Ø±Ø§ Ù‡Ù… Ø§Ø² HTML Ø§Ø³ØªØ®Ø±Ø§Ø¬ Ù…ÛŒâ€ŒÚ©Ù†ÛŒÙ…Ø› RSS Ø¨Ø¹Ø¶ÛŒ Ù…Ù†Ø§Ø¨Ø¹
            # ÙÙ‚Ø· ÛŒÚ© Ø®Ù„Ø§ØµÙ‡ Ú©ÙˆØªØ§Ù‡ Ø¯Ø§Ø±Ø¯. Ù…ØªÙ† RSS ÙÙ‚Ø· ÙˆÙ‚ØªÛŒ Ø¬Ø§ÛŒÚ¯Ø²ÛŒÙ† Ù…ÛŒâ€ŒØ´ÙˆØ¯
            # Ú©Ù‡ Ù…ØªÙ† ØµÙØ­Ù‡ Ø·ÙˆÙ„Ø§Ù†ÛŒâ€ŒØªØ± Ùˆ Ø§Ø­ØªÙ…Ø§Ù„Ø§Ù‹ Ú©Ø§Ù…Ù„â€ŒØªØ± Ø¨Ø§Ø´Ø¯.
            try:
                article_text = await asyncio.to_thread(
                    self._extract_article_text,
                    html[:MAX_HTML_CHARS],
                )
                current_content = self._clean_text(news.content)
                if article_text and len(article_text) > len(current_content):
                    news.content = article_text[:12000]
                    if not news.summary or len(news.summary) < 80:
                        news.summary = article_text[:500]
                    news.raw_data = news.raw_data or {}
                    news.raw_data["article_text_enriched"] = True
            except Exception:
                logger.debug(
                    "ARTICLE_TEXT_EXTRACTION_FAILED | source=%s | title=%s",
                    self.source_name,
                    news.title[:100],
                )

            # ØªØ­Ù„ÛŒÙ„ HTML Ú©Ø§Ø± CPU Ø§Ø³ØªØ› Ø¯Ø± thread Ø¬Ø¯Ø§ Ø§Ø¬Ø±Ø§ Ù…ÛŒâ€ŒØ´ÙˆØ¯ ØªØ§
            # Ø¨Ù‚ÛŒÙ‡â€ŒÛŒ Ø¯Ø§Ù†Ù„ÙˆØ¯Ù‡Ø§ Ù…ØªÙˆÙ‚Ù Ù†Ø´ÙˆÙ†Ø¯.
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
            # Ø¨Ø¯ÙˆÙ† Ø§ÛŒÙ†ØŒ Ù‡Ù…Ø§Ù† ØµÙØ­Ù‡â€ŒÛŒ Ù…Ø´Ú©Ù„â€ŒØ¯Ø§Ø± Ù‡Ø± Ú†Ø±Ø®Ù‡ Ø¯ÙˆØ¨Ø§Ø±Ù‡ Ø¯Ø§Ù†Ù„ÙˆØ¯ Ù…ÛŒâ€ŒØ´Ø¯
            self._remember_article(article_url, ("", "", "", ""))

    # ------------------------------------------------------------------
    # Ø§Ø¨Ø²Ø§Ø±Ù‡Ø§ÛŒ Ú©Ù…Ú©ÛŒ
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

        # Ø¨Ø¹Ø¶ÛŒ ÙˆØ±ÙˆØ¯ÛŒâ€ŒÙ‡Ø§ URL Ø±Ø§ Ø¨Ù‡ Ø´Ú©Ù„ Markdown Ù…ÛŒâ€ŒØ¯Ù‡Ù†Ø¯:
        # [https://example.com/article](https://example.com/article)
        markdown_match = re.match(r"^\[([^\]]+)\]\((https?://[^)]+)\)$", url)
        if markdown_match:
            url = markdown_match.group(2).strip()

        if base_url:
            try:
                url = urljoin(base_url, url)
            except ValueError:
                return ""

        return url if is_http_url(url) else ""

    def _base_url(self, entry: Any) -> str:
        return (
            self._entry_value(entry, "link", "")
            or getattr(self.source, "url", "")
            or ""
        )

    def _html_parts(self, entry: Any) -> List[str]:
        """HTML Ø¯Ø§Ø®Ù„ summary Ùˆ content:encoded."""

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
                # published_parsed Ø¯Ø± feedparser Ù‡Ù…ÛŒØ´Ù‡ UTC Ø§Ø³Øª
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
    # Ø¹Ú©Ø³
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

        # Ø¨Ø¹Ø¶ÛŒ ÙÛŒØ¯Ù‡Ø§ Ø¹Ú©Ø³ Ø±Ø§ Ø¯Ø§Ø®Ù„ HTML ØªÙˆØ¶ÛŒØ­ Ù…ÛŒâ€ŒÚ¯Ø°Ø§Ø±Ù†Ø¯.
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
    # ÙˆÛŒØ¯Ø¦Ùˆ (Ø¯Ø§Ø®Ù„ Ø®ÙˆØ¯ RSS)
    # ------------------------------------------------------------------

    def _extract_video(self, entry: Any) -> Tuple[str, str]:
        base_url = self._base_url(entry)

        # media:contentØŒ Ø§Ø² Ø¬Ù…Ù„Ù‡ medium=video Ú©Ù‡ Ø¨Ø¹Ø¶ÛŒ ÙÛŒØ¯Ù‡Ø§ Ù…ÛŒâ€ŒÚ¯Ø°Ø§Ø±Ù†Ø¯
        # Ø­ØªÛŒ ÙˆÙ‚ØªÛŒ Ø¢Ø¯Ø±Ø³ Ù¾Ø³ÙˆÙ†Ø¯ Ù†Ø¯Ø§Ø±Ø¯.
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

        # HTML Ø¯Ø§Ø®Ù„ summary ÛŒØ§ content:encoded
        for html in self._html_parts(entry):
            video_url, video_type, _, _ = extract_page_media(
                str(html),
                base_url,
            )

            if video_url:
                return video_url, video_type

        return "", ""

    # ------------------------------------------------------------------
    # Ù†Ø§Ù…â€ŒÙ‡Ø§ÛŒ Ù‚Ø¯ÛŒÙ…ÛŒ (Ø¨Ø±Ø§ÛŒ Ú©Ø¯Ù‡Ø§ÛŒÛŒ Ú©Ù‡ Ù…Ù…Ú©Ù† Ø§Ø³Øª Ù…Ø³ØªÙ‚ÛŒÙ… ØµØ¯Ø§ÛŒØ´Ø§Ù† Ø¨Ø²Ù†Ù†Ø¯)
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
        host = url_host(url)

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
