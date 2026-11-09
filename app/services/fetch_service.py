"""
Fetch Service

مدیریت دریافت خبر از تمام منابع
"""

import asyncio
import time
from collections import Counter
from typing import List

from app.fetchers.rss_fetcher import RSSFetcher
from app.fetchers.website_fetcher import WebsiteFetcher
from app.fetchers.api_fetcher import APIFetcher
from app.fetchers.social_fetcher import SocialFetcher
from app.fetchers.sports_api_fetcher import SportsApiFetcher

from app.models.news_source import NewsSource
from app.models.raw_news import RawNews
from app.utils.logger import logger


# ==========================================================
# تنظیمات
# ==========================================================

FETCH_CONCURRENCY = 10
SOURCE_TIMEOUT_SECONDS = 90

_logged_disabled = set()


class FetchService:
    async def fetch_source(self, source: NewsSource) -> List[RawNews]:
        logger.info(f"Fetching: {source.name}")

        try:
            source_type = (
                getattr(source, "source_type", "") or ""
            ).lower().strip()

            # --------------------------------------------------
            # RSS
            # --------------------------------------------------
            if source_type == "rss":
                fetcher = RSSFetcher(source)

            # --------------------------------------------------
            # Website
            # --------------------------------------------------
            elif source_type == "website":
                fetcher = WebsiteFetcher(source)

            # --------------------------------------------------
            # Sports API
            # --------------------------------------------------
            elif source_type in (
                "sports_api",
                "sports-api",
                "sportsapi",
            ):
                fetcher = SportsApiFetcher(source)

            # --------------------------------------------------
            # Generic API
            # --------------------------------------------------
            elif source_type == "api":
                fetcher = APIFetcher(source)

            # --------------------------------------------------
            # Social
            # --------------------------------------------------
            elif source_type == "social":
                fetcher = SocialFetcher(source)

            # --------------------------------------------------
            # Fallback: RSS
            # --------------------------------------------------
            elif getattr(source, "has_rss", False):
                logger.warning(
                    f"{source.name}: source_type is not 'rss'. "
                    f"Using RSS fallback."
                )
                fetcher = RSSFetcher(source)

            # --------------------------------------------------
            # Fallback: API
            # --------------------------------------------------
            elif getattr(source, "has_api", False):
                logger.warning(
                    f"{source.name}: source_type is not 'api'. "
                    f"Using API fallback."
                )
                fetcher = APIFetcher(source)

            # --------------------------------------------------
            # Fallback: Website
            # --------------------------------------------------
            elif getattr(source, "supports_scraping", False):
                logger.warning(
                    f"{source.name}: source_type is not 'website'. "
                    f"Using website fallback."
                )
                fetcher = WebsiteFetcher(source)

            # --------------------------------------------------
            # No fetcher
            # --------------------------------------------------
            else:
                logger.warning(
                    f"No fetcher available for {source.name}"
                )
                return []

            # --------------------------------------------------
            # Execute fetcher
            # --------------------------------------------------
            items = await fetcher.fetch()

            return self._postprocess(source, items)

        except Exception as e:
            logger.exception(
                f"Fetch error for {source.name}: {e}"
            )
            return []

    # ==========================================================
    # Post Process
    # ==========================================================

    @staticmethod
    def _postprocess(
        source: NewsSource,
        items: List[RawNews],
    ) -> List[RawNews]:

        categories = list(
            getattr(source, "categories", []) or []
        )

        # ------------------------------------------------------
        # Add source category hints
        # ------------------------------------------------------
        for item in items:
            if not getattr(
                item,
                "source_category_hint",
                None,
            ):
                item.source_category_hint = list(categories)

        # ------------------------------------------------------
        # Remove repeated image/avatar/logo
        # ------------------------------------------------------
        if len(items) >= 4:

            counts = Counter(
                item.image_url
                for item in items
                if getattr(item, "image_url", "")
            )

            for url, count in counts.items():

                if (
                    count >= 4
                    and count / len(items) >= 0.3
                ):

                    for item in items:
                        if item.image_url == url:
                            item.image_url = ""

                    logger.info(
                        f"{source.name}: عکس تکراری در "
                        f"{count} خبر حذف شد "
                        f"(آواتار یا لوگو): {url[:80]}"
                    )

        return items

    # ==========================================================
    # Limited Fetch
    # ==========================================================

    async def _fetch_limited(
        self,
        source,
        semaphore,
    ):
        async with semaphore:

            try:
                return await asyncio.wait_for(
                    self.fetch_source(source),
                    timeout=SOURCE_TIMEOUT_SECONDS,
                )

            except asyncio.TimeoutError:

                logger.warning(
                    f"Fetch timeout "
                    f"({SOURCE_TIMEOUT_SECONDS}s) "
                    f"for {source.name}; "
                    f"skipped this cycle"
                )

                return []

    # ==========================================================
    # Fetch All Sources
    # ==========================================================

    async def fetch_all(self, sources):

        started = time.monotonic()

        enabled = []

        # ------------------------------------------------------
        # Filter enabled sources
        # ------------------------------------------------------
        for source in sources:

            if getattr(source, "enabled", True):

                enabled.append(source)

            elif source.name not in _logged_disabled:

                _logged_disabled.add(source.name)

                logger.info(
                    f"Source disabled: {source.name}"
                )

        # ------------------------------------------------------
        # DEBUG: Football360
        # ------------------------------------------------------
        logger.info(
            f"DEBUG FETCH_ALL | "
            f"enabled_sources={len(enabled)}"
        )

        football360_in_enabled = [
            source
            for source in enabled
            if (
                "football360"
                in str(
                    getattr(source, "id", "")
                ).lower()
                or
                "football360"
                in str(
                    getattr(source, "name", "")
                ).lower()
            )
        ]

        logger.info(
            "DEBUG FETCH_ALL | "
            "Football360 in enabled list = "
            f"{len(football360_in_enabled)}"
        )

        for source in football360_in_enabled:

            logger.info(
                "DEBUG FETCH_ALL | "
                "Football360 task candidate | "
                f"id={source.id} | "
                f"name={source.name} | "
                f"type={source.source_type} | "
                f"enabled={source.enabled} | "
                f"platform="
                f"{getattr(source, 'social_platform', '')}"
            )

        # ------------------------------------------------------
        # Semaphore
        # ------------------------------------------------------
        semaphore = asyncio.Semaphore(
            FETCH_CONCURRENCY
        )

        # ------------------------------------------------------
        # Create fetch tasks
        # ------------------------------------------------------
        tasks = [
            self._fetch_limited(
                source,
                semaphore,
            )
            for source in enabled
        ]

        logger.info(
            "DEBUG FETCH_ALL | "
            f"tasks_created={len(tasks)}"
        )

        # ------------------------------------------------------
        # Execute all fetch tasks
        # ------------------------------------------------------
        results = await asyncio.gather(
            *tasks
        )

        # ------------------------------------------------------
        # Flatten results
        # ------------------------------------------------------
        all_news = [
            item
            for batch in results
            for item in batch
        ]

        # ------------------------------------------------------
        # Final log
        # ------------------------------------------------------
        logger.info(
            f"Fetched {len(all_news)} news "
            f"from {len(enabled)} sources "
            f"in "
            f"{time.monotonic() - started:.1f}s."
        )

        return all_news
