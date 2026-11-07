"""
KhabarF24 Sports API Fetcher
دریافت مسابقات فوتبال، نتایج، ترکیب‌های اصلی و اطلاعات تکمیلی
"""

import asyncio
import copy
import json
import logging
import os
import time

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

from app.models.raw_news import RawNews


logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# تنظیمات
# ----------------------------------------------------------------------

POLL_INTERVAL_SECONDS = 20 * 60

ACTIVE_HOURS_UTC = set(range(10, 24)) | {0, 1}

CACHE_TTL_SECONDS = 24 * 3600

MAX_MATCH_AGE_SECONDS = 36 * 3600

TEHRAN_TZ = timezone(
    timedelta(hours=3, minutes=30)
)

INCLUDE_SUBSTITUTES = False

INCLUDE_LINEUP_IN_RESULT = False

LINEUP_WINDOW_SECONDS = 95 * 60

LINEUP_LATE_SECONDS = 10 * 60

MIN_STARTERS = 9

LINEUP_EXPIRY_AFTER_KICKOFF_SECONDS = 2 * 3600


# ----------------------------------------------------------------------
# Cache
# ----------------------------------------------------------------------

_cache: Dict[str, Dict[str, Any]] = {}


# ----------------------------------------------------------------------
# Sports API Client
# ----------------------------------------------------------------------

