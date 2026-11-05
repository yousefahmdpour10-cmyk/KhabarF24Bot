"""
ESPN Client

API عمومی و بدون کلید ESPN (site.api.espn.com). حساب و ثبت‌نام ندارد،
پس مشکل تحریم یا تعلیق حساب هم ندارد. این API غیررسمی است و ESPN
ممکن است ساختارش را بدون اطلاع قبلی تغییر دهد.
"""

import asyncio
import time
from collections import Counter
from typing import Dict, List, Optional

import aiohttp

from app.utils.logger import logger

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer"

# slug لیگ در ESPN -> اسم لیگ (اسم‌ها با LEAGUE_TAGS در hashtags.py یکی است)
FOLLOWED_LEAGUES: Dict[str, str] = {
    "eng.1": "Premier League",
    "esp.1": "La Liga",
    "ita.1": "Serie A",
    "ger.1": "Bundesliga",
    "fra.1": "Ligue 1",
    "uefa.champions": "Champions League",
    "uefa.europa": "Europa League",
    "uefa.europa.conf": "Conference League",
}

# سقف رسمی منتشر نشده؛ برای مؤدب بودن بین درخواست‌ها فاصله می‌گذاریم
REQUEST_SPACING_SECONDS = 0.6

# تلاش مجدد برای پاسخ‌های موقتی (۲۰۲ معمولاً سد ضد‌ربات یا «بعداً بیا» است)
RETRYABLE_STATUSES = {202, 429, 500, 502, 503, 504}
MAX_ATTEMPTS = 3

# User-Agent ربات‌مانند (compatible; ...Bot) را سدهای ضد‌ربات زودتر
# می‌بندند؛ همان مرورگر معمولی که برای RSS هم استفاده می‌شود.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

_last_request_at: float = 0.0

# شمارنده‌ی نتیجه‌ی درخواست‌ها: ok, http_<کد>, error (برای گزارش در لاگ)
STATS: Counter = Counter()

# بدنه‌ی پاسخ ناموفق را برای هر کد فقط یک‌بار در لاگ می‌نویسیم
_body_logged = set()


class EspnClient:

    async def _get(self, url: str, params: Optional[dict] = None) -> Optional[dict]:
        global _last_request_at

        for attempt in range(1, MAX_ATTEMPTS + 1):

            wait = REQUEST_SPACING_SECONDS - (time.monotonic() - _last_request_at)
            if wait > 0:
                await asyncio.sleep(wait)

            _last_request_at = time.monotonic()

            try:
                timeout = aiohttp.ClientTimeout(total=20)
                async with aiohttp.ClientSession(
                    timeout=timeout,
                    headers=HEADERS,
                ) as session:
                    async with session.get(url, params=params) as response:

                        if response.status == 200:
                            STATS["ok"] += 1
                            return await response.json(content_type=None)

                        status = response.status
                        STATS[f"http_{status}"] += 1

                        if status not in _body_logged:
                            _body_logged.add(status)
                            try:
                                body = (await response.text())[:150]
                            except Exception:
                                body = ""
                            logger.warning(
                                f"EspnClient HTTP {status} -> {url} | "
                                f"body: {body!r}"
                            )

                        if status not in RETRYABLE_STATUSES:
                            return None

            except Exception as e:
                STATS["error"] += 1
                logger.warning(f"EspnClient error -> {url} -> {e}")

            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(2 * attempt)

        return None

    async def get_scoreboard(self, league_slug: str, date: str) -> List[dict]:
        """
        بازی‌های یک لیگ در یک روز. date به شکل YYYYMMDD.
        """

        data = await self._get(
            f"{BASE_URL}/{league_slug}/scoreboard",
            {"dates": date},
        )

        if not data:
            return []

        return data.get("events") or []

    async def get_summary(self, league_slug: str, event_id: str) -> Optional[dict]:
        """گزارش کامل یک بازی (ترکیب، آمار، رویدادها، داور)."""

        return await self._get(
            f"{BASE_URL}/{league_slug}/summary",
            {"event": event_id},
                            )
