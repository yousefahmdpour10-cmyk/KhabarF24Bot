"""
ESPN Check

بررسی مستقل بخش «نتیجه‌ی بازی‌ها»، بدون Gemini و بدون تلگرام.
در چند ثانیه نشان می‌دهد:
- تنظیمات (sources.json و اعتبار منبع ESPN) درست است یا نه؛
- ESPN برای هر لیگ چند بازی و چند بازی تمام‌شده برمی‌گرداند؛
- پستِ ساخته‌شده برای چند بازی دقیقاً چه چیزهایی (ترکیب، گل، کارت،
  آمار، داور و ...) دارد و چه چیزهایی ندارد.

اجرا:  python tools/espn_check.py
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(file).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.fetchers.sports_api_fetcher import SportsApiFetcher
from app.formatter.hashtags import HashtagBuilder
from app.formatter.sports.football.builder import FootballBuilder
from app.services.sports_api_client import EspnClient, FOLLOWED_LEAGUES

DAYS_BACK = 3
MAX_SHOW = 3
SPORTS_API_TYPES = ("sports_api", "sports-api", "sportsapi")


class _Source:
    name = "ESPN Matches"
    categories = ["sport", "football"]


def heading(text: str) -> None:
    print(f"\n======== {text} ========")


def check_config() -> None:
    heading("۱) تنظیمات")

    try:
        from config.sources import load_sources

        sources = load_sources()
        espn = [
            s for s in sources
            if str(getattr(s, "source_type", "")).lower() in SPORTS_API_TYPES
        ]

        print(f"منابع بارگذاری‌شده: {len(sources)}")

        if not espn:
            print("!! هیچ منبعی با source_type=sports_api پیدا نشد "
                  "=> fetcher ESPN هرگز اجرا نمی‌شود")

        for s in espn:
            enabled = getattr(s, "enabled", True)
            print(f"منبع ESPN: name={s.name} enabled={enabled}"
                  + ("   !! غیرفعال است" if not enabled else ""))

    except Exception as exc:
        print("!! خواندن sources ناموفق:", repr(exc))

    try:
        from app.processors.credibility.source_reputation import (
            SOURCE_REPUTATION,
        )

        score = SOURCE_REPUTATION.get("ESPN")
        verdict = "OK" if score and score >= 70 else "!! کمتر از ۷۰ یا ناموجود: خبرها رد می‌شوند"
        print(f"اعتبار منبع 'ESPN': {score}  {verdict}")

    except Exception as exc:
        print("!! خواندن source_reputation ناموفق:", repr(exc))

    try:
        from app.formatter.source_flags import get_flag

        print("پرچم منبع 'ESPN':", get_flag("ESPN"))

    except Exception as exc:
        print("!! خواندن source_flags ناموفق:", repr(exc))


async def collect_finished(client: EspnClient) -> list:
    heading("۲) بازی‌های تمام‌شده از ESPN")

    now = datetime.now(timezone.utc)
    dates = [
        (now - timedelta(days=i)).strftime("%Y%m%d")
        for i in range(DAYS_BACK)
    ]
    print("تاریخ‌های بررسی‌شده (UTC):", ", ".join(dates))

    found = []

    for slug, league in FOLLOWED_LEAGUES.items():
        total = finished = 0

        for date in dates:
            events = await client.get_scoreboard(slug, date)
            total += len(events)

            for event in events:
                data = SportsApiFetcher._extract(event, league)

                if data:
                    finished += 1
                    found.append((slug, data))

        print(f"{league:20} بازی={total:3}  تمام‌شده={finished:3}")

    print(f"\nمجموع بازی تمام‌شده: {len(found)}")

    return found


def pick_varied(found: list) -> list:
    """اول از هر لیگ یک بازی، بعد بقیه، تا سقف MAX_SHOW."""

    picked, leagues = [], set()

    for item in found:
        if item[1]["league"] not in leagues:
            picked.append(item)
            leagues.add(item[1]["league"])

    for item in found:
        if item not in picked:
            picked.append(item)

    return picked[:MAX_SHOW]


async def show_matches(client: EspnClient, found: list) -> None:
    heading("۳) پست ساخته‌شده برای چند بازی")

    fetcher = SportsApiFetcher(_Source())
    coverage = {"lineup": 0, "goals": 0, "assists": 0,
                "cards": 0, "stats": 0, "referee": 0}
    shown = 0
