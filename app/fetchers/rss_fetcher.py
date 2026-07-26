"""
دریافت اخبار از RSS
"""

import feedparser
from typing import List

from app.fetchers.base_fetcher import BaseFetcher
from app.models.news import News


class RSSFetcher(BaseFetcher):
    """
    دریافت اخبار از RSS
    """

    async def fetch(self) -> List[News]:

        feed = feedparser.parse(self.source.url)

        news_list = []

        for entry in feed.entries:

            news = News(
                title=entry.get("title", ""),
                summary=entry.get("summary", ""),
                url=entry.get("link", ""),
                source=self.source.name,
                category=self.source.categories[0] if self.source.categories else "",
            )

            if await self.validate(news):
                news = await self.normalize(news)
                news_list.append(news)

        return news_list
