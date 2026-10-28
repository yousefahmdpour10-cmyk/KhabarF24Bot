"""
KhabarF24 Main Engine
Priority-based news selection with sports support and safe publishing.
"""

import sys
import time
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import CHECK_INTERVAL
from config.sources import load_sources
from app.services.fetch_service import FetchService
from app.processors.pipeline import NewsPipeline
from app.utils.logger import logger


# تنظیمات اجرای ربات
MAX_RUNTIME_SECONDS = 5 * 3600 + 50 * 60
MAX_PUBLISH_PER_CYCLE = 3
MAX_CANDIDATES_PER_CYCLE = 50
MIN_GAP_BETWEEN_CANDIDATES = 3

MATCH_REPORT_SOURCE_IDS = (
    "espn_matches",
    "api_football",
)


# اولویت دسته‌های خبری
CATEGORY_PRIORITY = {
    "breaking": 100,
    "urgent": 100,
    "breaking_news": 100,
    "politics": 90,
    "iran": 80,
    "sport": 70,
    "sports": 70,
    "football": 70,
    "world": 60,
    "international": 60,
    "economy": 50,
    "business": 50,
    "finance": 50,
    "technology": 40,
    "tech": 40,
    "science": 40,
    "general": 30,
}

# کلیدواژه‌های خبر فوری
BREAKING_KEYWORDS = (
    "breaking news",
    "breaking:",
    "just in:",
    "urgent:",
    "خبر فوری",
    "فوری:",
    "خبر اضطراری",
    "فوق العاده",
    "خبر فوری:",
)

# کلیدواژه‌های سیاست
POLITICS_KEYWORDS = (
    "politics",
    "political",
    "president",
    "parliament",
    "government",
    "election",
    "minister",
    "senate",
    "diplomacy",
    "sanctions",
    "سیاست",
    "سیاسی",
    "رئیس جمهور",
    "رئیس‌جمهور",
    "دولت",
    "مجلس",
    "انتخابات",
    "وزیر",
    "تحریم",
    "دیپلماسی",
)

# کلیدواژه‌های ایران
IRAN_KEYWORDS = (
    "iran",
    "iranian",
    "tehran",
    "ایران",
    "ایرانی",
    "تهران",
)

# کلیدواژه‌های جهان
WORLD_KEYWORDS = (
    "world",
    "international",
    "global",
    "جهان",
    "بین الملل",
    "بین‌الملل",
)

# کلیدواژه‌های اقتصاد
ECONOMY_KEYWORDS = (
    "economy",
    "economic",
    "business",
    "finance",
    "market",
    "inflation",
    "اقتصاد",
    "اقتصادی",
    "بازار",
    "تورم",
    "بورس",
    "ارز",
)

# کلیدواژه‌های تکنولوژی
TECH_KEYWORDS = (
    "technology",
    "tech",
    "artificial intelligence",
    "ai news",
    "cybersecurity",
    "science",
    "تکنولوژی",
    "فناوری",
    "هوش مصنوعی",
    "علم و فناوری",
)

# نشانه‌های منابع ورزشی
SPORTS_SOURCE_KEYWORDS = (
    "bbc sport",
    "bbc football",
    "espn",
    "gianluca di marzio",
    "di marzio",
    "transfermarkt",
    "fabrizio romano",
    "sky sports",
    "uefa",
    "fifa",
    "premier league",
    "api-football",
)

