"""
KhabarF24 Main Engine
Priority-based news selection with safe publishing.

اولویت انتشار: خبر فوری ← سیاست ← ایران ← ورزش ← جهان ← بقیه
(اقتصاد، فناوری، سلامت و ...). اولویت مطلق باعث می‌شد دسته‌های پایین
هیچ‌وقت نوبت نگیرند (سیاست همیشه خبر تازه دارد)، پس به‌جایش هر دسته
متناسب با اولویتش «سهم» از پست‌ها می‌گیرد (ROTATION)، و خبر فوری همیشه
خارج از نوبت اول می‌آید.
"""

import sys
import time
import random
import asyncio
import logging
import contextlib
from collections import defaultdict, deque
from itertools import zip_longest
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
MAX_CANDIDATES_PER_CYCLE = 60
MIN_GAP_BETWEEN_CANDIDATES = 3

# نتیجه‌ی ساخت‌یافته‌ی بازی‌ها (ESPN؛ و نام قدیمی API-Football)
MATCH_REPORT_SOURCE_IDS = ("espn_matches", "api_football")

# دسته‌ها از مهم به کم‌اهمیت. اگر دسته‌ی نوبت‌دار خبر تازه نداشت، سراغ
# اولین دسته‌ی بعدی (به همین ترتیب) می‌رویم.
TIER_PRIORITY = ("breaking", "politics", "iran", "sport", "general", "other")

# سهم هر دسته در ۱۲ پست متوالی (خبر فوری خارج از این نوبت‌ها است):
# سیاست ۴، ایران ۳، ورزش ۲، جهان ۲، بقیه ۱. برای عوض‌کردن سهم‌ها فقط
# تعداد تکرار هر اسم را در این فهرست تغییر بده.
ROTATION = (
    "politics", "iran", "politics", "sport", "general", "iran",
    "politics", "sport", "other", "iran", "politics", "general",
)


def classify_tier(news) -> str:
    """دسته‌ی اولویتِ یک خبر (بعد از تشخیص دسته و ورزش)."""

    if getattr(news, "is_breaking", False):
        return "breaking"

    category = str(getattr(news, "category", "") or "").lower()

    if category == "politics":
        return "politics"

    if category == "iran":
        return "iran"

    if category == "sport" or getattr(news, "sport", None):
        return "sport"

    if category in ("", "general", "world"):
        return "general"

    return "other"


def _is_persian(news) -> bool:
    return str(getattr(news, "language", "") or "").lower() == "fa"


def _interleave(first, second):
    merged = []

    for a, b in zip_longest(first, second):
        if a is not None:
            merged.append(a)
        if b is not None:
            merged.append(b)

    return merged


def order_tier(tier, items):
    """ترتیب خبرهای یک دسته."""

    items = list(items)
    random.shuffle(items)

    if tier == "breaking":
        items.sort(
            key=lambda n: getattr(n, "importance_score", 0) or 0,
            reverse=True,
        )
        return items

    # نتیجه‌ی ساخت‌یافته‌ی بازی‌ها همیشه اول
    reports = [
        n for n in items
        if getattr(n, "source_id", "") in MATCH_REPORT_SOURCE_IDS
    ]
    report_ids = {id(n) for n in reports}
    rest = [n for n in items if id(n) not in report_ids]

    # فارسی و غیرفارسی نوبتی، تا خبر منابع ایرانی هم دیده شود
    persian = [n for n in rest if _is_persian(n)]
    others = [n for n in rest if not _is_persian(n)]

    return reports + _interleave(persian, others)


class CandidatePicker:
    """کاندید بعدی را بر اساس اولویت و نوبت انتخاب می‌کند."""

    # بین چرخه‌ها حفظ می‌شود (تا ربات ری‌استارت نشده)
    rotation_index = 0

    def __init__(self, tiers):
        self.queues = {
            tier: deque(order_tier(tier, tiers.get(tier, [])))
            for tier in TIER_PRIORITY
        }

    def next(self):
        """(خبر، دسته) یا None وقتی خبری نمانده باشد."""

        if self.queues["breaking"]:
            return self.queues["breaking"].popleft(), "breaking"

        wanted = ROTATION[CandidatePicker.rotation_index % len(ROTATION)]

        if self.queues[wanted]:
            return self.queues[wanted].popleft(), wanted

        for tier in TIER_PRIORITY[1:]:
            if self.queues[tier]:
                return self.queues[tier].popleft(), tier

        return None

    @staticmethod
    def advance():
        """بعد از هر پست عادی، نوبت به دسته‌ی بعدی می‌رسد."""
        CandidatePicker.rotation_index += 1


