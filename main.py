"""
KhabarF24 Main Engine
Balanced news selection with sports priority and safe publishing.
"""

import sys
import time
import random
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import CHECK_INTERVAL
from config.sources import load_sources
from app.services.fetch_service import FetchService
from app.processors.pipeline import NewsPipeline
from app.utils.logger import logger


MAX_RUNTIME_SECONDS = 5 * 3600 + 50 * 60
MAX_PUBLISH_PER_CYCLE = 3
MAX_CANDIDATES_PER_CYCLE = 50
SPORTS_CANDIDATE_TARGET = 20
MIN_GAP_BETWEEN_CANDIDATES = 3


SPORTS_SOURCE_KEYWORDS = (
    "bbc sport",
    "bbc football",
    "espn soccer",
    "gianluca di marzio",
    "di marzio",
    "transfermarkt",
    "fabrizio romano",
    "sky sports football",
    "uefa",
    "fifa",
    "premier league",
    "api-football",
)

SPORTS_CATEGORY_KEYWORDS = (
    "sport",
    "football",
    "soccer",
    "basketball",
    "volleyball",
    "tennis",
    "transfer",
    "premier_league",
    "champions_league",
    "europa_league",
)


def is_sports_candidate(news):
    source = str(getattr(news, "source", "") or "").lower()
    category = str(getattr(news, "category", "") or "").lower()

    return (
        any(word in source for word in SPORTS_SOURCE_KEYWORDS)
        or any(word in category for word in SPORTS_CATEGORY_KEYWORDS)
    )


def select_candidates(all_news):
    if not all_news:
        return []

    sports_news = []
    other_news = []

    for news in all_news:
        if is_sports_candidate(news):
            sports_news.append(news)
        else:
            other_news.append(news)

    random.shuffle(sports_news)
    random.shuffle(other_news)

    limit = min(MAX_CANDIDATES_PER_CYCLE, len(all_news))
    sports_target = min(
        SPORTS_CANDIDATE_TARGET,
        len(sports_news),
        limit,
    )

    sports_news = sports_news[:sports_target]
    remaining_slots = limit - len(sports_news)
    other_news = other_news[:remaining_slots]

    # نوبتی: یک خبر ورزشی، سپس یک خبر عمومی.
    # خبرهای باقی‌مانده هم در انتهای فهرست قرار می‌گیرند.
    selected = []
    sport_index = 0
    other_index = 0

    while len(selected) < limit:
        if sport_index < len(sports_news):
            selected.append(sports_news[sport_index])
            sport_index += 1

        if len(selected) >= limit:
            break

        if other_index < len(other_news):
            selected.append(other_news[other_index])
            other_index += 1

        if (
            sport_index >= len(sports_news)
            and other_index >= len(other_news)
        ):
            break

    logger.info(
        "Candidate selection: "
        f"{len(sports_news)} sports, "
        f"{len(other_news)} general, "
        f"{len(selected)} selected"
    )

    return selected


async def main():
    logger.info("KhabarF24 Bot Started Successfully")

    start_time = time.monotonic()
    fetch_service = FetchService()
    pipeline = NewsPipeline()
    sources = load_sources()

    logger.info(f"Loaded {len(sources)} sources")

    while True:
        if time.monotonic() - start_time > MAX_RUNTIME_SECONDS:
            logger.info("Maximum runtime reached; exiting cleanly")
            break

        try:
            logger.info("Checking for new news...")

            all_news = await fetch_service.fetch_all(sources)
            logger.info(f"Fetched {len(all_news)} news")

            candidates = select_candidates(all_news)

            published_count = 0
            processed_count = 0

            for news in candidates:
                if published_count >= MAX_PUBLISH_PER_CYCLE:
                    break

                source = str(
                    getattr(news, "source", "Unknown") or "Unknown"
                )
                title = str(
                    getattr(news, "title", "") or ""
                )[:100]

                try:
                    result = await pipeline.process(news)
                    processed_count += 1

                    if getattr(result, "is_duplicate", False):
                        logger.info(
                            "Skipped duplicate | source=%s | title=%s",
                            source,
                            title,
                        )
                        await asyncio.sleep(
                            MIN_GAP_BETWEEN_CANDIDATES
                        )
                        continue

                    if not getattr(result, "content_generated", False):
                        logger.info(
                            "Skipped: content not generated | "
                            "source=%s | title=%s",
                            source,
                            title,
                        )
                        await asyncio.sleep(
                            MIN_GAP_BETWEEN_CANDIDATES
                        )
                        continue

                    # این ویژگی باید در pipeline پس از ارسال تلگرام تنظیم شود.
                    if getattr(result, "published", False):
                        published_count += 1
                        logger.info(
                            "Successful publication: %s/%s",
                            published_count,
                            MAX_PUBLISH_PER_CYCLE,
                        )
                    else:
                        logger.warning(
                            "Not counted as published | "
                            "source=%s | title=%s",
                            source,
                            title,
                        )

                except Exception:
                    logger.exception(
                        "Candidate failed; continuing | "
                        "source=%s | title=%s",
                        source,
                        title,
                    )

                await asyncio.sleep(
                    MIN_GAP_BETWEEN_CANDIDATES
                )

            logger.info(
                "Cycle finished: "
                f"processed={processed_count}, "
                f"published={published_count}"
            )

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception:
            logger.exception("Cycle failed")
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
