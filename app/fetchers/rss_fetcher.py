"""
RSS Fetcher

دریافت خبر از منابع RSS
"""

import feedparser
from typing import List

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

                if await self.validate(news):
                    news = await self.normalize(news)
                    news_list.append(news)

            except Exception as e:

                print(
                    f"Error parsing news from {self.source.name}: {e}"
                )

        return news_list