@contextlib.contextmanager
def quiet_logs():
    """لاگ‌های INFO تشخیص‌دهنده‌ها را موقتاً خاموش می‌کند."""

    logging.disable(logging.INFO)

    try:
        yield
    finally:
        logging.disable(logging.NOTSET)


async def classify_all(pipeline, all_news):
    """
    رشته‌ی ورزشی، دسته و فوریت همه‌ی خبرها را «قبل از انتخاب» تعیین
    می‌کنیم تا بشود بر اساس آن‌ها اولویت داد. این مراحل سریع و محلی‌اند
    (بدون Gemini) و دوباره‌اجراشدنشان داخل pipeline همان نتیجه را می‌دهد.
    """

    detectors = [
        getattr(pipeline, name, None)
        for name in ("sport", "category", "importance")
    ]
    detectors = [d for d in detectors if d is not None]

    with quiet_logs():
        for news in all_news:
            for detector in detectors:
                try:
                    await detector.process(news)
                except Exception:
                    break


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

            match_reports = sum(
                1
                for item in all_news
                if getattr(item, "source_id", "") in MATCH_REPORT_SOURCE_IDS
            )
            logger.info(
                f"Fetched {len(all_news)} news "
                f"({match_reports} match reports)"
            )

            await classify_all(pipeline, all_news)

            tiers = defaultdict(list)

            for news in all_news:
                tiers[classify_tier(news)].append(news)

            persian_sport = sum(
                1 for n in tiers["sport"] if _is_persian(n)
            )
            logger.info(
                "Tiers: "
                + ", ".join(f"{t}={len(tiers[t])}" for t in TIER_PRIORITY)
                + f" | persian_sport={persian_sport}"
            )

            picker = CandidatePicker(tiers)

            published_count = 0
            processed_count = 0

            while (
                processed_count < MAX_CANDIDATES_PER_CYCLE
                and published_count < MAX_PUBLISH_PER_CYCLE
            ):
                picked = picker.next()

                if picked is None:
                    break

                news, tier = picked

                source = str(
                    getattr(news, "source", "Unknown") or "Unknown"
                )
                title = str(
                    getattr(news, "title", "") or ""
                )[:100]

                try:
                    result = await pipeline.process(news)
                    processed_count += 1

                    # Gemini در حال نوبت‌دهی یا بلوک سهمیه است؛ بقیه‌ی
                    # کاندیدهای این چرخه را بررسی نمی‌کنیم.
                    if getattr(result, "ai_paused", False):
                        logger.info(
                            "Gemini is pacing or paused; "
                            "ending this cycle early"
                        )
                        break

                    # تکراری‌ها Gemini مصرف نمی‌کنند؛ بدون مکث
                    if getattr(result, "is_duplicate", False):
                        logger.info(
                            "Skipped duplicate | source=%s | title=%s",
                            source,
                            title,
                        )
                        continue

                    if not getattr(result, "content_generated", False):
                        logger.info(
                            "Skipped: content not generated | "
                            "source=%s | title=%s",
                            source,
                            title,
                        )
                        await asyncio.sleep(MIN_GAP_BETWEEN_CANDIDATES)
                        continue

                    # این ویژگی در pipeline پس از ارسال تلگرام تنظیم می‌شود.
                    if getattr(result, "published", False):
                        published_count += 1

                        # فقط پست عادی نوبت را جلو می‌برد، نه خبر فوری
                        if tier != "breaking":
                            picker.advance()

                        logger.info(
                            "Successful publication: %s/%s | tier=%s",
                            published_count,
                            MAX_PUBLISH_PER_CYCLE,
                            tier,
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

                await asyncio.sleep(MIN_GAP_BETWEEN_CANDIDATES)

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