class SportsApiClient:
    """
    کلاینت دریافت اطلاعات مسابقات فوتبال.
    """

    BASE_URL = os.getenv(
        "SPORTS_API_BASE_URL",
        "",
    )

    API_KEY = os.getenv(
        "SPORTS_API_KEY",
        "",
    )

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:

        if not self.BASE_URL:
            logger.warning(
                "SPORTS_API_BASE_URL is not configured"
            )
            return None

        headers = {}

        if self.API_KEY:
            headers["x-api-key"] = self.API_KEY

        url = (
            self.BASE_URL.rstrip("/")
            + "/"
            + endpoint.lstrip("/")
        )

        try:
            timeout = aiohttp.ClientTimeout(
                total=30
            )

            async with aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
            ) as session:

                async with session.get(
                    url,
                    params=params,
                ) as response:

                    if response.status != 200:
                        logger.warning(
                            "Sports API returned HTTP %s",
                            response.status,
                        )
                        return None

                    return await response.json()

        except Exception:
            logger.exception(
                "Sports API request failed: %s",
                endpoint,
            )
            return None

    async def get_finished_fixtures(
        self,
        date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        if date is None:
            date = datetime.now(
                timezone.utc
            ).strftime("%Y-%m-%d")

        data = await self._request(
            "fixtures",
            {
                "date": date,
            },
        )

        if not data:
            return []

        if isinstance(data, dict):
            for key in (
                "response",
                "fixtures",
                "data",
                "results",
            ):
                if isinstance(
                    data.get(key),
                    list,
                ):
                    return data[key]

        if isinstance(data, list):
            return data

        return []

    async def get_fixture_summary(
        self,
        event_id: Any,
    ) -> Optional[Dict[str, Any]]:

        data = await self._request(
            f"fixtures/{event_id}"
        )

        if not data:
            return None

        if isinstance(data, dict):

            for key in (
                "response",
                "fixture",
                "data",
                "result",
            ):
                value = data.get(key)

                if isinstance(value, dict):
                    return value

                if isinstance(value, list) and value:
                    return value[0]

            return data

        return None


# ----------------------------------------------------------------------
# Sports API Fetcher
# ----------------------------------------------------------------------

class SportsApiFetcher:
    """
    دریافت و تبدیل اطلاعات مسابقات فوتبال
    به RawNews قابل پردازش در KhabarF24.
    """

    def __init__(self):
        self.client = SportsApiClient()

    # ------------------------------------------------------------------
    # ابزارهای کمکی
    # ------------------------------------------------------------------

    @staticmethod
    def _get(
        data: Any,
        *keys: str,
        default: Any = None,
    ) -> Any:

        if not isinstance(data, dict):
            return default

        for key in keys:
            if key in data:
                return data[key]

        return default

    @staticmethod
    def _safe_text(
        value: Any,
    ) -> str:

        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> Optional[float]:

        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip()

        if not text:
            return None

        try:
            return float(text)
        except ValueError:
            pass

        try:
            dt = datetime.fromisoformat(
                text.replace(
                    "Z",
                    "+00:00",
                )
            )

            if dt.tzinfo is None:
                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            return dt.timestamp()

        except Exception:
            return None

    @staticmethod
    def _format_tehran_time(
        timestamp: Optional[float],
    ) -> str:

        if timestamp is None:
            return ""

        try:
            dt = datetime.fromtimestamp(
                timestamp,
                tz=TEHRAN_TZ,
            )

            return dt.strftime("%H:%M")

        except Exception:
            return ""

    @staticmethod
    def _format_tehran_date(
        timestamp: Optional[float],
    ) -> str:

        if timestamp is None:
            return ""

        try:
            dt = datetime.fromtimestamp(
                timestamp,
                tz=TEHRAN_TZ,
            )

            return dt.strftime("%Y-%m-%d")

        except Exception:
            return ""

    @staticmethod
    def _country_flag(
        country: str,
    ) -> str:

        mapping = {
            "England": "🇬🇧",
            "United Kingdom": "🇬🇧",
            "UK": "🇬🇧",
            "Italy": "🇮🇹",
            "Spain": "🇪🇸",
            "Germany": "🇩🇪",
            "France": "🇫🇷",
            "Portugal": "🇵🇹",
            "Netherlands": "🇳🇱",
            "Belgium": "🇧🇪",
            "Brazil": "🇧🇷",
            "Argentina": "🇦🇷",
            "Iran": "🇮🇷",
            "Turkey": "🇹🇷",
            "United States": "🇺🇸",
            "USA": "🇺🇸",
            "Saudi Arabia": "🇸🇦",
            "Scotland": "🏴",
            "Wales": "🏴",
            "Ireland": "🇮🇪",
            "Austria": "🇦🇹",
            "Switzerland": "🇨🇭",
            "Denmark": "🇩🇰",
            "Sweden": "🇸🇪",
            "Norway": "🇳🇴",
            "Greece": "🇬🇷",
            "Croatia": "🇭🇷",
            "Serbia": "🇷🇸",
            "Ukraine": "🇺🇦",
            "Poland": "🇵🇱",
            "Mexico": "🇲🇽",
        }

        return mapping.get(
            country.strip(),
            "",
        )

    @staticmethod
    def _extract_team(
        value: Any,
    ) -> str:

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, dict):

            return (
                value.get("name")
                or value.get("team_name")
                or value.get("title")
                or ""
            )

        return ""

    # ------------------------------------------------------------------
    # استخراج مسابقات آینده
    # ------------------------------------------------------------------

    def _extract_upcoming(
        self,
        fixtures: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        results = []

        now_ts = time.time()

        for fixture in fixtures:

            if not isinstance(
                fixture,
                dict,
            ):
                continue

            event_id = (
                self._get(
                    fixture,
                    "id",
                    "event_id",
                    "fixture_id",
                )
            )

            if event_id is None:
                continue

            timestamp = self._parse_timestamp(
                self._get(
                    fixture,
                    "timestamp",
                    "kickoff_ts",
                    "start_timestamp",
                    "date",
                )
            )

            if timestamp is None:
                continue

            # مسابقه‌هایی که خیلی دور یا خیلی قدیمی هستند
            if timestamp < (
                now_ts
                - LINEUP_EXPIRY_AFTER_KICKOFF_SECONDS
            ):
                continue

            if timestamp > (
                now_ts
                + LINEUP_WINDOW_SECONDS
            ):
                continue

            teams = self._get(
                fixture,
                "teams",
                default={},
            )

            home_data = (
                self._get(
                    teams,
                    "home",
                    default={},
                )
                if isinstance(teams, dict)
                else {}
            )

            away_data = (
                self._get(
                    teams,
                    "away",
                    default={},
                )
                if isinstance(teams, dict)
                else {}
            )

            home = self._extract_team(
                home_data
            )

            away = self._extract_team(
                away_data
            )

            if not home or not away:

                home = self._extract_team(
                    self._get(
                        fixture,
                        "home",
                    )
                )

                away = self._extract_team(
                    self._get(
                        fixture,
                        "away",
                    )
                )

            if not home or not away:
                continue

            league_data = self._get(
                fixture,
                "league",
                default={},
            )

            if isinstance(
                league_data,
                dict,
            ):
                league = (
                    league_data.get("name")
                    or ""
                )

                stage = (
                    league_data.get("round")
                    or league_data.get("stage")
                    or ""
                )

            else:
                league = self._safe_text(
                    league_data
                )
                stage = ""

            venue_data = self._get(
                fixture,
                "venue",
                default={},
            )

            stadium = ""

            if isinstance(
                venue_data,
                dict,
            ):
                stadium = (
                    venue_data.get("name")
                    or ""
                )

            referee = self._safe_text(
                self._get(
                    fixture,
                    "referee",
                )
            )

            home_country = ""

            away_country = ""

            if isinstance(
                home_data,
                dict,
            ):
                home_country = (
                    home_data.get("country")
                    or ""
                )

            if isinstance(
                away_data,
                dict,
            ):
                away_country = (
                    away_data.get("country")
                    or ""
                )

            result = {
                "event_id": event_id,
                "found_at": now_ts,
                "kickoff_ts": timestamp,

                "home": home,
                "away": away,

                "home_id": (
                    home_data.get("id")
                    if isinstance(
                        home_data,
                        dict,
                    )
                    else None
                ),

                "away_id": (
                    away_data.get("id")
                    if isinstance(
                        away_data,
                        dict,
                    )
                    else None
                ),

                "home_country": home_country,
                "away_country": away_country,

                "league": league,
                "stage": stage,

                "stadium": stadium,
                "referee": referee,

                "match_date":
                    self._format_tehran_date(
                        timestamp
                    ),

                "match_time":
                    self._format_tehran_time(
                        timestamp
                    ),

                "lineup": {
                    "home": {
                        "name": home,
                        "starting": [],
                        "substitutes": [],
                    },
                    "away": {
                        "name": away,
                        "starting": [],
                        "substitutes": [],
                    },
                },

                "coach": {
                    "home": "",
                    "away": "",
                },
            }

            results.append(result)

        return results

    # ------------------------------------------------------------------
    # اعمال اطلاعات تکمیلی مسابقه
    # ------------------------------------------------------------------

    def _apply_info(
        self,
        base: Dict[str, Any],
        summary: Dict[str, Any],
    ) -> None:

        if not isinstance(
            summary,
            dict,
        ):
            return

        venue = self._get(
            summary,
            "venue",
            default={},
        )

        if isinstance(
            venue,
            dict,
        ):
            base["stadium"] = (
                venue.get("name")
                or base.get("stadium")
                or ""
            )

        referee = self._get(
            summary,
            "referee",
        )

        if referee:
            base["referee"] = (
                self._safe_text(
                    referee
                )
            )

        league = self._get(
            summary,
            "league",
            default={},
        )

        if isinstance(
            league,
            dict,
        ):
            base["league"] = (
                league.get("name")
                or base.get("league")
                or ""
            )

            base["stage"] = (
                league.get("round")
                or league.get("stage")
                or base.get("stage")
                or ""
            )

    # ------------------------------------------------------------------
    # استخراج ترکیب
    # ------------------------------------------------------------------

    def _apply_rosters(
        self,
        base: Dict[str, Any],
        summary: Dict[str, Any],
    ) -> None:

        if not isinstance(
            summary,
            dict,
        ):
            return

        lineups = (
            summary.get("lineups")
            or summary.get("lineup")
            or []
        )

        if isinstance(
            lineups,
            dict,
        ):
            lineups = [
                {
                    "team": {
                        "name": key
                    },
                    **(
                        value
                        if isinstance(
                            value,
                            dict,
                        )
                        else {}
                    ),
                }
                for key, value in lineups.items()
            ]

        if not isinstance(
            lineups,
            list,
        ):
            return

        for lineup in lineups:

            if not isinstance(
                lineup,
                dict,
            ):
                continue

            team_data = self._get(
                lineup,
                "team",
                default={},
            )

            team_name = self._extract_team(
                team_data
            )

            if not team_name:
                team_name = self._safe_text(
                    lineup.get("team_name")
                )

            if not team_name:
                continue

            side = None

            if (
                team_name
                == base["home"]
            ):
                side = "home"

            elif (
                team_name
                == base["away"]
            ):
                side = "away"

            else:
                team_id = (
                    team_data.get("id")
                    if isinstance(
                        team_data,
                        dict,
                    )
                    else None
                )

                if (
                    team_id
                    and team_id
                    == base.get(
                        "home_id"
                    )
                ):
                    side = "home"

                elif (
                    team_id
                    and team_id
                    == base.get(
                        "away_id"
                    )
                ):
                    side = "away"

            if side is None:
                continue

            formation = (
                lineup.get("formation")
                or ""
            )

            base["lineup"][side][
                "name"
            ] = (
                team_name
                + (
                    f" ({formation})"
                    if formation
                    else ""
                )
            )

            starters = (
                lineup.get(
                    "startXI"
                )
                or lineup.get(
                    "starting"
                )
                or []
            )

            substitutes = (
                lineup.get(
                    "substitutes"
                )
                or lineup.get(
                    "bench"
                )
                or []
            )

            def parse_players(
                players: Any,
            ) -> List[str]:

                output = []

                if not isinstance(
                    players,
                    list,
                ):
                    return output

                for player in players:

                    if not isinstance(
                        player,
                        dict,
                    ):
                        continue

                    player_data = (
                        player.get(
                            "player",
                            player,
                        )
                    )

                    if not isinstance(
                        player_data,
                        dict,
                    ):
                        continue

                    number = (
                        player_data.get(
                            "number"
                        )
                        or player.get(
                            "number"
                        )
                        or ""
                    )

                    name = (
                        player_data.get(
                            "name"
                        )
                        or player_data.get(
                            "fullname"
                        )
                        or player.get(
                            "name"
                        )
                        or ""
                    )

                    name = self._safe_text(
                        name
                    )

                    if not name:
                        continue

                    if number:
                        output.append(
                            f"{number} {name}"
                        )
                    else:
                        output.append(
                            name
                        )

                return output

            base["lineup"][side][
                "starting"
            ] = parse_players(
                starters
            )

            base["lineup"][side][
                "substitutes"
            ] = parse_players(
                substitutes
            )

            coach = (
                lineup.get("coach")
                or {}
            )

            if isinstance(
                coach,
                dict,
            ):
                coach_name = (
                    coach.get("name")
                    or ""
                )

                base["coach"][side] = (
                    self._safe_text(
                        coach_name
                    )
                )

    # ------------------------------------------------------------------
    # بررسی ترکیب
    # ------------------------------------------------------------------

    async def _maybe_lineup(
        self,
        fixtures: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        upcoming = (
            self._extract_upcoming(
                fixtures
            )
        )

        results = []

        now_ts = time.time()

        for base in upcoming:

            kickoff_ts = base.get(
                "kickoff_ts"
            )

            if kickoff_ts is None:
                continue

            # فقط بازه مناسب اعلام ترکیب
            if (
                kickoff_ts - now_ts
                > LINEUP_WINDOW_SECONDS
            ):
                continue

            if (
                now_ts - kickoff_ts
                > LINEUP_EXPIRY_AFTER_KICKOFF_SECONDS
            ):
                continue

            event_id = base.get(
                "event_id"
            )

            if event_id is None:
                continue

            key = (
                f"lineup:{event_id}"
            )

            cached = _cache.get(
                key
            )

            if cached:

                cached_at = cached.get(
                    "found_at",
                    0,
                )

                if (
                    now_ts
                    - cached_at
                    < CACHE_TTL_SECONDS
                ):
                    results.append(
                        cached
                    )
                    continue

            summary = (
                await self.client
                .get_fixture_summary(
                    event_id
                )
            )

            if not summary:
                continue

            self._apply_info(
                base,
                summary,
            )

            self._apply_rosters(
                base,
                summary,
            )

            home_starters = len(
                base["lineup"]["home"][
                    "starting"
                ]
            )

            away_starters = len(
                base["lineup"]["away"][
                    "starting"
                ]
            )

            if (
                home_starters
                < MIN_STARTERS
                or away_starters
                < MIN_STARTERS
            ):
                continue

            base["key"] = key

            # ----------------------------------------------------------
            # تعیین نوع پست
            # ----------------------------------------------------------
            # این مقدار برای انتخاب قالب اختصاصی
            # match_post.py ضروری است.

            base["kind"] = "lineup"

            _cache[key] = base

            results.append(
                base
            )

        return results

    # ------------------------------------------------------------------
    # ساخت RawNews برای نتیجه
    # ------------------------------------------------------------------

    def _make_news(
        self,
        data: Dict[str, Any],
    ) -> RawNews:

        home = data["home"]

        away = data["away"]

        home_goals = data.get(
            "home_goals",
            0,
        )

        away_goals = data.get(
            "away_goals",
            0,
        )

        title = (
            f"{home} {home_goals} - "
            f"{away_goals} {away}"
        )

        summary = (
            f"نتیجه دیدار {home} و "
            f"{away} در "
            f"{data.get('league', '')}"
        )

        news = RawNews(
            title=title,
            content=summary,
            summary=summary,
            url="",
            image_url=None,
            source="ESPN",
            source_id="espn",
            country="US",
            language="en",
            category="sport",
        )

        # --------------------------------------------------------------
        # اطلاعات ورزشی
        # --------------------------------------------------------------

        news.sport = "football"

        news.sport_name = "فوتبال"

        news.sport_emoji = "⚽"

        news.sport_hashtag = "#فوتبال"

        news.category = "sport"

        # --------------------------------------------------------------
        # نتیجه
        # --------------------------------------------------------------

        news.home_team = home

        news.away_team = away

        news.home_goals = home_goals

        news.away_goals = away_goals

        news.goals = data.get(
            "goals",
            [],
        )

        news.assists = data.get(
            "assists",
            [],
        )

        news.cards = data.get(
            "cards",
            [],
        )

        news.lineup = copy.deepcopy(
            data.get(
                "lineup",
                {},
            )
        )

        news.stats = data.get(
            "stats",
            {},
        )

        # --------------------------------------------------------------
        # اطلاعات مسابقه
        # --------------------------------------------------------------

        news.tournament = data.get(
            "league",
            "",
        )

        news.league = data.get(
            "league",
            "",
        )

        news.stage = data.get(
            "stage",
            "",
        )

        news.stadium = data.get(
            "stadium",
            "",
        )

        news.referee = data.get(
            "referee",
            "",
        )

        news.match_date = data.get(
            "match_date",
            "",
        )

        news.match_time = data.get(
            "match_time",
            "",
        )

        # --------------------------------------------------------------
        # اطلاعات اختصاصی Match Post
        # --------------------------------------------------------------
        # match_post.py برای انتخاب قالب نتیجه
        # به این دو فیلد نیاز دارد.

        news.match_phase = "result"

        news.match_info = {
            "home": data["home"],
            "away": data["away"],
            "home_goals": data["home_goals"],
            "away_goals": data["away_goals"],
            "home_country": data.get(
                "home_country",
                "",
            ),
            "away_country": data.get(
                "away_country",
                "",
            ),
            "home_flag": "",
            "away_flag": "",
        }

        # --------------------------------------------------------------
        # کشورها
        # --------------------------------------------------------------

        news.home_country = data.get(
            "home_country",
            "",
        )

        news.away_country = data.get(
            "away_country",
            "",
        )

        # --------------------------------------------------------------
        # منبع
        # --------------------------------------------------------------

        news.source = "ESPN"

        news.source_id = "espn"

        news.country = "US"

        news.language = "en"

        # --------------------------------------------------------------
        # زمان
        # --------------------------------------------------------------

        news.published_at = (
            datetime.now(
                timezone.utc
            )
        )

        news.fetched_at = (
            datetime.now(
                timezone.utc
            )
        )

        return news

    # ------------------------------------------------------------------
    # ساخت RawNews برای ترکیب
    # ------------------------------------------------------------------

    def _make_lineup_news(
        self,
        data: Dict[str, Any],
    ) -> RawNews:

        home = data["home"]

        away = data["away"]

        league = data.get(
            "league",
            "",
        )

        title = (
            f"ترکیب‌های رسمی تیم‌های "
            f"{home} و {away}"
            + (
                f" در {league}"
                if league
                else ""
            )
        )

        summary = (
            f"ترکیب‌های رسمی تیم‌های "
            f"{home} و {away} "
            f"برای این دیدار اعلام شد."
        )

        news = RawNews(
            title=title,
            content=summary,
            summary=summary,
            url="",
            image_url=None,
            source="ESPN",
            source_id="espn",
            country="US",
            language="en",
            category="sport",
        )

        # --------------------------------------------------------------
        # اطلاعات ورزشی
        # --------------------------------------------------------------

        news.sport = "football"

        news.sport_name = "فوتبال"

        news.sport_emoji = "⚽"

        news.sport_hashtag = "#فوتبال"

        news.category = "sport"

        # --------------------------------------------------------------
        # اطلاعات نتیجه
        # --------------------------------------------------------------

        news.home_team = home

        news.away_team = away

        news.home_goals = None

        news.away_goals = None

        news.goals = data.get(
            "goals",
            [],
        )

        news.assists = data.get(
            "assists",
            [],
        )

        news.cards = data.get(
            "cards",
            [],
        )

        # --------------------------------------------------------------
        # ترکیب
        # --------------------------------------------------------------

        news.lineup = copy.deepcopy(
            data["lineup"]
        )

        news.coach = copy.deepcopy(
            data.get(
                "coach",
                {},
            )
        )

        # --------------------------------------------------------------
        # اطلاعات مسابقه
        # --------------------------------------------------------------

        news.stats = data.get(
            "stats",
            {},
        )

        news.tournament = data.get(
            "league",
            "",
        )

        news.league = data.get(
            "league",
            "",
        )

        news.stage = data.get(
            "stage",
            "",
        )

        news.stadium = data.get(
            "stadium",
            "",
        )

        news.referee = data.get(
            "referee",
            "",
        )

        news.match_date = data.get(
            "match_date",
            "",
        )

        news.match_time = data.get(
            "match_time",
            "",
        )

        # --------------------------------------------------------------
        # اطلاعات اختصاصی Match Post
        # --------------------------------------------------------------
        # این بخش مهم‌ترین اصلاح این فایل است.
        #
        # match_post.py با بررسی match_phase متوجه می‌شود
        # که این خبر مربوط به ترکیب است و باید
        # _render_lineup() را اجرا کند.
        #
        # match_info نیز نام تیم‌ها و کشورها را در اختیار
        # قالب اختصاصی قرار می‌دهد.

        news.match_phase = "lineup"

        news.match_info = {
            "home": data["home"],
            "away": data["away"],
            "home_country": data.get(
                "home_country",
                "",
            ),
            "away_country": data.get(
                "away_country",
                "",
            ),
            "home_flag": "",
            "away_flag": "",
            "home_goals": "",
            "away_goals": "",
        }

        # --------------------------------------------------------------
        # کشورها
        # --------------------------------------------------------------

        news.home_country = data.get(
            "home_country",
            "",
        )

        news.away_country = data.get(
            "away_country",
            "",
        )

        # --------------------------------------------------------------
        # منبع
        # --------------------------------------------------------------

        news.source = "ESPN"

        news.source_id = "espn"

        news.country = "US"

        news.language = "en"

        # --------------------------------------------------------------
        # زمان
        # --------------------------------------------------------------

        news.published_at = (
            datetime.now(
                timezone.utc
            )
        )

        news.fetched_at = (
            datetime.now(
                timezone.utc
            )
        )

        return news

    # ------------------------------------------------------------------
    # دریافت اخبار
    # ------------------------------------------------------------------

    async def fetch(
        self,
    ) -> List[RawNews]:

        now = datetime.now(
            timezone.utc
        )

        current_hour = now.hour

        if (
            current_hour
            not in ACTIVE_HOURS_UTC
        ):
            return []

        today = now.strftime(
            "%Y-%m-%d"
        )

        try:

            fixtures = (
                await self.client
                .get_finished_fixtures(
                    today
                )
            )

            if not fixtures:
                return []

            news_list = []

            # ----------------------------------------------------------
            # ترکیب‌های رسمی
            # ----------------------------------------------------------

            lineup_data = (
                await self._maybe_lineup(
                    fixtures
                )
            )

            lineup_keys = set()

            for data in lineup_data:

                key = data.get(
                    "key"
                )

                if key:
                    lineup_keys.add(
                        key
                    )

                news_list.append(
                    self._make_lineup_news(
                        data
                    )
                )

            # ----------------------------------------------------------
            # نتایج نهایی
            # ----------------------------------------------------------

            for fixture in fixtures:

                if not isinstance(
                    fixture,
                    dict,
                ):
                    continue

                event_id = (
                    self._get(
                        fixture,
                        "id",
                        "event_id",
                        "fixture_id",
                    )
                )

                if event_id is None:
                    continue

                result_key = (
                    f"result:{event_id}"
                )

                # اگر قبلاً نتیجه منتشر شده
                # دوباره تولید نکن.

                if result_key in _cache:
                    cached_at = _cache[
                        result_key
                    ].get(
                        "found_at",
                        0,
                    )

                    if (
                        time.time()
                        - cached_at
                        < CACHE_TTL_SECONDS
                    ):
                        continue

                teams = self._get(
                    fixture,
                    "teams",
                    default={},
                )

                home_data = (
                    teams.get(
                        "home",
                        {},
                    )
                    if isinstance(
                        teams,
                        dict,
                    )
                    else {}
                )

                away_data = (
                    teams.get(
                        "away",
                        {},
                    )
                    if isinstance(
                        teams,
                        dict,
                    )
                    else {}
                )

                home = self._extract_team(
                    home_data
                )

                away = self._extract_team(
                    away_data
                )

                if not home or not away:
                    continue

                goals = self._get(
                    fixture,
                    "goals",
                    default={},
                )

                if not isinstance(
                    goals,
                    dict,
                ):
                    goals = {}

                home_goals = (
                    goals.get(
                        "home"
                    )
                    if "home" in goals
                    else 0
                )

                away_goals = (
                    goals.get(
                        "away"
                    )
                    if "away" in goals
                    else 0
                )

                if home_goals is None:
                    home_goals = 0

                if away_goals is None:
                    away_goals = 0

                timestamp = (
                    self._parse_timestamp(
                        self._get(
                            fixture,
                            "timestamp",
                            "kickoff_ts",
                            "start_timestamp",
                            "date",
                        )
                    )
                )

                if timestamp is None:
                    timestamp = time.time()

                league_data = self._get(
                    fixture,
                    "league",
                    default={},
                )

                if isinstance(
                    league_data,
                    dict,
                ):
                    league = (
                        league_data.get(
                            "name"
                        )
                        or ""
                    )

                    stage = (
                        league_data.get(
                            "round"
                        )
                        or league_data.get(
                            "stage"
                        )
                        or ""
                    )
                else:
                    league = (
                        self._safe_text(
                            league_data
                        )
                    )
                    stage = ""

                venue_data = self._get(
                    fixture,
                    "venue",
                    default={},
                )

                stadium = ""

                if isinstance(
                    venue_data,
                    dict,
                ):
                    stadium = (
                        venue_data.get(
                            "name"
                        )
                        or ""
                    )

                referee = self._safe_text(
                    self._get(
                        fixture,
                        "referee",
                    )
                )

                data = {
                    "event_id":
                        event_id,

                    "home":
                        home,

                    "away":
                        away,

                    "home_goals":
                        home_goals,

                    "away_goals":
                        away_goals,

                    "home_country":
                        (
                            home_data.get(
                                "country",
                                "",
                            )
                            if isinstance(
                                home_data,
                                dict,
                            )
                            else ""
                        ),

                    "away_country":
                        (
                            away_data.get(
                                "country",
                                "",
                            )
                            if isinstance(
                                away_data,
                                dict,
                            )
                            else ""
                        ),

                    "league":
                        league,

                    "stage":
                        stage,

                    "stadium":
                        stadium,

                    "referee":
                        referee,

                    "match_date":
                        self._format_tehran_date(
                            timestamp
                        ),

                    "match_time":
                        self._format_tehran_time(
                            timestamp
                        ),

                    "goals":
                        self._get(
                            fixture,
                            "events",
                            "goals",
                            default=[],
                        ),

                    "assists":
                        [],

                    "cards":
                        [],

                    "lineup":
                        {},

                    "stats":
                        {},
                }

                news = self._make_news(
                    data
                )

                _cache[result_key] = {
                    "found_at":
                        time.time(),
                    "news":
                        news,
                }

                news_list.append(
                    news
                )

            return news_list

        except Exception:
            logger.exception(
                "SportsApiFetcher.fetch failed"
            )
            return []
