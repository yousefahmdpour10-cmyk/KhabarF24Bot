"""
KhabarF24 RSS Fetcher
RSS + article-page media extraction
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import feedparser
from bs4 import BeautifulSoup

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.http_client import HTTPClient

logger = logging.getLogger(__name__)

MAX_ARTICLE_PAGES_PER_FETCH = 30
MAX_CONCURRENT_PAGE_REQUESTS = 5

VIDEO_EXTENSIONS = (
    ".mp4", ".webm", ".mov", ".m4v", ".m3u8", ".mpd",
)

VIDEO_MIME_TYPES = (
    "video/",
    "application/vnd.apple.mpegurl",
    "application/x-mpegurl",
    "application/dash+xml",
)

VIDEO_URL_RE = re.compile(
    r"""https?://[^\s"'<>\\]+""",
    re.IGNORECASE,
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
}

IMAGE_KEYS = {
    "thumbnailurl",
    "thumbnail_url",
    "image",
    "imageurl",
    "image_url",
    "thumbnail",
}


class RSSFetcher(BaseFetcher):
    def __init__(self, source):
        super().__init__(source)
        self.http = HTTPClient()

    async def fetch(self) -> List[RawNews]:
        feed_url = getattr(self.source, "url", None)

        if not feed_url:
            logger.warning("RSS source has no URL: %s", self.source)
            return []

        try:
            feed_text = await self.http.get(feed_url)

            if not feed_text:
                logger.warning("RSS download failed: %s", feed_url)
                return []

            feed = await asyncio.to_thread(feedparser.parse, feed_text)

            if getattr(feed, "bozo", False):
                logger.debug(
                    "RSS parser warning for %s: %s",
                    feed_url,
                    getattr(feed, "bozo_exception", ""),
                )

            entries = list(getattr(feed, "entries", []) or [])
            news_items: List[RawNews] = []
            article_jobs = []

            for entry in entries:
                title = self._clean_text(
                    entry.get("title", "")
                )

                article_url = (
                    entry.get("link")
                    or entry.get("id")
                    or ""
                )

                if not title or not article_url:
                    continue

                content = self._extract_content(entry)
                summary = self._clean_text(
                    entry.get("summary", "")
                )
                image_url = self._extract_image_url(entry)

                video_url, video_type = self._extract_video(entry)

                raw_data = dict(entry)

                item = RawNews(
                    source_id=getattr(
                        self.source, "id", ""
                    ),
                    source=getattr(
                        self.source,
                        "name",
                        "Unknown",
                    ),
                    title=title,
                    content=content,
                    summary=summary,
                    url=article_url,
                    published_at=self._extract_published_at(
                        entry
                    ),
                    language=getattr(
                        self.source, "language", "en"
                    ),
                    category=self._extract_category(),
                    image_url=image_url or "",
                    video_url=video_url or "",
                    video_content_type=video_type or "",
                    raw_data=raw_data,
                    tags=[],
                )

                news_items.append(item)

                # Also inspect the article page. RSS media fields
                # frequently contain only thumbnails.
                if (
                    not video_url
                    and self._is_http_url(article_url)
                    and len(article_jobs)
                    < MAX_ARTICLE_PAGES_PER_FETCH
                ):
                    article_jobs.append(
                        (item, article_url)
                    )

            semaphore = asyncio.Semaphore(
                MAX_CONCURRENT_PAGE_REQUESTS
            )

            async def inspect_article(item, url):
                async with semaphore:
                    try:
                        html = await self.http.get(url)

                        if not html:
                            logger.debug(
                                "Could not load article: %s",
                                url,
                            )
                            return

                        video, content_type, image = (
                            self._extract_page_media(
                                html,
                                url,
                            )
                        )

                        if video:
                            item.video_url = video
                            item.video_content_type = (
                                content_type or ""
                            )

                            logger.info(
                                "ARTICLE VIDEO FOUND | %s | %s",
                                getattr(
                                    self.source,
                                    "name",
                                    "RSS",
                                ),
                                video[:250],
                            )
                        else:
                            logger.debug(
                                "ARTICLE VIDEO NOT FOUND | %s",
                                url,
                            )

                        if not getattr(item, "image_url", "") and image:
                            item.image_url = image

                    except Exception:
                        logger.exception(
                            "Article media extraction failed: %s",
                            url,
                        )

            await asyncio.gather(
                *[
                    inspect_article(item, url)
                    for item, url in article_jobs
                ],
                return_exceptions=True,
            )

            logger.info(
                "RSS PARSED | %s | news=%s | article_pages_checked=%s",
                getattr(self.source, "name", "RSS"),
                len(news_items),
                len(article_jobs),
            )

            return news_items

        except Exception:
            logger.exception(
                "RSS fetch failed: %s",
                feed_url,
            )
            return []

    def _extract_category(self) -> str:
        categories = getattr(
            self.source,
            "categories",
            None,
        ) or []

        if isinstance(categories, str):
            return categories

        if categories:
            return str(categories[0])

        return "general"

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
    def _clean_text(value: Any) -> str:
        if not value:
            return ""

        if isinstance(value, list):
            value = " ".join(
                str(part) for part in value
            )

        soup = BeautifulSoup(str(value), "html.parser")

        return re.sub(
            r"\s+",
            " ",
            soup.get_text(" ", strip=True),
        ).strip()

    def _extract_content(self, entry) -> str:
        contents = entry.get("content", [])

        if contents:
            parts = []

            for item in contents:
                value = item.get("value", "")
                if value:
                    parts.append(
                        self._clean_text(value)
                    )

            if parts:
                return "\n".join(parts)

        return self._clean_text(
            entry.get("summary", "")
        )

    @staticmethod
    def _extract_published_at(entry) -> Optional[datetime]:
        for key in ("published_parsed", "updated_parsed"):
            parsed = entry.get(key)

            if parsed:
                try:
                    from time import mktime

                    return datetime.fromtimestamp(
                        mktime(parsed),
                        tz=timezone.utc,
                    )
                except (ValueError, OverflowError, OSError):
                    pass

        for key in ("published", "updated", "date"):
            value = entry.get(key)

            if not value:
                continue

            try:
                result = parsedate_to_datetime(value)

                if result.tzinfo is None:
                    result = result.replace(
                        tzinfo=timezone.utc
                    )

                return result
            except (TypeError, ValueError, OverflowError):
                continue

        return None

    def _extract_image_url(self, entry) -> Optional[str]:
        for key in ("media_thumbnail", "media_content"):
            for media in entry.get(key, []) or []:
                url = media.get("url")

                if url and self._looks_like_image(url, media):
                    return url

        for link in entry.get("links", []) or []:
            url = link.get("href", "")
            media_type = link.get("type", "").lower()
            rel = link.get("rel", "").lower()

            if (
                url
                and (
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
