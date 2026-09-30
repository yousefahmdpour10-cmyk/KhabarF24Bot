"""
RSS Fetcher

دریافت خبر از منابع RSS
"""

import feedparser
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

        xml = await self.http.get(self.source.url)

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
                    title=getattr(entry, "title", ""),
                    summary=getattr(entry, "summary", ""),
                    url=getattr(entry, "link", ""),
                    published_at=getattr(entry, "published", ""),
                    language=self.source.language,
                )

                news.source_category_hint = getattr(
                    self.source, "categories", None
                )

                news.image_url = self._extract_image_url(entry)

                news_list.append(news)

            except Exception as e:

                print(
                    f"Error parsing news from {self.source.name}: {e}"
                )

        return news_list

    @staticmethod
    def _extract_image_url(entry) -> Optional[str]:
        """
        تلاش برای پیدا کردن آدرس عکس خبر از فرمت‌های رایج RSS
        (media:thumbnail, media:content, enclosure).
        """

        media_thumbnail = getattr(entry, "media_thumbnail", None)
        if media_thumbnail:
            url = media_thumbnail[0].get("url")
            if url:
                return url

        media_content = getattr(entry, "media_content", None)
        if media_content:
            url = media_content[0].get("url")
            if url:
                return url

        for link in getattr(entry, "links", []):
            if link.get("rel") == "enclosure" and str(
                link.get("type", "")
            ).startswith("image"):
                url = link.get("href")
                if url:
                    return url

        return None
