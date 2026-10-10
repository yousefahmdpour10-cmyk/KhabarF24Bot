"""
Sports API Client (api-football.com)

پلن رایگان: ۱۰۰ درخواست در روز (ریست ساعت ۰۰:۰۰ UTC) و ۱۰ درخواست در دقیقه.
برای همین همه‌ی درخواست‌ها از یک شمارنده‌ی مشترک عبور می‌کنند و بین
درخواست‌ها فاصله‌ی زمانی رعایت می‌شود.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import aiohttp

from config import settings
from app.utils.logger import logger

BASE_URL = "https://v3.football.api-sports.io"

FOLLOWED_LEAGUES: Dict[int, str] = {
    39: "Premier League",
    140: "La Liga",
    135: "Serie A",
    78: "Bundesliga",
    61: "Ligue 1",
    2: "Champions League",
    3: "Europa League",
}

FREE_DAILY_LIMIT = 100
DAILY_REQUEST_CAP = 90          # ۱۰ درخواست ذخیره برای اطمینان
REQUEST_SPACING_SECONDS = 6.5   # زیر سقف ۱۰ درخواست در دقیقه

# شمارنده‌ی مشترک بین همه‌ی نمونه‌ها (هر چرخه یک نمونه‌ی جدید ساخته می‌شود)
_usage = {"day": "", "count": 0}
_last_request_at: float = 0.0


def budget_left() -> int:
    """تعداد درخواست‌های باقی‌مانده‌ی امروز (UTC)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if _usage["day"] != today:
        _usage["day"] = today
        _usage["count"] = 0
    return DAILY_REQUEST_CAP - _usage["count"]


class SportsApiClient:

    def __init__(self):
        self.api_key = getattr(settings, "SPORTS_API_KEY", "")

    async def _get(self, path: str, params: dict) -> Optional[dict]:
        global _last_request_at

        if not self.api_key:
            logger.error("SportsApiClient: SPORTS_API_KEY تنظیم نشده است")
            return None

        if budget_left() <= 0:
            logger.warning("SportsApiClient: سقف درخواست امروز پر شده است")
            return None

        wait = REQUEST_SPACING_SECONDS - (time.monotonic() - _last_request_at)
        if wait > 0:
            await asyncio.sleep(wait)

        _last_request_at = time.monotonic()
        _usage["count"] += 1

        headers = {"x-apisports-key": self.api_key}

        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
            ) as session:
                async with session.get(
                    f"{BASE_URL}{path}", params=params
                ) as response:

                    # شمارنده‌ی واقعیِ سرور را با شمارنده‌ی خودمان هماهنگ
                    # می‌کنیم (ری‌استارت ربات شمارنده‌ی ما را صفر می‌کند،
                    # ولی مصرف واقعی امروز روی سرور باقی می‌ماند).
                    remaining = response.headers.get(
                        "x-ratelimit-requests-remaining"
                    )
                    if remaining is not None:
                        try:
                            used = FREE_DAILY_LIMIT - int(remaining)
                            _usage["count"] = max(_usage["count"], used)
                            logger.info(
                                f"SportsApiClient: باقی‌مانده امروز طبق سرور = {remaining}"
                            )
                        except ValueError:
                            pass

                    if response.status != 200:
                        body = await response.text()
                        logger.error(
                            f"SportsApiClient HTTP {response.status} -> {body[:300]}"
                        )
                        return None

                    data = await response.json()

                    errors = data.get("errors")
                    if errors:
                        logger.error(f"SportsApiClient API error -> {errors}")
                        if isinstance(errors, dict) and "requests" in errors:
                            _usage["count"] = DAILY_REQUEST_CAP
                        return None

                    return data

        except Exception as e:
            logger.error(f"SportsApiClient error -> {e}")

        return None

    async def get_finished_fixtures(self, date: str) -> List[dict]:
        """
        همه‌ی بازی‌های تمام‌شده‌ی یک تاریخ (UTC) را با «یک» درخواست
        می‌گیرد و خودمان فقط لیگ‌های دنبال‌شده را نگه می‌داریم.
        """

        data = await self._get(
            "/fixtures",
            {"date": date, "status": "FT-AET-PEN"},
        )

        if not data:
            return []

        results: List[dict] = []
        total = 0

        for item in data.get("response", []):
            total += 1
            league_id = (item.get("league") or {}).get("id")
            if league_id in FOLLOWED_LEAGUES:
                item["_league_name"] = FOLLOWED_LEAGUES[league_id]
                results.append(item)

        logger.info(
            f"SportsApiClient: {date} -> {total} بازی تمام‌شده در دنیا، "
            f"{len(results)} بازی در لیگ‌های دنبال‌شده"
        )

        return results

    async def get_fixture_events(self, fixture_id: int) -> List[dict]:

        data = await self._get(
            "/fixtures/events",
            {"fixture": fixture_id},
        )

        if not data:
            return []

        return data.get("response", [])
