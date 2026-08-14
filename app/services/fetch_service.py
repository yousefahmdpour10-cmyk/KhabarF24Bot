# app/services/fetch_service.py

"""
Fetch Service

مدیریت دریافت خبر از تمام منابع
"""

from typing import List

from app.fetchers.rss_fetcher import RSSFetcher
from app.fetchers.website_fetcher import WebsiteFetcher
from app.models.news_source import NewsSource
from app.models.raw_news import RawNews
from app.utils.logger import logger


class FetchService:
    """
    سرویس دریافت خبر
    """

    async def fetch_source(
        self,
        source: NewsSource,
    ) -> List[RawNews]:
        """
        دریافت خبر از یک منبع
        """

        logger.info(f"Fetching: {source.name}")

        try:

            if source.has_rss:

                fetcher = RSSFetcher(source)

            elif source.supports_scraping:

                fetcher = WebsiteFetcher(source)

            else:

                logger.warning(
                    f"No fetcher available for {source.name}"
                )

                return []

            return await fetcher.fetch()

        except Exception as e:

            logger.exception(e)

            return []

    async def fetch_all(
        self,
        sources: List[NewsSource],
    ) -> List[RawNews]:
        """
        دریافت خبر از تمام منابع
        """

        all_news: List[RawNews] = []

        for source in sources:

            news = await self.fetch_source(source)

            all_news.extend(news)

        logger.info(
            f"Fetched {len(all_news)} news from {len(sources)} sources."
        )

        return all_news