SPORTS_CATEGORY_KEYWORDS = (
    "sport",
    "sports",
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


def normalize_text(value):
    """تبدیل مقدار ورودی به متن قابل بررسی."""

    return str(value or "").strip().casefold()


def is_sports_candidate(news):
    """تشخیص احتمالی خبر ورزشی از اطلاعات موجود."""

    source = normalize_text(
        getattr(news, "source", "")
    )

    source_id = normalize_text(
        getattr(news, "source_id", "")
    )

    category = normalize_text(
        getattr(news, "category", "")
    )

    sport = normalize_text(
        getattr(news, "sport", "")
    )

    if sport:
        return True

    if any(
        keyword in source
        for keyword in SPORTS_SOURCE_KEYWORDS
    ):
        return True

    if any(
        keyword in source_id
        for keyword in SPORTS_CATEGORY_KEYWORDS
    ):
        return True

    if any(
        keyword in category
        for keyword in SPORTS_CATEGORY_KEYWORDS
    ):
        return True

    return False


def get_news_priority(news):
    """
    محاسبه اولویت اولیه خبر پیش از اجرای Pipeline.

    این تابع از دسته موجود، راهنمای دسته منبع،
    عنوان و خلاصه استفاده می‌کند.
    """

    title = normalize_text(
        getattr(news, "title", "")
    )

    summary = normalize_text(
        getattr(news, "summary", "")
    )

    text = f"{title} {summary}"

    category = normalize_text(
        getattr(news, "category", "")
    )

    source_categories = (
        getattr(news, "source_category_hint", []) or []
    )

    if isinstance(source_categories, str):
        source_categories = [source_categories]

    source_categories = [
        normalize_text(item)
        for item in source_categories
    ]

    # اولویت فوری فقط با نشانه صریح در عنوان
    # یا دسته‌ای که از قبل مشخص شده باشد.
    if category in ("breaking", "urgent", "breaking_news"):
        return 100

    if any(
        keyword in title
        for keyword in BREAKING_KEYWORDS
    ):
        return 100

    # دسته خبر یا راهنمای دسته منبع
    categories = [category] + source_categories

    priority = max(
        (
            CATEGORY_PRIORITY.get(item, 0)
            for item in categories
        ),
        default=0,
    )

    # اگر دسته هنوز مشخص نیست، از متن کمک بگیر.
    # این تشخیص اولیه است و جای CategoryDetector را نمی‌گیرد.
    if priority == 0:

        if any(
            keyword in text
            for keyword in POLITICS_KEYWORDS
        ):
            priority = max(priority, 90)

        if any(
            keyword in text
            for keyword in IRAN_KEYWORDS
        ):
            priority = max(priority, 80)

        if any(
            keyword in text
            for keyword in WORLD_KEYWORDS
        ):
            priority = max(priority, 60)

        if any(
            keyword in text
            for keyword in ECONOMY_KEYWORDS
        ):
            priority = max(priority, 50)

        if any(
            keyword in text
            for keyword in TECH_KEYWORDS
        ):
            priority = max(priority, 40)

    # ورزش از تشخیص موجود یا منبع ورزشی
    if is_sports_candidate(news):
        priority = max(priority, 70)

    # خبرهای مهم ورزشی، در صورت وجود نتیجه ساخت‌یافته
    if (
        getattr(news, "source_id", "")
        in MATCH_REPORT_SOURCE_IDS
    ):
        priority = max(priority, 70)

    return priority or CATEGORY_PRIORITY["general"]


def select_candidates(all_news):
    """انتخاب و مرتب‌سازی خبرها بر اساس اولویت."""

    if not all_news:
        return []

    # مرتب‌سازی پایدار:
    # امتیاز بالاتر جلوتر است؛ در امتیاز برابر،
    # ترتیب اولیه منابع حفظ می‌شود.
    selected = sorted(
        all_news,
        key=get_news_priority,
        reverse=True,
    )

    selected = selected[:MAX_CANDIDATES_PER_CYCLE]

    sports_count = sum(
        1
        for news in selected
        if is_sports_candidate(news)
    )

    urgent_count = sum(
        1
        for news in selected
        if get_news_priority(news) == 100
    )

    logger.info(
        "Priority selection | "
        "urgent=%s | sports=%s | selected=%s",
        urgent_count,
        sports_count,
        len(selected),
    )

    return selected


async def main():
    logger.info("KhabarF24 Bot Started Successfully")

    start_time = time.monotonic()

    fetch_service = FetchService()
    pipeline = NewsPipeline()
    sources = load_sources()

    logger.info("Loaded %s sources", len(sources))

    while True:

        if (
            time.monotonic() - start_time
            > MAX_RUNTIME_SECONDS
        ):
            logger.info(
                "Maximum runtime reached; exiting cleanly"
            )
            break

        try:
            logger.info("Checking for new news...")

            all_news = await fetch_service.fetch_all(sources)

            match_reports = sum(
                1
                for item in all_news
                if getattr(item, "source_id", "")
                in MATCH_REPORT_SOURCE_IDS
            )

            logger.info(
                "Fetched %s news (%s match reports)",
                len(all_news),
                match_reports,
            )

            candidates = select_candidates(all_news)

            published_count = 0
            processed_count = 0

            for news in candidates:

                if published_count >= MAX_PUBLISH_PER_CYCLE:
                    break

                source = str(
                    getattr(news, "source", "Unknown")
                    or "Unknown"
                )

                title = str(
                    getattr(news, "title", "") or ""
                )[:100]

                priority = get_news_priority(news)

                logger.info(
                    "Processing candidate | priority=%s | "
                    "source=%s | title=%s",
                    priority,
                    source,
                    title,
                )

                try:
                    result = await pipeline.process(news)
                    processed_count += 1

                    # اگر پردازش هوش مصنوعی متوقف یا محدود شده،
                    # این چرخه را زودتر تمام کن.
                    if getattr(result, "ai_paused", False):
                        logger.info(
                            "Gemini is pacing or paused; "
                            "ending this cycle early"
                        )
                        break

                    if getattr(result, "is_duplicate", False):
                        logger.info(
                            "Skipped duplicate | source=%s | "
                            "title=%s",
                            source,
                            title,
                        )

                        await asyncio.sleep(
                            MIN_GAP_BETWEEN_CANDIDATES
                        )
                        continue

                    if not getattr(
                        result,
                        "content_generated",
                        False,
                    ):
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
                "Cycle finished: processed=%s, published=%s",
                processed_count,
                published_count,
            )

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception:
            logger.exception("Cycle failed")
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
