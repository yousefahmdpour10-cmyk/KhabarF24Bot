"""
Sports API Client (api-football.com)

اتصال به API-Football برای گرفتن نتیجه‌ی بازی‌ها و گلزنان.
"""

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


class SportsApiClient:

    def __init__(self):
        self.api_key = getattr(settings, "SPORTS_API_KEY", "")

    async def _get(self, path: str, params: dict) -> Optional[dict]:

        if not self.api_key:
            logger.error("SportsApiClient: SPORTS_API_KEY تنظیم نشده است")
            return None

        headers = {"x-apisports-key": self.api_key}
        url = f"{BASE_URL}{path}"

        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
            ) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        errors = data.get("errors")
                        if errors:
                            logger.error(
                                f"SportsApiClient API error -> {errors}"
                            )

                        return data

                    body = await response.text()
                    logger.error(
                        f"SportsApiClient HTTP {response.status} -> {body[:300]}"
                    )

        except Exception as e:
            logger.error(f"SportsApiClient error -> {e}")

        return None

    async def get_finished_fixtures(self, date: str) -> List[dict]:

        fixtures: List[dict] = []

        for league_id, league_name in FOLLOWED_LEAGUES.items():

            data = await self._get(
                "/fixtures",
                {
                    "date": date,
                    "league": league_id,
                    "status": "FT",
                },
            )

            if not data:
                logger.warning(
                    f"SportsApiClient: پاسخی برای لیگ {league_name} دریافت نشد"
                )
                continue

            found = data.get("response", [])

            logger.info(
                f"SportsApiClient: {league_name} -> {len(found)} بازی تمام‌شده در {date}"
            )

            for item in found:
                item["_league_name"] = league_name
                fixtures.append(item)

        return fixtures

    async def get_fixture_events(self, fixture_id: int) -> List[dict]:

        data = await self._get(
            "/fixtures/events",
            {"fixture": fixture_id},
        )

        if not data:
            return []

        return data.get("response", [])
