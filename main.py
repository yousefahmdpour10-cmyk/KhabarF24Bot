"""
KhabarF24 Main Engine
Priority-based news selection with safe publishing.

اولویت انتشار: خبر فوری ← سیاست ← ایران ← ورزش ← جهان ← بقیه
(اقتصاد، فناوری، سلامت و ...). اولویت مطلق باعث می‌شد دسته‌های پایین
هیچ‌وقت نوبت نگیرند (سیاست همیشه خبر تازه دارد)، پس به‌جایش هر دسته
متناسب با اولویتش «سهم» از پست‌ها می‌گیرد (ROTATION)، و خبر فوری همیشه
خارج از نوبت اول می‌آید.

داخل هر دسته، منابع نوبتی هستند (منبعی که اخیراً کمتر پست داشته جلوتر
است) و در هر منبع تازه‌ترین خبر اول می‌آید؛ تا یک منبع پرخبر (مثل
ورزش سه) جلوی بقیه (رومانو، BBC، Sky ...) را نگیرد.
"""

import sys
import time
import random
import asyncio
import logging
import contextlib
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
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

# منبعِ آخرین پست‌های منتشرشده؛ برای نوبت‌دادن به منابع
RECENT_SOURCES = deque(maxlen=60)

# نتیجه‌ی دسته‌بندی هر خبر؛ بیشتر خبرهای هر چرخه همان خبرهای چرخه‌ی قبل‌اند
# و دسته‌بندی ۲۶۰۰ خبر هر بار حدود ۲۰ ثانیه طول می‌کشید.
CLASSIFIED = {}
MAX_CLASSIFIED = 20000
CLASSIFIED_ATTRS = (
    "sport", "sport_name", "sport_emoji", "sport_hashtag", "league",
    "category", "importance_score", "is_breaking", "source_score",
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


def _source_key(news) -> str:
    return str(getattr(news, "source", "") or "Unknown")


def _timestamp(news) -> float:
    """زمان انتشار خبر (برای تازه‌ترین-اول)؛ نامشخص = ۰."""

    value = getattr(news, "published_at", None)

    if isinstance(value, datetime):
        try:
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.timestamp()
        except (ValueError, OverflowError, OSError):
            return 0.0

    return 0.0


def order_tier(tier, items):
    """ترتیب خبرهای یک دسته."""

    items = list(items)

    if tier == "breaking":
        items.sort(
            key=lambda n: (
                getattr(n, "importance_score", 0) or 0,
                _timestamp(n),
            ),
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

    # گروه‌بندی بر اساس منبع؛ در هر منبع تازه‌ترین خبر اول
    groups = defaultdict(list)

    for news in rest:
        groups[_source_key(news)].append(news)

    for group in groups.values():
        group.sort(key=_timestamp, reverse=True)

    # منبعی که اخیراً کمتر پست داشته جلوتر است (بین برابرها تصادفی)
    names = list(groups)
    random.shuffle(names)
    recent = Counter(RECENT_SOURCES)
    names.sort(key=lambda name: recent[name])

    # نوبتی از منبع‌ها: یکی از هر منبع، بعد دور دوم و ...
    merged = [
        news
        for row in zip_longest(*(groups[name] for name in names))
        for news in row
        if news is not None
    ]

    return reports + merged


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


def _classify_key(news) -> str:
    url = str(getattr(news, "url", "") or "")

    if url:
        return url

    return f"{_source_key(news)}|{getattr(news, 'title', '')}"


async def classify_all(pipeline, all_news):
    """
    رشته‌ی ورزشی، دسته و فوریت همه‌ی خبرها را «قبل از انتخاب» تعیین
    می‌کنیم تا بشود بر اساس آن‌ها اولویت داد. این مراحل سریع و محلی‌اند
    (بدون Gemini) و دوباره‌اجراشدنشان داخل pipeline همان نتیجه را می‌دهد.
    نتیجه‌ی هر خبر در CLASSIFIED نگه داشته می‌شود تا خبری که قبلاً
    دسته‌بندی شده دوباره پردازش نشود.
    """

    detectors = [
        getattr(pipeline, name, None)
        for name in ("sport", "category", "importance")
    ]
    detectors = [d for d in detectors if d is not None]

    with quiet_logs():
        for news in all_news:
            key = _classify_key(news)
            cached = CLASSIFIED.get(key)

            if cached is not None:
                for attr, value in cached.items():
                    setattr(news, attr, value)
                continue

            for detector in detectors:
                try:
                    await detector.process(news)
                except Exception:
                    break

            if len(CLASSIFIED) >= MAX_CLASSIFIED:
                CLASSIFIED.pop(next(iter(CLASSIFIED)))

            CLASSIFIED[key] = {
                attr: getattr(news, attr)
                for attr in CLASSIFIED_ATTRS
                if hasattr(news, attr)
            }


def _top(counter: Counter, limit: int = 12) -> str:
    return ", ".join(f"{k}={v}" for k, v in counter.most_common(limit))


async def main():
    logger.info("KhabarF24 Bot Started Successfully")

    start_time = time.monotonic()
    fetch_service = FetchService()
    pipeline = NewsPipeline()
    sources = load_sources()

    logger.info(f"Loaded {len(sources)} sources")

    api_sources = [
        src for src in sources
        if str(getattr(src, "source_type", "")).lower()
        in ("sports_api", "sports-api", "sportsapi")
    ]
    logger.info(
        "Match-report sources: "
        + (
            ", ".join(
                f"{src.name} (enabled={getattr(src, 'enabled', True)})"
                for src in api_sources
            )
            or "NONE - match reports are disabled (add data/sources/sports_api.json)"
        )
    )

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
            logger.info(
                "Sport tier sources: "
                + _top(Counter(_source_key(n) for n in tiers["sport"]))
            )

            generic_sport = [
                n for n in tiers["sport"] if not getattr(n, "sport", None)
            ]
            if generic_sport:
                logger.info(
                    "Sport category without a specific sport: "
                    + " | ".join(
                        f"{_source_key(n)}: {str(getattr(n, 'title', ''))[:50]}"
                        for n in generic_sport[:8]
                    )
                )

            picker = CandidatePicker(tiers)

            published_count = 0
            processed_count = 0
            stats = Counter()
            published_by_tier = Counter()
            rejected_sources = Counter()

            while (
                processed_count < MAX_CANDIDATES_PER_CYCLE
                and published_count < MAX_PUBLISH_PER_CYCLE
            ):
                picked = picker.next()

                if picked is None:
                    break

                news, tier = picked

                source = _source_key(news)
                title = str(
                    getattr(news, "title", "") or ""
                )[:100]

                try:
                    result = await pipeline.process(news)
                    processed_count += 1

                    # Gemini در حال نوبت‌دهی یا بلوک سهمیه است؛ بقیه‌ی
                    # کاندیدهای این چرخه را بررسی نمی‌کنیم.
                    if getattr(result, "ai_paused", False):
                        stats["ai_paused"] += 1
                        logger.info(
                            "Gemini is pacing or paused; "
                            "ending this cycle early"
                        )
                        break

                    # تکراری‌ها Gemini مصرف نمی‌کنند؛ بدون مکث
                    if getattr(result, "is_duplicate", False):
                        stats["duplicates"] += 1
                        logger.info(
                            "Skipped duplicate | source=%s | title=%s",
                            source,
                            title,
                        )
                        continue

                    # خبر بی‌محتوا (مثل «N12») برای همیشه رد شد؛ بدون مکث
                    if getattr(result, "junk_content", False):
                        stats["junk"] += 1
                        logger.info(
                            "Skipped: not enough content | "
                            "source=%s | title=%s",
                            source,
                            title,
                        )
                        continue

                    if not getattr(result, "content_generated", False):
                        if getattr(result, "is_verified", True) is False:
                            stats["low_credibility"] += 1
                            rejected_sources[source] += 1
                        else:
                            stats["content_failed"] += 1

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
                        published_by_tier[tier] += 1
                        RECENT_SOURCES.append(source)

                        # فقط پست عادی نوبت را جلو می‌برد، نه خبر فوری
                        if tier != "breaking":
                            picker.advance()

                        logger.info(
                            "Successful publication: %s/%s | tier=%s | source=%s",
                            published_count,
                            MAX_PUBLISH_PER_CYCLE,
                            tier,
                            source,
                        )
                    else:
                        stats["publish_failed"] += 1
                        logger.warning(
                            "Not counted as published | "
                            "source=%s | title=%s",
                            source,
                            title,
                        )

                except Exception:
                    stats["errors"] += 1
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
                f"published={published_count} "
                f"({_top(published_by_tier) or 'none'}), "
                f"duplicates={stats['duplicates']}, "
                f"low_credibility={stats['low_credibility']}, "
                f"junk={stats['junk']}, "
                f"content_failed={stats['content_failed']}, "
                f"publish_failed={stats['publish_failed']}, "
                f"ai_paused={stats['ai_paused']}"
            )

            if rejected_sources:
                logger.info(
                    "Rejected for low credibility: " + _top(rejected_sources)
                )

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception:
            logger.exception("Cycle failed")
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
