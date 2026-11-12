"""
KhabarF24 Main Engine
Priority-based news selection with safe publishing.

ساختار:
- دو حلقه‌ی «دریافت» جدا از هم می‌چرخند: یکی برای ESPN (نتیجه و ترکیب
  بازی‌ها، هر ۲ دقیقه)، یکی برای بقیه‌ی منابع (۲۰۰+ منبع، هر چند دقیقه که
  تمام شود). هر دو خبرها را در یک «استخر» می‌ریزند و دسته‌بندی هم همان‌جا
  انجام می‌شود.
- حلقه‌ی «انتشار» هر CHECK_INTERVAL ثانیه از استخر برمی‌دارد و منتظر
  دریافت نمی‌ماند. قبلاً دریافت و انتشار پشت‌سرهم بودند: با ۲۰۰+ منبع هر
  چرخه ده‌ها دقیقه طول می‌کشید و پست‌های وقت‌دار (ترکیب و نتیجه) دیر
  می‌رسیدند.

اولویت انتشار: خبر فوری ← پست وقت‌دار (ترکیب/نتیجه‌ی بازی، حداکثر ۲ تا
پشت‌سرهم) ← سیاست ← ایران ← ورزش ← جهان ← بقیه. اولویت مطلق باعث می‌شد
دسته‌های پایین هیچ‌وقت نوبت نگیرند، پس هر دسته متناسب با اولویتش «سهم»
می‌گیرد (ROTATION). داخل هر دسته، منابع نوبتی هستند و در هر منبع
تازه‌ترین خبر اول می‌آید.
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

# فاصله‌ی شروع دو دریافت پشت‌سرهم (ثانیه). اگر یک دریافت از این بیشتر
# طول بکشد، دریافت بعدی بعد از MIN_FETCH_PAUSE شروع می‌شود.
LIVE_FETCH_INTERVAL = 120
FEEDS_FETCH_INTERVAL = 180
MIN_FETCH_PAUSE = 30

# خبری که تولیدش خراب شد، این‌قدر کنار می‌ماند (ثانیه). وگرنه یک خبر
# همیشه‌خراب (مثلاً JSON نامعتبر Gemini) هر چرخه سهمیه‌ی Gemini را می‌سوزاند و
# چون وقت‌دار است جلوتر از همه می‌ایستد.
FAIL_COOLDOWN_SECONDS = 600
FAILED_UNTIL = {}

# دسته‌بندی در بسته‌های این‌قدری انجام می‌شود تا حلقه‌ی انتشار گرسنه نماند
CLASSIFY_BATCH = 100

SPORTS_API_TYPES = ("sports_api", "sports-api", "sportsapi")

# نتیجه‌ی ساخت‌یافته‌ی بازی‌ها (ESPN؛ و نام قدیمی API-Football)
MATCH_REPORT_SOURCE_IDS = ("espn_matches", "api_football")

# دسته‌ها از مهم به کم‌اهمیت. اگر دسته‌ی نوبت‌دار خبر تازه نداشت، سراغ
# اولین دسته‌ی بعدی (به همین ترتیب) می‌رویم.
TIER_PRIORITY = (
    "breaking", "timely", "politics", "iran", "sport", "general", "other",
)

# پست‌های «وقت‌دار» (ترکیب قبل از بازی، نتیجه‌ی بعد از بازی) زودتر از بقیه
# می‌آیند، ولی بعد از این‌قدر پست وقت‌دار پشت‌سرهم یک پست عادی نوبت
# می‌گیرد تا شب‌های پربازی (لیگ قهرمانان) بقیه‌ی خبرها گرسنه نمانند.
TIMELY_MAX_STREAK = 2

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
CLASSIFIED = {}
MAX_CLASSIFIED = 30000
CLASSIFIED_ATTRS = (
    "sport", "sport_name", "sport_emoji", "sport_hashtag", "league",
    "category", "importance_score", "is_breaking", "source_score",
)


def classify_tier(news) -> str:
    """دسته‌ی اولویتِ یک خبر (بعد از تشخیص دسته و ورزش)."""

    if getattr(news, "is_breaking", False):
        return "breaking"

    if getattr(news, "timely", False):
        return "timely"

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

    if tier == "timely":
        # ترکیب قبل از بازی (بازی نزدیک‌تر اول)، بعد نتیجه‌ی تازه‌ترین بازی
        items.sort(key=lambda n: getattr(n, "timely_key", (2, 0)))
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
    timely_streak = 0

    def __init__(self, tiers):
        self.queues = {
            tier: deque(order_tier(tier, tiers.get(tier, [])))
            for tier in TIER_PRIORITY
        }

    def next(self):
        """(خبر، دسته) یا None وقتی خبری نمانده باشد."""

        if self.queues["breaking"]:
            return self.queues["breaking"].popleft(), "breaking"

        if (
            self.queues["timely"]
            and CandidatePicker.timely_streak < TIMELY_MAX_STREAK
        ):
            return self.queues["timely"].popleft(), "timely"

        wanted = ROTATION[CandidatePicker.rotation_index % len(ROTATION)]

        if self.queues[wanted]:
            return self.queues[wanted].popleft(), wanted

        # دسته‌ی نوبت‌دار خبر تازه نداشت: اول بقیه‌ی دسته‌ها به ترتیب اولویت
        # (وقت‌دار را کنار می‌گذاریم، وگرنه سقف پشت‌سرهم دور زده می‌شود)
        for tier in TIER_PRIORITY:
            if tier in ("breaking", "timely"):
                continue

            if self.queues[tier]:
                return self.queues[tier].popleft(), tier

        # خبر عادی‌ای نمانده: پست وقت‌دارِ باقی‌مانده سقف را ندارد
        if self.queues["timely"]:
            return self.queues["timely"].popleft(), "timely"

        return None

    @staticmethod
    def advance():
        """بعد از هر پست عادی، نوبت به دسته‌ی بعدی می‌رسد."""
        CandidatePicker.rotation_index += 1


# ----------------------------------------------------------------------
# استخر خبر و حلقه‌ی دریافت
# ----------------------------------------------------------------------

class NewsPool:
    """خبرهای دریافت‌شده. حلقه‌ی دریافت می‌نویسد، حلقه‌ی انتشار می‌خواند."""

    def __init__(self):
        self.groups = {}

    def update(self, group, items):
        # یک دریافت خالیِ «فیدها» معمولاً خطای موقت شبکه است؛ خبرهای قبلی
        # را نگه می‌داریم. گروه «live» (ESPN) همیشه تازه می‌شود، چون
        # پست‌های وقت‌دارِ منقضی باید از استخر بیرون بروند.
        if items or group == "live":
            self.groups[group] = list(items)

    def has_data(self):
        return any(self.groups.values())

    def snapshot(self):
        return [item for items in self.groups.values() for item in items]


def split_sources(sources):
    """(منابع ESPN، بقیه‌ی منابع)."""

    live = [
        s for s in sources
        if str(getattr(s, "source_type", "")).lower() in SPORTS_API_TYPES
    ]
    live_ids = {id(s) for s in live}
    feeds = [s for s in sources if id(s) not in live_ids]

    return live, feeds


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
    (بدون Gemini). نتیجه‌ی هر خبر در CLASSIFIED نگه داشته می‌شود.

    در بسته‌های CLASSIFY_BATCH تایی کار می‌کند و بین بسته‌ها به حلقه‌ی
    انتشار نوبت می‌دهد. توجه: داخل یک بسته هیچ await واقعی نیست، پس
    خاموش‌بودن لاگ (quiet_logs) به حلقه‌ی دیگر نشت نمی‌کند.
    """

    detectors = [
        getattr(pipeline, name, None)
        for name in ("sport", "category", "importance")
    ]
    detectors = [d for d in detectors if d is not None]

    for start in range(0, len(all_news), CLASSIFY_BATCH):

        with quiet_logs():
            for news in all_news[start:start + CLASSIFY_BATCH]:
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

        await asyncio.sleep(0)


