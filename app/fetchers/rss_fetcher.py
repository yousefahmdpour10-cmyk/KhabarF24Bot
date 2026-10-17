
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

VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
    ".m3u8",
    ".mpd",
)

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
                    country=getattr(self.source, "country", "") or "",
                    language=getattr(self.source, "language", "") or "",
                    category=category,
                    raw_data=raw_data,
                )

                news_items.append(news)

                # Only inspect the article when RSS did not provide a
                # usable direct video URL.
                if (
                    not news.video_url
                    and article_url
                    and self._is_http_url(article_url)
                    and len(article_jobs) < MAX_ARTICLE_PAGES_PER_FETCH
                ):
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

    async def _inspect_article(
        self,
        news: RawNews,
        article_url: str,
    ) -> None:
        """Inspect an article page for video and image media."""

        try:
            html = await self.http.get(article_url)

            # BBC syndication may expose additional clip information
            # through clip-related query parameters. Try this only when
            # the normal article response did not yield a direct video.
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
                return

            video_url, video_type, image_url, embed_url = (
                self._extract_page_media(html, article_url)
            )

            if video_url and not news.video_url:
                news.video_url = video_url
                news.video_content_type = video_type or ""

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

            if image_url and not news.image_url:
                news.image_url = image_url

            # Keep an embedded-player URL for diagnosis or a future
            # dedicated player resolver. Do not treat an iframe page as
            # a direct video file that ffmpeg can necessarily download.
            if embed_url:
                news.raw_data = news.raw_data or {}
                news.raw_data["video_embed_url"] = embed_url

            news.raw_data = news.raw_data or {}
            news.raw_data["article_media_checked"] = True

        except Exception:
            logger.exception(
                "ARTICLE_MEDIA_ERROR | source=%s | url=%s",
                self.source_name,
                article_url,
            )

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
                from time import mktime

                timestamp = mktime(parsed)
                return datetime.fromtimestamp(
                    timestamp,
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

        # Some feeds place images in the description HTML.
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

    def _extract_video(
        self,
        entry: Any,
    ) -> Tuple[str, str]:
        base_url = (
            self._entry_value(entry, "link", "")
            or getattr(self.source, "url", "")
            or ""
        )

        # Check RSS media:content, including the explicit medium=video
        # attribute used by some feeds even when the URL has no suffix.
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

        # Check RSS enclosure links.
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

        # Check content:encoded or summary HTML for video sources.
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
    def _looks_like_image(url: str) -> bool:
        path = urlparse(url).path.lower()

        return path.endswith(
            (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")
        )

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
media_type.startswith("image/")
                    or rel == "enclosure"
                    and self._looks_like_image(url, link)
                )
            ):
                return url

        return None

    @staticmethod
    def _looks_like_image(
        url: str,
        metadata: Optional[dict] = None,
    ) -> bool:
        metadata = metadata or {}

        media_type = str(
            metadata.get("type", "")
        ).lower()

        if media_type.startswith("image/"):
            return True

        path = urlparse(url).path.lower()

        return path.endswith(
            (".jpg", ".jpeg", ".png", ".webp", ".gif")
        )

    def _extract_video(
        self,
        entry,
    ) -> Tuple[Optional[str], Optional[str]]:
        for media in entry.get("media_content", []) or []:
            url = media.get("url", "")
            media_type = media.get("type", "")

            if url and self._looks_like_video(
                url,
                media_type,
            ):
                return url, media_type

        for link in entry.get("links", []) or []:
            url = link.get("href", "")
            media_type = link.get("type", "")

            if (
                url
                and link.get("rel") == "enclosure"
                and self._looks_like_video(
                    url,
                    media_type,
                )
            ):
                return url, media_type

        return None, None

    @staticmethod
    def _looks_like_video(
        url: str,
        media_type: str = "",
    ) -> bool:
        media_type = (media_type or "").lower()
        path = urlparse(url).path.lower()

        return (
            path.endswith(VIDEO_EXTENSIONS)
            or any(
                media_type.startswith(prefix)
                for prefix in VIDEO_MIME_TYPES
            )
        )

    def _extract_page_media(
        self,
        html: str,
        page_url: str,
    ) -> Tuple[
        Optional[str],
        Optional[str],
        Optional[str],
    ]:
        soup = BeautifulSoup(html, "html.parser")

        video_candidates = []
        image_candidates = []

        def add_video(url, media_type=""):
            if not isinstance(url, str) or not url.strip():
                return

            url = urljoin(page_url, url.strip())

            if not self._is_http_url(url):
                return

            if url not in [
                item[0] for item in video_candidates
            ]:
                video_candidates.append(
                    (url, media_type or "")
                )

        def add_image(url):
            if not isinstance(url, str) or not url.strip():
                return

            url = urljoin(page_url, url.strip())

            if (
                self._is_http_url(url)
                and url not in image_candidates
            ):
                image_candidates.append(url)

        # 1. Actual video and source elements.
        for video in soup.find_all("video"):
            for attribute in ("src", "data-src"):
                add_video(video.get(attribute))

            for source in video.find_all("source"):
                add_video(
                    source.get("src")
                    or source.get("data-src"),
                    source.get("type", ""),
                )

            add_image(
                video.get("poster")
                or video.get("data-poster")
            )

        # 2. Open Graph, Twitter and common player metadata.
        video_meta_names = {
            "og:video",
            "og:video:url",
            "og:video:secure_url",
            "twitter:player:stream",
            "twitter:player:stream:content_type",
            "twitter:player:video",
            "twitter:player:video:src",
        }

        for meta in soup.find_all("meta"):
            key = (
                meta.get("property")
                or meta.get("name")
                or meta.get("itemprop")
                or ""
            ).lower()

            value = meta.get("content", "")

            if key in video_meta_names and value:
                add_video(
                    value,
                    meta.get("type", ""),
                )

            if key in {
                "og:image",
                "og:image:url",
                "twitter:image",
                "twitter:image:src",
            }:
                add_image(value)

        # 3. JSON-LD and other embedded JSON objects.
        for script in soup.find_all("script"):
            script_type = str(
                script.get("type", "")
            ).lower()

            script_text = script.string or script.get_text(
                strip=True
            )

            if not script_text:
                continue

            if (
                "json" in script_type
                or script.get("id") in {
                    "__NEXT_DATA__",
                    "__NUXT_DATA__",
                }
                or script_type == ""
            ):
                self._scan_json_media(
                    script_text,
                    page_url,
                    add_video,
                    add_image,
                )

        # 4. Direct media URLs embedded in the HTML.
        # Keep extensionless CDN URLs when they appear in
        # an explicit video-related HTML attribute.
        for tag in soup.find_all(True):
            for attr in (
                "data-video",
                "data-video-url",
                "data-video-src",
                "data-src",
                "data-media-url",
                "data-playback-url",
            ):
                value = tag.get(attr)

                if isinstance(value, str) and value.startswith(
                    ("http://", "https://", "//", "/")
                ):
                    candidate = urljoin(page_url, value)

                    if (
                        self._looks_like_video(candidate)
                        or attr != "data-src"
                    ):
                        add_video(candidate)

        # Search raw HTML for direct URLs with known extensions.
        for match in VIDEO_URL_RE.findall(html):
            candidate = match.rstrip("),;]}")

            if self._looks_like_video(candidate):
                add_video(candidate)

        # Prefer actual media URLs over player-page URLs.
        for url, media_type in video_candidates:
            if self._looks_like_video(url, media_type):
                return url, media_type or "video", (
                    image_candidates[0]
                    if image_candidates
                    else None
                )

        # Extensionless URLs are accepted only when explicitly
        # identified as video by metadata/HTML player fields.
        if video_candidates:
            url, media_type = video_candidates[0]
            return (
                url,
                media_type or "video",
                image_candidates[0]
                if image_candidates
                else None,
            )

        return (
            None,
            None,
            image_candidates[0]
            if image_candidates
            else None,
        )

    def _scan_json_media(
        self,
        text: str,
        page_url: str,
        add_video,
        add_image,
    ) -> None:
        try:
            data = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            # Some player scripts contain JSON fragments rather
            # than one complete JSON document.
            data = None

        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    normalized = re.sub(
                        r"[^a-z0-9_]",
                        "",
                        str(key).lower(),
                    )

                    if isinstance(child, str):
                        if normalized in VIDEO_KEYS:
                            add_video(
                                urljoin(page_url, child)
                            )
                        elif normalized in IMAGE_KEYS:
                            add_image(
                                urljoin(page_url, child)
                            )

                        # Some schemas use contentUrl with a
                        # MIME type in a sibling field.
                        elif (
                            normalized in {
                                "url",
                                "src",
                                "embedurl",
                            }
                            and self._looks_like_video(child)
                        ):
                            add_video(
                                urljoin(page_url, child)
                            )

                    elif isinstance(child, (dict, list)):
                        walk(child)

            elif isinstance(value, list):
                for item in value:
                    walk(item)

        if data is not None:
            walk(data)

        # Also inspect escaped URLs in player JSON, even when
        # the surrounding script is not valid JSON.
        for match in VIDEO_URL_RE.findall(text):
            candidate = (
                match.replace("\\/", "/")
                .replace("\\u0026", "&")
                .rstrip("\\),;]}")
            )

            if self._looks_like_video(candidate):
                add_video(candidate)
