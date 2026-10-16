"""
ESPN Client

API عمومی و بدون کلید ESPN (site.api.espn.com). حساب و ثبت‌نام ندارد،
پس مشکل تحریم یا تعلیق حساب هم ندارد. این API غیررسمی است و ESPN
ممکن است ساختارش را بدون اطلاع قبلی تغییر دهد.
"""

import asyncio
import time
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; KhabarF24Bot/1.0)",
    "Accept": "application/json",
}

_last_request_at: float = 0.0


class EspnClient:

    async def _get(self, url: str, params: Optional[dict] = None) -> Optional[dict]:
        global _last_request_at

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

                    if response.status != 200:
                        logger.warning(
                            f"EspnClient HTTP {response.status} -> {url}"
                        )
                        return None

                    return await response.json(content_type=None)

        except Exception as e:
            logger.warning(f"EspnClient error -> {url} -> {e}")

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