async def fetch_loop(fetch_service, pipeline, sources, pool, group, interval):
    """یک گروه از منابع را مدام دریافت و دسته‌بندی می‌کند و در استخر می‌ریزد."""

    while True:
        started = time.monotonic()

        try:
            items = await fetch_service.fetch_all(sources)
            await classify_all(pipeline, items)
            pool.update(group, items)

            logger.info(
                f"Fetch loop [{group}]: {len(items)} news from "
                f"{len(sources)} sources in {time.monotonic() - started:.0f}s"
            )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(f"Fetch loop [{group}] failed")

        elapsed = time.monotonic() - started
        await asyncio.sleep(max(MIN_FETCH_PAUSE, interval - elapsed))


def _top(counter: Counter, limit: int = 12) -> str:
    return ", ".join(f"{k}={v}" for k, v in counter.most_common(limit))


# ----------------------------------------------------------------------
# حلقه‌ی انتشار
# ----------------------------------------------------------------------

async def publish_cycle(pipeline, all_news):
    """یک چرخه‌ی انتشار از خبرهای آماده‌ی استخر."""

    match_reports = sum(
        1
        for item in all_news
        if getattr(item, "source_id", "") in MATCH_REPORT_SOURCE_IDS
    )
    logger.info(
        f"Pool: {len(all_news)} news ({match_reports} match posts)"
    )

    tiers = defaultdict(list)

    for news in all_news:
        tiers[classify_tier(news)].append(news)

    persian_sport = sum(1 for n in tiers["sport"] if _is_persian(n))
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
        title = str(getattr(news, "title", "") or "")[:100]
        key = _classify_key(news)

        # خبری که تولیدش به‌تازگی خراب شد، فعلاً کنار می‌ماند
        if time.monotonic() < FAILED_UNTIL.get(key, 0):
            stats["cooling"] += 1
            continue

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
                    "Skipped: not enough content | source=%s | title=%s",
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
                    FAILED_UNTIL[key] = (
                        time.monotonic() + FAIL_COOLDOWN_SECONDS
                    )

                logger.info(
                    "Skipped: content not generated | source=%s | title=%s",
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

                # پست وقت‌دار سهم خودش را دارد؛ خبر فوری هم نوبت
                # را جلو نمی‌برد. فقط پست عادی نوبت را جلو می‌برد.
                if tier == "timely":
                    CandidatePicker.timely_streak += 1
                elif tier != "breaking":
                    CandidatePicker.timely_streak = 0
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
                FAILED_UNTIL[key] = time.monotonic() + FAIL_COOLDOWN_SECONDS
                logger.warning(
                    "Not counted as published | source=%s | title=%s",
                    source,
                    title,
                )

        except Exception:
            stats["errors"] += 1
            logger.exception(
                "Candidate failed; continuing | source=%s | title=%s",
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
        f"cooling={stats['cooling']}, "
        f"publish_failed={stats['publish_failed']}, "
        f"ai_paused={stats['ai_paused']}"
    )

    if rejected_sources:
        logger.info(
            "Rejected for low credibility: " + _top(rejected_sources)
        )

    return processed_count, published_count


async def main(max_cycles=None):
    logger.info("KhabarF24 Bot Started Successfully")

    deadline = time.monotonic() + MAX_RUNTIME_SECONDS
    fetch_service = FetchService()
    pipeline = NewsPipeline()
    sources = load_sources()

    logger.info(f"Loaded {len(sources)} sources")

    live, feeds = split_sources(sources)

    logger.info(
        "Match-report sources: "
        + (
            ", ".join(
                f"{src.name} (enabled={getattr(src, 'enabled', True)})"
                for src in live
            )
            or "NONE - match reports are disabled (add data/sources/sports_api.json)"
        )
    )

    pool = NewsPool()
    tasks = []

    if live:
        tasks.append(
            asyncio.create_task(
                fetch_loop(
                    fetch_service, pipeline, live, pool,
                    "live", LIVE_FETCH_INTERVAL,
                )
            )
        )

    if feeds:
        tasks.append(
            asyncio.create_task(
                fetch_loop(
                    fetch_service, pipeline, feeds, pool,
                    "feeds", FEEDS_FETCH_INTERVAL,
                )
            )
        )

    try:
        # اولین خبرها که رسید (معمولاً اول ESPN) انتشار شروع می‌شود؛
        # منتظر تمام‌شدن دریافت ۲۰۰ منبع نمی‌مانیم.
        while not pool.has_data():
            if time.monotonic() > deadline or all(t.done() for t in tasks):
                break

            await asyncio.sleep(0.2)

        cycles = 0

        while time.monotonic() < deadline:
            try:
                await publish_cycle(pipeline, pool.snapshot())

            except Exception:
                logger.exception("Cycle failed")
                await asyncio.sleep(30)

            cycles += 1

            if max_cycles is not None and cycles >= max_cycles:
                break

            await asyncio.sleep(CHECK_INTERVAL)

        if time.monotonic() >= deadline:
            logger.info("Maximum runtime reached; exiting cleanly")

    finally:
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
