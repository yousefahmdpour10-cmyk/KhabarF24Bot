"""
Sports API Fetcher - KhabarF24

دریافت مسابقات فوتبال از API ورزشی
و تبدیل آن‌ها به RawNews سازگار با
Football Match Formatter و Match Prompt.
"""

import asyncio
import copy
import json
import logging
import os
import time

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

from app.models.raw_news import RawNews


logger = logging.getLogger(__name__)


# =========================================================
# Configuration
# =========================================================

POLL_INTERVAL_SECONDS = 20 * 60

ACTIVE_HOURS_UTC = set(range(10, 24)) | {0, 1}

CACHE_TTL_SECONDS = 24 * 3600

MAX_MATCH_AGE_SECONDS = 36 * 3600

TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))

LINEUP_WINDOW_MINUTES = 95
LINEUP_LATE_SECONDS = 10 * 60

MIN_STARTERS = 9

LINEUP_EXPIRY_AFTER_KICKOFF_SECONDS = 2 * 3600

INCLUDE_SUBSTITUTES = True
INCLUDE_LINEUP_IN_RESULT = False


# =========================================================
# Cache
# =========================================================

_cache: Dict[str, Dict[str, Any]] = {}


# =========================================================
# Sports API Client
# =========================================================

class SportsApiClient:
    """
    Client for sports API.
    """

    def __init__(self):
        self.base_url = (
            os.getenv("SPORTS_API_BASE_URL", "").strip()
        ).rstrip("/")

        self.api_key = os.getenv(
            "SPORTS_API_KEY",
            ""
        ).strip()

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if not self.base_url:
            logger.error("SPORTS_API_BASE_URL is not configured.")
            return None

        headers = {}

        if self.api_key:
            headers["x-api-key"] = self.api_key
            headers["X-API-Key"] = self.api_key

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        timeout = aiohttp.ClientTimeout(total=20)

        try:
            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    url,
                    params=params or {},
                    headers=headers,
                ) as response:

                    if response.status != 200:
                        logger.warning(
                            "Sports API returned HTTP %s for %s",
                            response.status,
                            endpoint,
                        )
                        return None

                    content_type = (
                        response.headers.get("Content-Type", "")
                        .lower()
                    )

                    if "json" in content_type:
                        return await response.json()

                    text = await response.text()

                    try:
                        return json.loads(text)
                    except Exception:
                        return text

        except asyncio.TimeoutError:
            logger.warning(
                "Sports API timeout for endpoint: %s",
                endpoint,
            )
            return None

        except Exception as exc:
            logger.exception(
                "Sports API request error for %s: %s",
                endpoint,
                exc,
            )
            return None

    async def get_finished_fixtures(
        self,
        date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        دریافت مسابقات پایان‌یافته روز.
        """

        if not date:
            date = datetime.now(
                timezone.utc
            ).strftime("%Y-%m-%d")

        data = await self._request(
            "/fixtures",
            params={
                "date": date,
                "status": "FT",
            },
        )

        if not data:
            return []

        if isinstance(data, dict):

            if isinstance(data.get("response"), list):
                return data["response"]

            if isinstance(data.get("fixtures"), list):
                return data["fixtures"]

            if isinstance(data.get("data"), list):
                return data["data"]

        if isinstance(data, list):
            return data

        return []

    async def get_fixture_summary(
        self,
        event_id: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        دریافت اطلاعات کامل یک مسابقه.
        """

        data = await self._request(
            f"/fixtures/{event_id}"
        )

        if not data:
            return None

        if isinstance(data, dict):

            if isinstance(data.get("response"), list):
                if data["response"]:
                    return data["response"][0]

            if isinstance(data.get("data"), dict):
                return data["data"]

            if isinstance(data.get("fixture"), dict):
                return data["fixture"]

            return data

        return None


# =========================================================
# Sports API Fetcher
# =========================================================

class SportsApiFetcher:
    """
    Fetcher مخصوص منابع ورزشی.

    سازگار با:
        FetchService -> SportsApiFetcher(source)
    """

    def __init__(self, source=None):
        self.source = source
        self.client = SportsApiClient()

    # =====================================================
    # Generic helpers
    # =====================================================

    @staticmethod
    def _get(
        data: Any,
        *keys: str,
        default: Any = None,
    ) -> Any:

        current = data

        for key in keys:

            if isinstance(current, dict):
                current = current.get(key)

            else:
                return default

            if current is None:
                return default

        return current

    @staticmethod
    def _safe_text(value: Any) -> str:

        if value is None:
            return ""

        if isinstance(value, str):
            return value.strip()

        return str(value).strip()

    @staticmethod
    def _parse_timestamp(value: Any) -> Optional[datetime]:

        if value is None:
            return None

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(
                    tzinfo=timezone.utc
                )
            return value

        if isinstance(value, (int, float)):

            try:
                return datetime.fromtimestamp(
                    value,
                    tz=timezone.utc,
                )
            except Exception:
                return None

        value = str(value).strip()

        if not value:
            return None

        try:
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"

            dt = datetime.fromisoformat(value)

            if dt.tzinfo is None:
                dt = dt.replace(
                    tzinfo=timezone.utc
                )

            return dt

        except Exception:
            pass

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(
                    value,
                    fmt,
                ).replace(tzinfo=timezone.utc)
            except Exception:
                continue

        return None

    @staticmethod
    def _format_tehran_time(
        value: Any,
    ) -> str:

        dt = (
            value
            if isinstance(value, datetime)
            else SportsApiFetcher._parse_timestamp(value)
        )

        if not dt:
            return ""

        return dt.astimezone(
            TEHRAN_TZ
        ).strftime("%H:%M")

    @staticmethod
    def _format_tehran_date(
        value: Any,
    ) -> str:

        dt = (
            value
            if isinstance(value, datetime)
            else SportsApiFetcher._parse_timestamp(value)
        )

        if not dt:
            return ""

        return dt.astimezone(
            TEHRAN_TZ
        ).strftime("%Y-%m-%d")

    @staticmethod
    def _country_flag(
        country: Any,
    ) -> str:

        if not country:
            return ""

        value = str(country).strip().lower()

        mapping = {
            "iran": "🇮🇷",
            "ir": "🇮🇷",

            "england": "🇬🇧",
            "gb": "🇬🇧",
            "uk": "🇬🇧",

            "italy": "🇮🇹",
            "it": "🇮🇹",

            "spain": "🇪🇸",
            "es": "🇪🇸",

            "france": "🇫🇷",
            "fr": "🇫🇷",

            "germany": "🇩🇪",
            "de": "🇩🇪",

            "portugal": "🇵🇹",
            "pt": "🇵🇹",

            "netherlands": "🇳🇱",
            "nl": "🇳🇱",

            "belgium": "🇧🇪",
            "be": "🇧🇪",

            "brazil": "🇧🇷",
            "br": "🇧🇷",

            "argentina": "🇦🇷",
            "ar": "🇦🇷",

            "turkey": "🇹🇷",
            "tr": "🇹🇷",

            "usa": "🇺🇸",
            "us": "🇺🇸",

            "united states": "🇺🇸",

            "mexico": "🇲🇽",
            "mx": "🇲🇽",

            "saudi arabia": "🇸🇦",
            "sa": "🇸🇦",

            "japan": "🇯🇵",
            "jp": "🇯🇵",

            "south korea": "🇰🇷",
            "korea republic": "🇰🇷",
            "kr": "🇰🇷",

            "australia": "🇦🇺",
            "au": "🇦🇺",

            "scotland": "🏴",
            "wales": "🏴",
            "ireland": "🇮🇪",
            "republic of ireland": "🇮🇪",

            "switzerland": "🇨🇭",
            "ch": "🇨🇭",

            "austria": "🇦🇹",
            "at": "🇦🇹",

            "denmark": "🇩🇰",
            "dk": "🇩🇰",

            "sweden": "🇸🇪",
            "se": "🇸🇪",

            "norway": "🇳🇴",
            "no": "🇳🇴",

            "poland": "🇵🇱",
            "pl": "🇵🇱",

            "ukraine": "🇺🇦",
            "ua": "🇺🇦",

            "croatia": "🇭🇷",
            "hr": "🇭🇷",

            "serbia": "🇷🇸",
            "rs": "🇷🇸",

            "greece": "🇬🇷",
            "gr": "🇬🇷",

            "czech republic": "🇨🇿",
            "czechia": "🇨🇿",
            "cz": "🇨🇿",

            "colombia": "🇨🇴",
            "co": "🇨🇴",

            "chile": "🇨🇱",
            "cl": "🇨🇱",

            "uruguay": "🇺🇾",
            "uy": "🇺🇾",

            "ecuador": "🇪🇨",
            "ec": "🇪🇨",
        }

        return mapping.get(value, "")

    # =====================================================
    # Team extraction
    # =====================================================

    def _extract_team(
        self,
        team_data: Any,
    ) -> Dict[str, str]:

        if not isinstance(team_data, dict):
            return {
                "name": self._safe_text(team_data),
                "country": "",
                "flag": "",
            }

        name = (
            self._safe_text(
                team_data.get("name")
            )
            or self._safe_text(
                team_data.get("team", {}).get("name")
                if isinstance(team_data.get("team"), dict)
                else ""
            )
        )

        country = (
            self._safe_text(
                team_data.get("country")
            )
            or self._safe_text(
                team_data.get("nationality")
            )
            or self._safe_text(
                team_data.get("team", {}).get("country")
                if isinstance(team_data.get("team"), dict)
                else ""
            )
        )

        flag = (
            self._safe_text(
                team_data.get("flag")
            )
            or self._country_flag(country)
        )

        return {
            "name": name,
            "country": country,
            "flag": flag,
        }

    # =====================================================
    # Upcoming / lineup helpers
    # =====================================================

    def _extract_upcoming(
        self,
        fixture: Dict[str, Any],
    ) -> Dict[str, Any]:

        teams = fixture.get("teams") or {}

        home = self._extract_team(
            teams.get("home") or {}
        )

        away = self._extract_team(
            teams.get("away") or {}
        )

        fixture_data = (
            fixture.get("fixture")
            if isinstance(fixture.get("fixture"), dict)
            else fixture
        )

        event_id = (
            fixture_data.get("id")
            or fixture.get("id")
            or fixture.get("event_id")
        )

        timestamp = (
            fixture_data.get("timestamp")
            or fixture_data.get("date")
            or fixture.get("timestamp")
            or fixture.get("date")
        )

        league = fixture.get("league") or {}

        venue = fixture_data.get("venue") or {}

        if isinstance(venue, dict):
            stadium = (
                venue.get("name")
                or venue.get("stadium")
                or ""
            )
        else:
            stadium = self._safe_text(venue)

        referee = (
            fixture_data.get("referee")
            or ""
        )

        return {
            "event_id": event_id,
            "home": home,
            "away": away,
            "timestamp": timestamp,
            "league": league,
            "stadium": self._safe_text(stadium),
            "referee": self._safe_text(referee),
        }

    def _apply_info(
        self,
        info: Dict[str, Any],
        fixture: Dict[str, Any],
    ) -> None:

        extracted = self._extract_upcoming(
            fixture
        )

        info.update(extracted)

    def _apply_rosters(
        self,
        info: Dict[str, Any],
        fixture: Dict[str, Any],
    ) -> None:

        rosters = (
            fixture.get("lineups")
            or fixture.get("rosters")
            or []
        )

        if not isinstance(rosters, list):
            return

        info["lineups"] = rosters

    async def _maybe_lineup(
        self,
        fixture: Dict[str, Any],
    ) -> Optional[RawNews]:

        info = self._extract_upcoming(
            fixture
        )

        timestamp = info.get("timestamp")

        match_dt = self._parse_timestamp(
            timestamp
        )

        if not match_dt:
            return None

        now = datetime.now(
            timezone.utc
        )

        seconds_until_kickoff = (
            match_dt - now
        ).total_seconds()

        if (
            seconds_until_kickoff > LINEUP_WINDOW_MINUTES * 60
            or seconds_until_kickoff < -LINEUP_LATE_SECONDS
        ):
            return None

        event_id = info.get("event_id")

        if not event_id:
            return None

        cache_key = f"lineup:{event_id}"

        cached = _cache.get(
            cache_key
        )

        if cached:
            cached_at = cached.get(
                "timestamp",
                0,
            )

            if (
                time.time() - cached_at
                < CACHE_TTL_SECONDS
            ):
                return None

        summary = await self.client.get_fixture_summary(
            event_id
        )

        if not summary:
            return None

        self._apply_info(
            info,
            summary,
        )

        self._apply_rosters(
            info,
            summary,
        )

        lineups = (
            info.get("lineups")
            or []
        )

        if not lineups:
            return None

        starters_count = 0

        for lineup in lineups:

            if not isinstance(lineup, dict):
                continue

            start_xi = (
                lineup.get("startXI")
                or lineup.get("starting_xi")
                or lineup.get("starters")
                or []
            )

            if isinstance(start_xi, list):
                starters_count += len(start_xi)

        if starters_count < MIN_STARTERS:
            return None

        news = self._make_lineup_news(
            info,
            summary,
        )

        if news:
            _cache[cache_key] = {
                "timestamp": time.time(),
            }

        return news

    # =====================================================
    # Result News
    # =====================================================

    def _make_news(
        self,
        info: Dict[str, Any],
        fixture: Dict[str, Any],
    ) -> Optional[RawNews]:

        home = info.get("home") or {}
        away = info.get("away") or {}

        home_name = self._safe_text(
            home.get("name")
        )

        away_name = self._safe_text(
            away.get("name")
        )

        if not home_name or not away_name:
            return None

        fixture_data = (
            fixture.get("fixture")
            if isinstance(fixture.get("fixture"), dict)
            else fixture
        )

        event_id = (
            info.get("event_id")
            or fixture_data.get("id")
            or fixture.get("id")
        )

        timestamp = (
            info.get("timestamp")
            or fixture_data.get("timestamp")
            or fixture_data.get("date")
        )

        league = (
            info.get("league")
            or fixture.get("league")
            or {}
        )

        if isinstance(league, dict):
            league_name = (
                league.get("name")
                or league.get("league")
                or ""
            )

            league_country = (
                league.get("country")
                or ""
            )

            league_logo = (
                league.get("logo")
                or ""
            )
        else:
            league_name = self._safe_text(
                league
            )
            league_country = ""
            league_logo = ""

        goals = (
            fixture.get("events")
            or fixture.get("goals")
            or []
        )

        assists = (
            fixture.get("assists")
            or []
        )

        cards = (
            fixture.get("cards")
            or []
        )

        statistics = (
            fixture.get("statistics")
            or []
        )

        venue = (
            fixture_data.get("venue")
            or fixture.get("venue")
            or {}
        )

        if isinstance(venue, dict):
            stadium = (
                venue.get("name")
                or venue.get("stadium")
                or info.get("stadium")
                or ""
            )
        else:
            stadium = self._safe_text(
                venue
            )

        referee = (
            fixture_data.get("referee")
            or fixture.get("referee")
            or info.get("referee")
            or ""
        )

        score = (
            fixture.get("score")
            or fixture.get("scores")
            or {}
        )

        home_goals = None
        away_goals = None

        if isinstance(score, dict):

            fulltime = (
                score.get("fulltime")
                or score.get("full_time")
                or {}
            )

            if isinstance(fulltime, dict):

                home_goals = (
                    fulltime.get("home")
                    if fulltime.get("home") is not None
                    else score.get("home")
                )

                away_goals = (
                    fulltime.get("away")
                    if fulltime.get("away") is not None
                    else score.get("away")
                )

            else:

                home_goals = score.get(
                    "home"
                )

                away_goals = score.get(
                    "away"
                )

        if home_goals is None:
            home_goals = (
                fixture.get("home_goals")
                or fixture.get("goals_home")
            )

        if away_goals is None:
            away_goals = (
                fixture.get("away_goals")
                or fixture.get("goals_away")
            )

        # -------------------------------------------------
        # Country + flag
        # -------------------------------------------------

        home_country = (
            self._safe_text(
                home.get("country")
            )
            or self._safe_text(
                fixture.get("home_country")
            )
        )

        away_country = (
            self._safe_text(
                away.get("country")
            )
            or self._safe_text(
                fixture.get("away_country")
            )
        )

        home_flag = (
            self._safe_text(
                home.get("flag")
            )
            or self._country_flag(
                home_country
            )
        )

        away_flag = (
            self._safe_text(
                away.get("flag")
            )
            or self._country_flag(
                away_country
            )
        )

        # -------------------------------------------------
        # RawNews
        # -------------------------------------------------

        news = RawNews(
            title=f"{home_name} {home_goals} - {away_goals} {away_name}",

            content="",

            summary="",

            url=(
                fixture_data.get("url")
                or fixture.get("url")
                or ""
            ),

            image_url="",

            author="ESPN",

            published_at=(
                self._parse_timestamp(timestamp)
                or datetime.now(
                    timezone.utc
                )
            ),

            fetched_at=datetime.now(
                timezone.utc
            ),

            source="ESPN",

            source_id="espn",

            country="US",

            language="en",

            category="sport",

            tags=[
                "football",
                "sport",
            ],

            related_urls=[],

            raw_data=fixture,
        )

        # =================================================
        # Football metadata
        # =================================================

        news.sport = "football"
        news.sport_name = "فوتبال"
        news.sport_emoji = "⚽"
        news.sport_hashtag = "#فوتبال"

        news.home_team = home_name
        news.away_team = away_name

        news.home_country = home_country
        news.away_country = away_country

        news.home_flag = home_flag
        news.away_flag = away_flag

        news.home_goals = home_goals
        news.away_goals = away_goals

        news.goals = goals
        news.assists = assists

        news.yellow_cards = []
        news.red_cards = []

        news.cards = cards

        news.statistics = statistics

        news.lineups = []

        news.coaches = {}

        news.tournament = league_name
        news.league = league_name
        news.league_country = league_country
        news.league_logo = league_logo

        news.stage = (
            fixture.get("stage")
            or self._get(
                league,
                "round",
                default=""
            )
            or ""
        )

        news.stadium = self._safe_text(
            stadium
        )

        news.referee = self._safe_text(
            referee
        )

        news.match_date = (
            self._format_tehran_date(
                timestamp
            )
        )

        news.match_time = (
            self._format_tehran_time(
                timestamp
            )
        )

        news.match_phase = "result"

        # -------------------------------------------------
        # IMPORTANT:
        # Match Post directly consumes these fields.
        # -------------------------------------------------

        news.match_info = {
            "home": home_name,
            "away": away_name,

            "home_goals": home_goals,
            "away_goals": away_goals,

            "home_country": home_country,
            "away_country": away_country,

            "home_flag": home_flag,
            "away_flag": away_flag,
        }

        return news

    # =====================================================
    # Lineup News
    # =====================================================

    def _make_lineup_news(
        self,
        info: Dict[str, Any],
        fixture: Dict[str, Any],
    ) -> Optional[RawNews]:

        home = info.get("home") or {}
        away = info.get("away") or {}

        home_name = self._safe_text(
            home.get("name")
        )

        away_name = self._safe_text(
            away.get("name")
        )

        if not home_name or not away_name:
            return None

        timestamp = (
            info.get("timestamp")
        )

        league = (
            info.get("league")
            or fixture.get("league")
            or {}
        )

        if isinstance(league, dict):
            league_name = (
                league.get("name")
                or league.get("league")
                or ""
            )

            league_country = (
                league.get("country")
                or ""
            )

            league_logo = (
                league.get("logo")
                or ""
            )
        else:
            league_name = self._safe_text(
                league
            )
            league_country = ""
            league_logo = ""

        home_country = (
            self._safe_text(
                home.get("country")
            )
        )

        away_country = (
            self._safe_text(
                away.get("country")
            )
        )

        # -------------------------------------------------
        # FIX:
        # پرچم واقعی تیم‌ها را همین‌جا تولید می‌کنیم
        # -------------------------------------------------

        home_flag = (
            self._safe_text(
                home.get("flag")
            )
            or self._country_flag(
                home_country
            )
        )

        away_flag = (
            self._safe_text(
                away.get("flag")
            )
            or self._country_flag(
                away_country
            )
        )

        lineups = (
            info.get("lineups")
            or fixture.get("lineups")
            or fixture.get("rosters")
            or []
        )

        venue = (
            info.get("stadium")
            or fixture.get("stadium")
            or ""
        )

        referee = (
            info.get("referee")
            or fixture.get("referee")
            or ""
        )

        event_id = (
            info.get("event_id")
            or fixture.get("id")
            or fixture.get("event_id")
        )

        news = RawNews(
            title=(
                f"ترکیب اصلی {home_name} و {away_name} اعلام شد"
            ),

            content="",

            summary="",

            url=(
                fixture.get("url")
                or ""
            ),

            image_url="",

            author="ESPN",

            published_at=(
                self._parse_timestamp(timestamp)
                or datetime.now(
                    timezone.utc
                )
            ),

            fetched_at=datetime.now(
                timezone.utc
            ),

            source="ESPN",

            source_id="espn",

            country="US",

            language="en",

            category="sport",

            tags=[
                "football",
                "sport",
            ],

            related_urls=[],

            raw_data=fixture,
        )

        # =================================================
        # Football metadata
        # =================================================

        news.sport = "football"
        news.sport_name = "فوتبال"
        news.sport_emoji = "⚽"
        news.sport_hashtag = "#فوتبال"

        news.home_team = home_name
        news.away_team = away_name

        news.home_country = home_country
        news.away_country = away_country

        news.home_flag = home_flag
        news.away_flag = away_flag

        news.home_goals = None
        news.away_goals = None

        news.goals = []
        news.assists = []

        news.yellow_cards = []
        news.red_cards = []

        news.cards = []

        news.statistics = (
            fixture.get("statistics")
            or []
        )

        news.lineups = lineups

        news.coaches = (
            fixture.get("coaches")
            or {}
        )

        news.tournament = league_name
        news.league = league_name
        news.league_country = league_country
        news.league_logo = league_logo

        news.stage = (
            fixture.get("stage")
            or self._get(
                league,
                "round",
                default=""
            )
            or ""
        )

        news.stadium = self._safe_text(
            venue
        )

        news.referee = self._safe_text(
            referee
        )

        news.match_date = (
            self._format_tehran_date(
                timestamp
            )
        )

        news.match_time = (
            self._format_tehran_time(
                timestamp
            )
        )

        news.match_phase = "lineup"

        # -------------------------------------------------
        # IMPORTANT:
        # Match Post uses these exact keys.
        # -------------------------------------------------

        news.match_info = {
            "home": home_name,
            "away": away_name,

            "home_country": home_country,
            "away_country": away_country,

            "home_flag": home_flag,
            "away_flag": away_flag,

            "home_goals": "",
            "away_goals": "",
        }

        return news

    # =====================================================
    # Main fetch
    # =====================================================

    async def fetch(self) -> List[RawNews]:

        now_utc = datetime.now(
            timezone.utc
        )

        if now_utc.hour not in ACTIVE_HOURS_UTC:
            logger.debug(
                "Sports API outside active hours; skipped."
            )
            return []

        today = now_utc.strftime(
            "%Y-%m-%d"
        )

        fixtures = await self.client.get_finished_fixtures(
            today
        )

        if not fixtures:
            logger.info(
                "Sports API: no fixtures found for %s",
                today,
            )
            return []

        results: List[RawNews] = []

        # =================================================
        # Lineup detection
        # =================================================

        for fixture in fixtures:

            try:

                lineup_news = await self._maybe_lineup(
                    fixture
                )

                if lineup_news:
                    results.append(
                        lineup_news
                    )

            except Exception as exc:

                logger.exception(
                    "Lineup processing error: %s",
                    exc,
                )

        # =================================================
        # Finished matches
        # =================================================

        for fixture in fixtures:

            try:

                info = self._extract_upcoming(
                    fixture
                )

                event_id = info.get(
                    "event_id"
                )

                if not event_id:
                    continue

                cache_key = f"result:{event_id}"

                cached = _cache.get(
                    cache_key
                )

                if cached:

                    cached_at = cached.get(
                        "timestamp",
                        0,
                    )

                    if (
                        time.time() - cached_at
                        < CACHE_TTL_SECONDS
                    ):
                        continue

                summary = await self.client.get_fixture_summary(
                    event_id
                )

                if summary:

                    fixture_data = copy.deepcopy(
                        summary
                    )

                    self._apply_info(
                        info,
                        fixture_data
                    )

                    fixture = fixture_data

                news = self._make_news(
                    info,
                    fixture
                )

                if not news:
                    continue

                _cache[cache_key] = {
                    "timestamp": time.time(),
                }

                results.append(
                    news
                )

            except Exception as exc:

                logger.exception(
                    "Result processing error: %s",
                    exc,
                )

        logger.info(
            "Sports API fetched %d football news.",
            len(results),
        )

        return results
