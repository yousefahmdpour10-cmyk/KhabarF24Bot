"""
RSS Fetcher

دریافت خبر از منابع RSS
"""

import feedparser
from datetime import datetime
from typing import List, Optional

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.http_client import HTTPClient


class RSSFetcher(BaseFetcher):
    """
    دریافت خبر از RSS
    """

    def __init__(self, source):
        super().__init__(source)
        self.http = HTTPClient()

    async def fetch(self) -> List[RawNews]:
        """
        دریافت خبرها از RSS
        """

        news_list: List[RawNews] = []

        # استفاده از rss_url در مدل جدید NewsSource
        # و حفظ سازگاری با مدل قبلی که از url استفاده می‌کرد.
        rss_url = getattr(self.source, "rss_url", None) or self.source.url

        if not rss_url:
            return news_list

        xml = await self.http.get(rss_url)

        if not xml:
            return news_list

        feed = feedparser.parse(xml)

        if feed.bozo:
            print(f"RSS Error: {self.source.name}")

        for entry in feed.entries:

            try:

                news = RawNews(
                    source_id=self.source.id,
                    source=self.source.name,

                    title=getattr(
                        entry,
                        "title",
                        ""
                    ) or "",

                    content=self._extract_content(entry),

                    summary=getattr(
                        entry,
                        "summary",
                        ""
                    ) or "",

                    url=getattr(
                        entry,
                        "link",
                        ""
                    ) or "",

                    published_at=self._extract_published_at(entry),

                    language=self.source.language,

                    category=(
                        self.source.categories[0]
                        if getattr(
                            self.source,
                            "categories",
                            None
                        )
                        else ""
                    ),

                    image_url=self._extract_image_url(entry),

                    raw_data=dict(entry),

                    tags=list(
                        getattr(
                            entry,
                            "tags",
                            []
                        ) or []
                    ),
                )

                news_list.append(news)

            except Exception as e:

                print(
                    f"Error parsing news from "
                    f"{self.source.name}: {e}"
                )

        return news_list

    @staticmethod
    def _extract_content(entry) -> str:
        """
        استخراج متن اصلی خبر از RSS.

        بعضی RSSها متن خبر را در content
        و بعضی در summary قرار می‌دهند.
        """

        content = getattr(
            entry,
            "content",
            None
        )

        if content:
            try:
                if isinstance(content, list):
                    for item in content:
                        value = item.get("value", "")
                        if value:
                            return value
            except Exception:
                pass

        return (
            getattr(
                entry,
                "summary",
                ""
            )
            or ""
        )

    @staticmethod
    def _extract_published_at(entry) -> Optional[datetime]:
        """
        تبدیل تاریخ RSS به datetime.

        feedparser معمولاً تاریخ را در
        published_parsed یا updated_parsed
        به شکل time.struct_time قرار می‌دهد.
        """

        parsed_time = getattr(
            entry,
            "published_parsed",
            None
        )

        if not parsed_time:
            parsed_time = getattr(
                entry,
                "updated_parsed",
                None
            )

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
            except Exception:
                pass

        return None

    @staticmethod
    def _extract_image_url(entry) -> Optional[str]:
        """
        تلاش برای پیدا کردن آدرس عکس خبر از فرمت‌های رایج RSS
        (media:thumbnail, media:content, enclosure).
        """

        media_thumbnail = getattr(
            entry,
            "media_thumbnail",
            None
        )

        if media_thumbnail:
            url = media_thumbnail[0].get("url")

            if url:
                return url

        media_content = getattr(
            entry,
            "media_content",
            None
        )

        if media_content:
            url = media_content[0].get("url")

            if url:
                return url

        for link in getattr(
            entry,
            "links",
            []
        ):

            if (
                link.get("rel") == "enclosure"
                and str(
                    link.get("type", "")
                ).startswith("image")
            ):

                url = link.get("href")

                if url:
                    return url

        return None
