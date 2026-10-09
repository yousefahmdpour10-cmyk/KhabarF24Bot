```python
"""
KhabarF24 Main Engine
Balanced news selection with dedicated sports coverage.
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

# سهمیه‌ی اولیه برای بررسی خبرهای ورزشی
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
    """
    Identify likely sports candidates using source/category metadata.
    Actual sport classification remains the SportDetector's responsibility.
    """

    source = str(getattr(news, "source", "") or "").lower()
    category = str(getattr(news, "category", "") or "").lower()

    if any(keyword in source for keyword in SPORTS_SOURCE_KEYWORDS):
        return True

    if any(keyword in category for keyword in SPORTS_CATEGORY_KEYWORDS):
        return True

    return False


def select_candidates(all_news):
    """
    Give sports-related sources a fair chance without excluding other news.
    Select from the complete fetched collection before filling remaining slots.
    """

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

    selected = sports_news[:sports_target]
    remaining_slots = limit - len(selected)

    selected.extend(other_news[:remaining_slots])

    # اگر خبرهای غیرورزشی برای پر کردن سهمیه کافی نبودند،
    # خبرهای ورزشی باقی‌مانده را هم وارد فهرست کن.
    if len(selected) < limit:
        selected_ids = {id(news) for news in selected}

        remaining_news = [
            news
            for news in sports_news + other_news
            if id(news) not in selected_ids
        ]

        random.shuffle(remaining_news)
        selected.extend(remaining_news[:limit - len(selected)])

    random.shuffle(selected)

    logger.info(
        "Candidate selection: "
        f"{len(sports_news)} sports-related, "
        f"{len(other_news)} other, "
        f"{len(selected)} selected"
    )

    logger.info(
        "Sports candidates selected: "
        f"{sum(1 for news in selected if is_sports_candidate(news))}"
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
            logger.info(
                "Max runtime reached, exiting cleanly for next scheduled run"
            )
            break

        try:
            logger.info("Checking for new news...")

            all_news = await fetch_service.fetch_all(sources)

            logger.info(f"Fetched {len(all_news)} news")

            candidates = select_candidates(all_news)

            publish_attempts = 0
            processed_count = 0

            for news in candidates:
                if publish_attempts >= MAX_PUBLISH_PER_CYCLE:
                    break

                result = await pipeline.process(news)
                processed_count += 1

                if getattr(result, "is_duplicate", False):
                    await asyncio.sleep(MIN_GAP_BETWEEN_CANDIDATES)
                    continue

                if not getattr(result, "content_generated", False):
                    await asyncio.sleep(MIN_GAP_BETWEEN_CANDIDATES)
                    continue

                # فعلاً سقف تلاش‌های انتشار را حفظ می‌کنیم.
                # برای تشخیص قطعی موفقیت ارسال، باید Pipeline نیز
                # وضعیت واقعی انتشار را روی نتیجه ثبت کند.
                publish_attempts += 1

                await asyncio.sleep(5)

            logger.info(
                "Cycle finished: "
                f"processed={processed_count}, "
                f"publish_slots_used={publish_attempts}"
            )

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
```
    
