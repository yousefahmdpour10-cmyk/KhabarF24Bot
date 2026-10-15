"""
RSS Fetcher

دریافت خبرها از RSS، همراه با استخراج تصویر و ویدئوی مستقیم.
"""

import feedparser
from datetime import datetime
from typing import List, Optional, Tuple

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.http_client import HTTPClient


class RSSFetcher(BaseFetcher):
    """دریافت خبر از RSS."""

    def __init__(self, source):
        super().__init__(source)
        self.http = HTTPClient()

    async def fetch(self) -> List[RawNews]:
        news_list: List[RawNews] = []

        rss_url = (
            getattr(self.source, "rss_url", None)
            or self.source.url
        )

        if not rss_url:
            print(f"RSS URL MISSING: {self.source.name}")
            return news_list

        try:
            xml = await self.http.get(rss_url)
        except Exception as exc:
            print(
                f"RSS FETCH ERROR: {self.source.name} | "
                f"url={rss_url} | error={exc}"
            )
            return news_list

        if not xml:
            print(
                f"RSS FETCH FAILED: {self.source.name} | "
                f"url={rss_url} | response is empty"
            )
            return news_list

        try:
            feed = feedparser.parse(xml)
        except Exception as exc:
            print(
                f"RSS PARSE ERROR: {self.source.name} | error={exc}"
            )
            return news_list

        if feed.bozo:
            print(
                f"RSS PARSE WARNING: {self.source.name} | "
                f"{getattr(feed, 'bozo_exception', 'unknown error')}"
            )

        source_categories = list(
            getattr(self.source, "categories", None) or []
        )

        print(
            f"RSS RESULT: {self.source.name} | "
            f"entries={len(feed.entries)} | url={rss_url}"
        )

        for entry in feed.entries:
            try:
                video_url, video_type = self._extract_video(entry)

                news = RawNews(
                    source_id=self.source.id,
                    source=self.source.name,
                    source_category_hint=source_categories,
                    title=getattr(entry, "title", "") or "",
                    content=self._extract_content(entry),
                    summary=getattr(entry, "summary", "") or "",
                    url=getattr(entry, "link", "") or "",
                    published_at=self._extract_published_at(entry),
                    language=self.source.language,
                    category=(
                        source_categories[0]
                        if source_categories
                        else ""
                    ),
                    image_url=self._extract_image_url(entry),
                    video_url=video_url or "",
                    video_content_type=video_type or "",
                    raw_data=dict(entry),
                    tags=list(getattr(entry, "tags", []) or []),
                )

                if not news.title and not news.content and not news.url:
                    continue

                news_list.append(news)

            except Exception as exc:
                print(
                    f"RSS ENTRY ERROR: {self.source.name} | error={exc}"
                )

        print(
            f"RSS PARSED: {self.source.name} | news={len(news_list)}"
        )
        return news_list

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
    def _extract_published_at(entry) -> Optional[datetime]:
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
    def _extract_image_url(entry) -> Optional[str]:
        for field in ("media_thumbnail", "media_content"):
            items = getattr(entry, field, None) or []
            for item in items:
                if not isinstance(item, dict):
                    continue

                url = item.get("url")
                media_type = str(item.get("type", "")).lower()

                if url and (
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

    @staticmethod
    def _extract_video(entry) -> Tuple[Optional[str], Optional[str]]:
        """
        فقط لینک‌هایی را برمی‌گرداند که RSS آن‌ها را به‌عنوان
        ویدئو یا فایل رسانه‌ای ویدئویی معرفی کرده باشد.
        """

        candidates = []

        for field in ("media_content", "media_thumbnail"):
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

            is_video = (
                media_type.startswith("video/")
                or medium == "video"
                or (
                    rel == "enclosure"
                    and media_type in (
                        "application/mp4",
                        "application/x-mpegurl",
                    )
                )
            )

            if is_video:
                return url, media_type

        return None, None
