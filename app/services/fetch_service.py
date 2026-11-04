"""
Fetch Service

مدیریت دریافت خبر از تمام منابع
"""

import asyncio
import time
from typing import List

from app.fetchers.rss_fetcher import RSSFetcher
from app.fetchers.website_fetcher import WebsiteFetcher
from app.fetchers.api_fetcher import APIFetcher
from app.fetchers.social_fetcher import SocialFetcher
from app.fetchers.sports_api_fetcher import SportsApiFetcher

from app.models.news_source import NewsSource
from app.models.raw_news import RawNews
from app.utils.logger import logger


# چند منبع هم‌زمان دریافت شوند. با ۱۰۰+ منبع، دریافت پشت‌سرهم هر چرخه
# چند دقیقه طول می‌کشید.
FETCH_CONCURRENCY = 10

# اگر یک منبع بیشتر از این گیر کرد، رد می‌شود و بقیه منتظر آن نمی‌مانند.
SOURCE_TIMEOUT_SECONDS = 90

# منابع غیرفعال فقط یک‌بار در لاگ نوشته می‌شوند (نه هر چرخه)
_logged_disabled = set()


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

    async def _fetch_limited(
        self,
        source: NewsSource,
        semaphore: asyncio.Semaphore,
    ) -> List[RawNews]:
        """دریافت یک منبع، با سقف هم‌زمانی و مهلت زمانی."""

        async with semaphore:
            try:
                return await asyncio.wait_for(
                    self.fetch_source(source),
                    timeout=SOURCE_TIMEOUT_SECONDS,
                )

            except asyncio.TimeoutError:
                logger.warning(
                    f"Fetch timeout ({SOURCE_TIMEOUT_SECONDS}s) for "
                    f"{source.name}; skipped this cycle"
                )
                return []

    async def fetch_all(
        self,
        sources: List[NewsSource],
    ) -> List[RawNews]:
        """
        دریافت خبر از تمام منابع (هم‌زمان، حداکثر FETCH_CONCURRENCY تا)
        """

        started = time.monotonic()

        enabled = []

        for source in sources:

            if getattr(source, "enabled", True):
                enabled.append(source)

            elif source.name not in _logged_disabled:
                _logged_disabled.add(source.name)
                logger.info(
                    f"Source disabled: {source.name}"
                )

        semaphore = asyncio.Semaphore(FETCH_CONCURRENCY)

        results = await asyncio.gather(
            *[
                self._fetch_limited(source, semaphore)
                for source in enabled
            ]
        )

        # ترتیب نتیجه‌ها همان ترتیب منابع است
        all_news: List[RawNews] = [
            item for batch in results for item in batch
        ]

        logger.info(
            f"Fetched {len(all_news)} news "
            f"from {len(enabled)} sources "
            f"in {time.monotonic() - started:.1f}s."
        )

        return all_news
