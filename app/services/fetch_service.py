"""
Fetch Service

مدیریت دریافت خبر از تمام منابع
"""

from typing import List

from app.fetchers.rss_fetcher import RSSFetcher
from app.fetchers.website_fetcher import WebsiteFetcher
from app.fetchers.api_fetcher import APIFetcher
from app.fetchers.social_fetcher import SocialFetcher
from app.fetchers.sports_api_fetcher import SportsApiFetcher

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
            source_type = (
                getattr(source, "source_type", "")
                or ""
            ).lower().strip()

            # ==================================================
            # RSS
            # ==================================================

            if source_type == "rss":

                fetcher = RSSFetcher(source)

            # ==================================================
            # Website
            # ==================================================

            elif source_type == "website":

                fetcher = WebsiteFetcher(source)

            # ==================================================
            # Sports API
            # ==================================================

            elif source_type in (
                "sports_api",
                "sports-api",
                "sportsapi",
            ):

                fetcher = SportsApiFetcher(source)

            # ==================================================
            # General API
            # ==================================================

            elif source_type == "api":

                fetcher = APIFetcher(source)

            # ==================================================
            # Social
            # ==================================================

            elif source_type == "social":

                fetcher = SocialFetcher(source)

            # ==================================================
            # Fallback برای منابع قدیمی
            # ==================================================

            elif getattr(source, "has_rss", False):

                logger.warning(
                    f"{source.name}: source_type is not 'rss'. "
                    f"Using RSS fallback."
                )

                fetcher = RSSFetcher(source)

            elif getattr(source, "has_api", False):

                logger.warning(
                    f"{source.name}: source_type is not 'api'. "
                    f"Using API fallback."
                )

                fetcher = APIFetcher(source)

            elif getattr(source, "supports_scraping", False):

                logger.warning(
                    f"{source.name}: source_type is not 'website'. "
                    f"Using website fallback."
                )

                fetcher = WebsiteFetcher(source)

            else:

                logger.warning(
                    f"No fetcher available for {source.name}"
                )

                return []

            return await fetcher.fetch()

        except Exception as e:

            logger.exception(
                f"Fetch error for {source.name}: {e}"
            )

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

            if not getattr(source, "enabled", True):
                logger.info(
                    f"Source disabled: {source.name}"
                )
                continue

            news = await self.fetch_source(source)

            all_news.extend(news)

        logger.info(
            f"Fetched {len(all_news)} news "
            f"from {len(sources)} sources."
        )

        return all_news
