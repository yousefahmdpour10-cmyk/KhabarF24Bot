"""
Sports Fetcher (ESPN)

نتیجه‌ی بازی‌های تمام‌شده‌ی لیگ‌های دنبال‌شده را با جزئیات می‌گیرد:
گلزنان، پاس گل، کارت‌ها، ترکیب، آمار و داور.

- هر ~۲۰ دقیقه و فقط در ساعت‌های فعال بازی‌ها لیگ‌ها را چک می‌کنیم؛
- گلزنان و کارت‌ها از خود لیست بازی‌ها می‌آیند، و برای هر بازی
  «تازه‌تمام‌شده» یک درخواست گزارش کامل (ترکیب، آمار، داور) می‌زنیم؛
- نتیجه‌ی بازی‌های پیداشده در حافظه می‌ماند و هر چرخه دوباره به
  pipeline داده می‌شود. تکراری‌ها را DuplicateChecker حذف می‌کند و اگر
  ترجمه‌ی AI شکست بخورد، همان بازی چرخه‌ی بعد دوباره امتحان می‌شود.
"""

import copy
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.services.sports_api_client import EspnClient, FOLLOWED_LEAGUES, STATS
from app.utils.logger import logger


POLL_INTERVAL_SECONDS = 20 * 60
ACTIVE_HOURS_UTC = set(range(10, 24)) | {0, 1}
CACHE_TTL_SECONDS = 24 * 3600

# بازی‌ای که بیشتر از این از شروعش گذشته باشد دیگر خبر نیست
MAX_MATCH_AGE_SECONDS = 36 * 3600

TEHRAN_TZ = timezone(
    timedelta(hours=3, minutes=30)
)

# اگر True شود، بازیکنان ذخیره هم در پست می‌آیند
# (پست خیلی بلند می‌شود)
INCLUDE_SUBSTITUTES = False

# ترکیب اصلی در یک پست جدا «قبل از بازی» می‌آید؛ پس در پست نتیجه
# تکرار نمی‌شود.
INCLUDE_LINEUP_IN_RESULT = False

# ESPN ترکیب اصلی را حدود یک ساعت قبل از شروع در گزارش بازی می‌گذارد.
LINEUP_WINDOW_SECONDS = 95 * 60

# حداکثر این‌قدر از شروع بازی گذشته باشد
# تا پست ترکیب هنوز ارسال شود.
LINEUP_LATE_SECONDS = 10 * 60

# هر تیم حداقل این‌قدر بازیکن اصلی داشته باشد
# تا «ترکیب اعلام‌شده» حساب شود.
MIN_STARTERS = 9

# پست ترکیب بعد از این مدت از شروع بازی دیگر ارسال نمی‌شود
LINEUP_EXPIRY_AFTER_KICKOFF_SECONDS = 2 * 3600


# (اسم آمار در ESPN, برچسب فارسی)
STAT_LABELS = [
    ("possessionPct", "مالکیت توپ"),
    ("totalShots", "شوت"),
    ("shotsOnTarget", "شوت در چارچوب"),
    ("wonCorners", "کرنر"),
    ("foulsCommitted", "خطا"),
]


_ASSIST_RE = re.compile(
    r"Assisted by ([^.]+?)(?: with | following | after |\.|$)"
)


# حافظه‌ی مشترک بین چرخه‌ها
# (هر چرخه یک نمونه‌ی جدید fetcher ساخته می‌شود)
_cache: Dict[str, dict] = {}

_last_poll_at: Optional[float] = None

_shape_logged = False

_last_poll_summary: Optional[str] = None


def _to_int(value) -> Optional[int]:
    if isinstance(value, dict):
        value = value.get(
            "displayValue",
            value.get("value"),
        )

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _name_of(
    athlete: Optional[dict],
) -> Optional[str]:

    athlete = athlete or {}

    return (
        athlete.get("displayName")
        or athlete.get("fullName")
        or athlete.get("shortName")
    )


def _extract_team_country(
    competitor: Optional[dict],
) -> str:
    """
    کشور تیم را از داده ESPN استخراج می‌کند.

    چون ساختار پاسخ ESPN ممکن است بسته به endpoint
    کمی متفاوت باشد، چند مسیر احتمالی بررسی می‌شود.

    اگر کشور پیدا نشود، رشته خالی برمی‌گردد.
    در این حالت Formatter می‌تواند از fallback خودش
    استفاده کند.

    این تابع عمداً از روی نام تیم کشور را حدس نمی‌زند.
    """

    competitor = competitor or {}

    team = competitor.get("team") or {}

    candidates = [
        competitor.get("country"),
        competitor.get("countryCode"),
        competitor.get("locationCountry"),
        competitor.get("teamCountry"),
        competitor.get("teamCountryCode"),

        team.get("country"),
        team.get("countryCode"),
        team.get("locationCountry"),
        team.get("teamCountry"),
        team.get("teamCountryCode"),
    ]

    for value in candidates:

        if isinstance(value, dict):
            value = (
                value.get("abbreviation")
                or value.get("code")
                or value.get("name")
                or value.get("displayName")
            )

        value = str(
            value or ""
        ).strip()

        if value:
            return value

    return ""


class SportsApiFetcher(BaseFetcher):

    def __init__(self, source):
        super().__init__(source)
        self.client = EspnClient()

    async def fetch(self) -> List[RawNews]:

        await self._maybe_poll()
        self._prune()

        logger.info(
            f"EspnFetcher: cached={len(_cache)} | last poll: "
            f"{_last_poll_summary or 'not run yet (outside 10:00-01:59 UTC, or waiting)'}"
        )

        return [
            self._make_news(data)
            for data in _cache.values()
        ]

    # ------------------------------------------------------------------
    # دریافت
    # ------------------------------------------------------------------

    async def _maybe_poll(self) -> None:

        global _last_poll_at
        global _last_poll_summary

        now = datetime.now(timezone.utc)

        if now.hour not in ACTIVE_HOURS_UTC:
            return

        if (
            _last_poll_at is not None
            and time.monotonic() - _last_poll_at
            < POLL_INTERVAL_SECONDS
        ):
            return

        _last_poll_at = time.monotonic()

        # فقط بازی‌های «تمام‌شده» را می‌خواهیم.
        # همیشه امروز و دیروز را می‌گیریم.
        dates = [
            now.strftime("%Y%m%d"),
            (now - timedelta(days=1)).strftime("%Y%m%d"),
        ]

        before = dict(STATS)

        total_events = 0
        total_finished = 0
        new_matches = 0
        new_lineups = 0

        for slug, league_name in FOLLOWED_LEAGUES.items():

            for date in dates:

                events = await self.client.get_scoreboard(
                    slug,
                    date,
                )

                total_events += len(events)

                finished = 0

                for event in events:

                    data = self._extract(
                        event,
                        league_name,
                    )

                    if not data:

                        # بازی هنوز تمام نشده:
                        # شاید ترکیب اصلی اعلام شده باشد.
                        if await self._maybe_lineup(
                            slug,
                            league_name,
                            event,
                        ):
                            new_lineups += 1

                        continue

                    finished += 1

                    age = (
                        time.time()
                        - data.get(
                            "kickoff_ts",
                            data["found_at"],
                        )
                    )

                    if age > MAX_MATCH_AGE_SECONDS:
                        continue

                    if data["key"] in _cache:
                        continue

                    summary = await self.client.get_summary(
                        slug,
                        data["event_id"],
                    )

                    if summary:
                        self._log_shape_once(
                            summary
                        )

                        self._apply_summary(
                            data,
                            summary,
                        )

                    _cache[data["key"]] = data

                    new_matches += 1

                total_finished += finished

                logger.info(
                    f"EspnFetcher: {league_name} {date} -> "
                    f"{len(events)} بازی، "
                    f"{finished} تمام‌شده"
                )

        requests = {
            key: value - before.get(key, 0)
            for key, value in STATS.items()
            if value - before.get(key, 0)
        }

        _last_poll_summary = (
            f"events={total_events}, "
            f"finished={total_finished}, "
            f"new={new_matches}, "
            f"lineups={new_lineups}, "
            f"requests={requests}"
        )

        logger.info(
            f"EspnFetcher: poll done | "
            f"{_last_poll_summary} | "
            f"cached={len(_cache)}"
        )

    # ------------------------------------------------------------------
    # ترکیب قبل از بازی
    # ------------------------------------------------------------------

    async def _maybe_lineup(
        self,
        slug: str,
        league_name: str,
        event: dict,
    ) -> bool:
        """
        اگر بازی نزدیک است و ترکیب اصلی دو تیم اعلام شده،
        یک «پست ترکیب» می‌سازد.
        """

        base = self._extract_upcoming(
            event,
            league_name,
        )

        if not base:
            return False

        key = (
            f"lineup:"
            f"{league_name}:"
            f"{base['event_id']}"
        )

        if (
            key in _cache
            or f"{league_name}:{base['event_id']}"
            in _cache
        ):
            return False

        until_kickoff = (
            base["kickoff_ts"]
            - time.time()
        )

        if not (
            -LINEUP_LATE_SECONDS
            <= until_kickoff
            <= LINEUP_WINDOW_SECONDS
        ):
            return False

        summary = await self.client.get_summary(
            slug,
            base["event_id"],
        )

        if not summary:
            return False

        self._log_shape_once(
            summary
        )

        for part in (
            self._apply_info,
            self._apply_rosters,
        ):
            try:
                part(
                    base,
                    summary,
                )
            except Exception as e:
                logger.warning(
                    f"EspnFetcher: بخش "
                    f"{part.__name__} ناموفق -> {e}"
                )

        lineup = base.get("lineup") or {}

        ready = all(
            len(
                (
                    lineup.get(side)
                    or {}
                ).get("starting")
                or []
            )
            >= MIN_STARTERS
            for side in (
                "home",
                "away",
            )
        )

        if not ready:
            return False

        base["key"] = key
        base["kind"] = "lineup"

        _cache[key] = base

        logger.info(
            "EspnFetcher: ترکیب اصلی اعلام شد -> "
            f"{base['home']} - {base['away']}"
        )

        return True

    # ------------------------------------------------------------------
    # استخراج بازی آینده
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_upcoming(
        event: dict,
        league_name: str,
    ) -> Optional[dict]:
        """
        بازی‌ای که هنوز شروع نشده
        یا تازه شروع شده.
        """

        competitions = (
            event.get("competitions")
            or []
        )

        comp = (
            competitions[0]
            if competitions
            else {}
        )

        status = (
            comp.get("status")
            or event.get("status")
            or {}
        ).get("type") or {}

        if (
            status.get("completed")
            or status.get("state")
            not in ("pre", "in")
        ):
            return None

        competitors = (
            comp.get("competitors")
            or []
        )

        home = next(
            (
                c
                for c in competitors
                if c.get("homeAway")
                == "home"
            ),
            None,
        )

        away = next(
            (
                c
                for c in competitors
                if c.get("homeAway")
                == "away"
            ),
            None,
        )

        if not home or not away:
            return None

        home_team = (
            home.get("team")
            or {}
        )

        away_team = (
            away.get("team")
            or {}
        )

        home_name = (
            home_team.get(
                "displayName"
            )
        )

        away_name = (
            away_team.get(
                "displayName"
            )
        )

        if not home_name or not away_name:
            return None

        home_country = _extract_team_country(
            home
        )

        away_country = _extract_team_country(
            away
        )

        kickoff_ts = None
        match_date = None
        match_time = None

        raw_date = (
            event.get("date")
            or comp.get("date")
        )

        if raw_date:

            try:
                dt = datetime.fromisoformat(
                    raw_date.replace(
                        "Z",
                        "+00:00",
                    )
                )

                kickoff_ts = dt.timestamp()

                dt = dt.astimezone(
                    TEHRAN_TZ
                )

                match_date = dt.strftime(
                    "%Y-%m-%d"
                )

                match_time = dt.strftime(
                    "%H:%M"
                )

            except ValueError:
                pass

        if kickoff_ts is None:
            return None

        notes = (
            comp.get("notes")
            or []
        )

        return {
            "event_id": str(
                event.get("id", "")
            ),

            "found_at": time.time(),

            "kickoff_ts": kickoff_ts,

            "home": home_name,
            "away": away_name,

            "home_id": str(
                home_team.get(
                    "id",
                    "",
                )
            ),

            "away_id": str(
                away_team.get(
                    "id",
                    "",
                )
            ),

            # کشور واقعی تیم، اگر ESPN ارائه کند
            "home_country": home_country,
            "away_country": away_country,

            "league": league_name,

            "stage": (
                notes[0].get(
                    "headline"
                )
                if notes
                else None
            )
            or None,

            "stadium": (
                comp.get("venue")
                or {}
            ).get("fullName"),

            "referee": None,

            "match_date": match_date,
            "match_time": match_time,

            "lineup": None,
            "coach": None,
        }

    # ------------------------------------------------------------------
    # پاک‌سازی حافظه
    # ------------------------------------------------------------------

    @staticmethod
    def _prune() -> None:

        now = time.time()

        cutoff = (
            now
            - MAX_MATCH_AGE_SECONDS
        )

        for key, data in list(
            _cache.items()
        ):

            kickoff = data.get(
                "kickoff_ts",
                data["found_at"],
            )

            if kickoff < cutoff:
                del _cache[key]

            elif data.get(
                "kind"
            ) == "lineup":

                result_key = (
                    f"{data['league']}:"
                    f"{data['event_id']}"
                )

                if (
                    result_key in _cache
                    or now
                    > kickoff
                    + LINEUP_EXPIRY_AFTER_KICKOFF_SECONDS
                ):
                    del _cache[key]

    # ------------------------------------------------------------------
    # ثبت ساختار ESPN در لاگ
    # ------------------------------------------------------------------

    @staticmethod
    def _log_shape_once(
        summary: dict,
    ) -> None:

        global _shape_logged

        if _shape_logged:
            return

        _shape_logged = True

        try:

            rosters = (
                summary.get(
                    "rosters"
                )
                or []
            )

            roster_keys = (
                list(
                    rosters[0].keys()
                )
                if rosters
                else []
            )

            first_player = (
                list(
                    (
                        rosters[0].get(
                            "roster"
                        )
                        or [{}]
                    )[0].keys()
                )
                if rosters
                else []
            )

            teams = (
                summary.get(
                    "boxscore"
                )
                or {}
            ).get(
                "teams"
            ) or []

            stat_names = [
                s.get("name")
                for s in (
                    teams[0].get(
                        "statistics"
                    )
                    or []
                )
            ][:20] if teams else []

            key_events = (
                summary.get(
                    "keyEvents"
                )
                or []
            )

            sample_event = (
                (
                    key_events[0].get(
                        "text"
                    )
                    or ""
                )[:120]
                if key_events
                else ""
            )

            logger.info(
                "ESPN shape: "
                f"summary keys = "
                f"{list(summary.keys())}"
            )

            logger.info(
                "ESPN shape: "
                f"roster keys = "
                f"{roster_keys}, "
                f"player keys = "
                f"{first_player}"
            )

            logger.info(
                "ESPN shape: "
                f"stat names = "
                f"{stat_names}"
            )

            logger.info(
                "ESPN shape: "
                f"keyEvents = "
                f"{len(key_events)}, "
                f"sample text = "
                f"{sample_event!r}"
            )

        except Exception as e:

            logger.warning(
                f"ESPN shape log failed -> {e}"
            )

    # ------------------------------------------------------------------
    # استخراج بازی تمام‌شده
    # ------------------------------------------------------------------

    @staticmethod
    def _extract(
        event: dict,
        league_name: str,
    ) -> Optional[dict]:

        competitions = (
            event.get(
                "competitions"
            )
            or []
        )

        comp = (
            competitions[0]
            if competitions
            else {}
        )

        status = (
            comp.get("status")
            or event.get("status")
            or {}
        ).get("type") or {}

        if not (
            status.get("completed")
            or status.get("state")
            == "post"
        ):
            return None

        competitors = (
            comp.get(
                "competitors"
            )
            or []
        )

        home = next(
            (
                c
                for c in competitors
                if c.get("homeAway")
                == "home"
            ),
            None,
        )

        away = next(
            (
                c
                for c in competitors
                if c.get("homeAway")
                == "away"
            ),
            None,
        )

        if not home or not away:
            return None

        home_team = (
            home.get("team")
            or {}
        )

        away_team = (
            away.get("team")
            or {}
        )

        home_name = (
            home_team.get(
                "displayName"
            )
        )

        away_name = (
            away_team.get(
                "displayName"
            )
        )

        home_goals = _to_int(
            home.get("score")
        )

        away_goals = _to_int(
            away.get("score")
        )

        if not home_name or not away_name:
            return None

        if (
            home_goals is None
            or away_goals is None
        ):
            return None

        home_id = str(
            home_team.get(
                "id",
                "",
            )
        )

        away_id = str(
            away_team.get(
                "id",
                "",
            )
        )

        # کشور تیم‌ها
        home_country = (
            _extract_team_country(
                home
            )
        )

        away_country = (
            _extract_team_country(
                away
            )
        )

        team_names = {
            home_id: home_name,
            away_id: away_name,
        }

        title = (
            f"{home_name} "
            f"{home_goals}-"
            f"{away_goals} "
            f"{away_name}"
        )

        result = (
            f"{home_name} "
            f"{home_goals} - "
            f"{away_goals} "
            f"{away_name}"
        )

        status_name = (
            status.get(
                "name"
            )
            or ""
        ).upper()

        if "PEN" in status_name:

            pen_home = _to_int(
                home.get(
                    "shootoutScore"
                )
            )

            pen_away = _to_int(
                away.get(
                    "shootoutScore"
                )
            )

            if (
                pen_home is not None
                and pen_away is not None
            ):

                title += (
                    f" ({pen_home}-"
                    f"{pen_away} "
                    f"on penalties)"
                )

                result += (
                    f" (پنالتی: "
                    f"{pen_home} - "
                    f"{pen_away})"
                )

        elif (
            "AET"
            in status_name
            or "EXTRA"
            in status_name
        ):

            result += (
                " (پس از وقت اضافه)"
            )

        goals: List[str] = []

        yellow_cards: List[str] = []

        red_cards: List[str] = []

        for detail in (
            comp.get(
                "details"
            )
            or []
        ):

            if detail.get(
                "shootout"
            ):
                continue

            athletes = (
                detail.get(
                    "athletesInvolved"
                )
                or []
            )

            player = (
                _name_of(
                    athletes[0]
                )
                if athletes
                else None
            )

            player = (
                player
                or "بازیکن نامشخص"
            )

            minute = (
                (
                    detail.get(
                        "clock"
                    )
                    or {}
                ).get(
                    "displayValue"
                )
                or ""
            )

            team = team_names.get(
                str(
                    (
                        detail.get(
                            "team"
                        )
                        or {}
                    ).get(
                        "id",
                        "",
                    )
                ),
                "",
            )

            if detail.get(
                "scoringPlay"
            ):

                if detail.get(
                    "ownGoal"
                ):

                    goals.append(
                        f"{player} "
                        f"({minute}) "
                        f"(o.g.)"
                    )

                else:

                    tag = (
                        " (pen.)"
                        if detail.get(
                            "penaltyKick"
                        )
                        else ""
                    )

                    goals.append(
                        f"{player} "
                        f"({minute})"
                        f"{tag} - "
                        f"{team}"
                    )

            elif detail.get(
                "redCard"
            ):

                red_cards.append(
                    f"{player} "
                    f"({minute}) - "
                    f"{team}"
                )

            elif detail.get(
                "yellowCard"
            ):

                yellow_cards.append(
                    f"{player} "
                    f"({minute}) - "
                    f"{team}"
                )

        match_date = None
        match_time = None
        kickoff_ts = None

        raw_date = (
            event.get("date")
            or comp.get("date")
        )

        if raw_date:

            try:

                dt = datetime.fromisoformat(
                    raw_date.replace(
                        "Z",
                        "+00:00",
                    )
                )

                kickoff_ts = (
                    dt.timestamp()
                )

                dt = dt.astimezone(
                    TEHRAN_TZ
                )

                match_date = (
                    dt.strftime(
                        "%Y-%m-%d"
                    )
                )

                match_time = (
                    dt.strftime(
                        "%H:%M"
                    )
                )

            except ValueError:
                pass

        notes = (
            comp.get(
                "notes"
            )
            or []
        )

        stage = (
            (
                notes[0].get(
                    "headline"
                )
                if notes
                else None
            )
            or None
        )

        event_id = str(
            event.get(
                "id",
                "",
            )
        )

        return {
            "key": (
                f"{league_name}:"
                f"{event_id}"
            ),

            "event_id": event_id,

            "found_at": time.time(),

            "kickoff_ts": (
                kickoff_ts
                or time.time()
            ),

            "home": home_name,
            "away": away_name,

            "home_id": home_id,
            "away_id": away_id,

            # اطلاعات کشور تیم
            "home_country": home_country,
            "away_country": away_country,

            "home_goals": home_goals,
            "away_goals": away_goals,

            "title": title,
            "result": result,

            "league": league_name,
            "stage": stage,

            "stadium": (
                comp.get(
                    "venue"
                )
                or {}
            ).get(
                "fullName"
            ),

            "referee": None,

            "match_date": match_date,
            "match_time": match_time,

            "goals": goals,

            "assists": [],

            "yellow_cards": (
                yellow_cards
            ),

            "red_cards": (
                red_cards
            ),

            "lineup": None,

            "coach": None,

            "stats": [],
        }

    # ------------------------------------------------------------------
    # تکمیل با گزارش کامل بازی
    # ------------------------------------------------------------------

    @classmethod
    def _apply_summary(
        cls,
        data: dict,
        summary: dict,
    ) -> None:

        # هر بخش مستقل است؛ اگر یکی ساختار
        # غیرمنتظره داشت، بقیه خراب نشوند.

        for part in (
            cls._apply_info,
            cls._apply_rosters,
            cls._apply_stats,
            cls._apply_assists,
        ):

            try:

                part(
                    data,
                    summary,
                )

            except Exception as e:

                logger.warning(
                    f"EspnFetcher: بخش "
                    f"{part.__name__} ناموفق -> {e}"
                )

    # ------------------------------------------------------------------
    # داور و ورزشگاه
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_info(
        data: dict,
        summary: dict,
    ) -> None:

        info = (
            summary.get(
                "gameInfo"
            )
            or {}
        )

        officials = (
            info.get(
                "officials"
            )
            or []
        )

        for official in officials:

            position = (
                (
                    official.get(
                        "position"
                    )
                    or {}
                ).get(
                    "displayName"
                )
                or ""
            ).lower()

            if (
                "referee"
                in position
                and "assistant"
                not in position
                and "var"
                not in position
            ):

                data["referee"] = (
                    official.get(
                        "fullName"
                    )
                    or official.get(
                        "displayName"
                    )
                )

                break

        if not data["stadium"]:

            data["stadium"] = (
                info.get(
                    "venue"
                )
                or {}
            ).get(
                "fullName"
            )

    # ------------------------------------------------------------------
    # ترکیب
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_rosters(
        data: dict,
        summary: dict,
    ) -> None:

        lineup: Dict[
            str,
            dict
        ] = {}

        for roster in (
            summary.get(
                "rosters"
            )
            or []
        ):

            side = roster.get(
                "homeAway"
            )

            if side not in (
                "home",
                "away",
            ):
                continue

            def place(
                entry: dict
            ) -> int:

                try:
                    return int(
                        entry.get(
                            "formationPlace"
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    return 99

            players = (
                roster.get(
                    "roster"
                )
                or []
            )

            starters = sorted(
                [
                    p
                    for p in players
                    if p.get(
                        "starter"
                    )
                ],
                key=place,
            )

            def line(
                entry: dict
            ) -> Optional[str]:

                athlete = (
                    entry.get(
                        "athlete"
                    )
                    or {}
                )

                name = _name_of(
                    athlete
                )

                if not name:
                    return None

                jersey = (
                    entry.get(
                        "jersey"
                    )
                    or athlete.get(
                        "jersey"
                    )
                )

                return (
                    f"{jersey} {name}"
                    if jersey
                    else name
                )

            starting = [
                l
                for l in (
                    line(p)
                    for p in starters
                )
                if l
            ]

            substitutes: List[
                str
            ] = []

            if INCLUDE_SUBSTITUTES:

                substitutes = [
                    l
                    for l in (
                        line(p)
                        for p in players
                        if not p.get(
                            "starter"
                        )
                    )
                    if l
                ]

            team_name = (
                (
                    roster.get(
                        "team"
                    )
                    or {}
                ).get(
                    "displayName"
                )
                or data[side]
            )

            formation = (
                roster.get(
                    "formation"
                )
            )

            if isinstance(
                formation,
                dict,
            ):

                formation = (
                    formation.get(
                        "summary"
                    )
                    or formation.get(
                        "name"
                    )
                )

            if formation:

                team_name = (
                    f"{team_name} "
                    f"({formation})"
                )

            if starting:

                lineup[side] = {
                    "name": team_name,
                    "starting": starting,
                    "substitutes": substitutes,
                }

        if lineup:
            data["lineup"] = lineup

    # ------------------------------------------------------------------
    # آمار
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_stats(
        data: dict,
        summary: dict,
    ) -> None:

        by_side: Dict[
            str,
            Dict[str, str]
        ] = {}

        for team in (
            (
                summary.get(
                    "boxscore"
                )
                or {}
            ).get(
                "teams"
            )
            or []
        ):

            team_id = str(
                (
                    team.get(
                        "team"
                    )
                    or {}
                ).get(
                    "id",
                    "",
                )
            )

            side = team.get(
                "homeAway"
            )

            if side not in (
                "home",
                "away",
            ):

                side = (
                    "home"
                    if team_id
                    == data["home_id"]
                    else (
                        "away"
                        if team_id
                        == data["away_id"]
                        else None
                    )
                )

            if not side:
                continue

            by_side[side] = {
                s.get("name"):
                    s.get("displayValue")
                for s in (
                    team.get(
                        "statistics"
                    )
                    or []
                )
            }

        home = by_side.get(
            "home"
        )

        away = by_side.get(
            "away"
        )

        if not home or not away:
            return

        lines = []

        for key, label in (
            STAT_LABELS
        ):

            home_value = (
                home.get(key)
            )

            away_value = (
                away.get(key)
            )

            if (
                home_value
                in (None, "")
                and
                away_value
                in (None, "")
            ):
                continue

            def fmt(value) -> str:

                if value in (
                    None,
                    "",
                ):
                    return "0"

                value = str(
                    value
                )

                if (
                    key
                    == "possessionPct"
                    and not value.endswith(
                        "%"
                    )
                ):
                    value += "%"

                return value

            lines.append(
                f"{label}: "
                f"{fmt(home_value)} - "
                f"{fmt(away_value)}"
            )

        data["stats"] = lines

    # ------------------------------------------------------------------
    # پاس گل
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_assists(
        data: dict,
        summary: dict,
    ) -> None:

        """
        ESPN پاس‌دهنده را جدا نمی‌دهد؛
        در متن رویداد گل می‌آید
        ("... Assisted by X.").
        از همان متن بیرون می‌کشیم.
        """

        for event in (
            summary.get(
                "keyEvents"
            )
            or []
        ):

            kind = (
                (
                    event.get(
                        "type"
                    )
                    or {}
                ).get(
                    "text"
                )
                or ""
            ).lower()

            if (
                "goal"
                not in kind
                or "own"
                in kind
            ):
                continue

            match = _ASSIST_RE.search(
                event.get(
                    "text"
                )
                or ""
            )

            if not match:
                continue

            minute = (
                (
                    event.get(
                        "clock"
                    )
                    or {}
                ).get(
                    "displayValue"
                )
                or ""
            )

            team = (
                (
                    event.get(
                        "team"
                    )
                    or {}
                ).get(
                    "displayName"
                )
                or ""
            )

            data["assists"].append(
                f"{match.group(1).strip()} "
                f"({minute}) - "
                f"{team}"
            )

    # ------------------------------------------------------------------
    # ساخت RawNews
    # ------------------------------------------------------------------

    def _make_news(
        self,
        data: dict,
    ) -> RawNews:

        """
        هر بار یک RawNews تازه می‌سازیم،
        چون pipeline عنوان و خلاصه را تغییر می‌دهد
        و نباید نسخه‌ی تغییرکرده دوباره استفاده شود.
        """

        if data.get(
            "kind"
        ) == "lineup":

            return self._make_lineup_news(
                data
            )

        summary = (
            f"Full-time in the "
            f"{data['league']}: "
            f"{data['home']} "
            f"{data['home_goals']}-"
            f"{data['away_goals']} "
            f"{data['away']}."
        )

        if data["goals"]:

            summary += (
                " Goals: "
                + "; ".join(
                    data["goals"]
                )
                + "."
            )

        news = RawNews(
            source_id="espn_matches",
            source="ESPN",
            title=data["title"],
            summary=summary,
            language="en",
        )

        # --------------------------------------------------------------
        # اطلاعات ورزشی
        # --------------------------------------------------------------

        news.sport = "football"
        news.sport_name = "فوتبال"
        news.sport_emoji = "⚽"
        news.sport_hashtag = "#فوتبال"

        # تا main.py این را «خبر ورزشی» حساب کند
        news.category = "sport"

        # --------------------------------------------------------------
        # اطلاعات بازی
        # --------------------------------------------------------------

        news.result = data["result"]

        news.goals = list(
            data["goals"]
        )

        news.assists = list(
            data["assists"]
        )

        news.yellow_cards = list(
            data["yellow_cards"]
        )

        news.red_cards = list(
            data["red_cards"]
        )

        news.lineup = (
            copy.deepcopy(
                data["lineup"]
            )
            if INCLUDE_LINEUP_IN_RESULT
            else None
        )

        news.coach = data["coach"]

        news.stats = list(
            data["stats"]
        )

        news.tournament = (
            data["league"]
        )

        news.league = (
            data["league"]
        )

        news.stage = (
            data["stage"]
        )

        news.stadium = (
            data["stadium"]
        )

        news.referee = (
            data["referee"]
        )

        news.match_date = (
            data["match_date"]
        )

        news.match_time = (
            data["match_time"]
        )

        # --------------------------------------------------------------
        # کشور تیم‌ها
        # --------------------------------------------------------------
        # این دو فیلد توسط match_post.py برای پرچم
        # استفاده می‌شوند.

        news.home_country = (
            data.get(
                "home_country",
                "",
            )
        )

        news.away_country = (
            data.get(
                "away_country",
                "",
            )
        )

        # --------------------------------------------------------------
        # اطلاعات منبع
        # --------------------------------------------------------------

        news.source_category_hint = (
            getattr(
                self.source,
                "categories",
                None,
            )
        )

        # --------------------------------------------------------------
        # زمان‌دار بودن خبر
        # --------------------------------------------------------------

        news.timely = True

        news.timely_key = (
            1,
            -data["kickoff_ts"],
        )

        news.skip_story_repeat = True

        return news

    # ------------------------------------------------------------------
    # ساخت پست ترکیب
    # ------------------------------------------------------------------

    def _make_lineup_news(
        self,
        data: dict,
    ) -> RawNews:

        """
        پست «ترکیب اصلی» قبل از بازی.
        """

        lineup = (
            data["lineup"]
            or {}
        )

        home_line = (
            (
                lineup.get(
                    "home"
                )
                or {}
            ).get(
                "name"
            )
            or data["home"]
        )

        away_line = (
            (
                lineup.get(
                    "away"
                )
                or {}
            ).get(
                "name"
            )
            or data["away"]
        )

        summary = (
            "Confirmed starting lineups "
            f"for {data['home']} "
            f"vs {data['away']} "
            f"in the {data['league']}"
        )

        if data.get(
            "stadium"
        ):

            summary += (
                f" at "
                f"{data['stadium']}"
            )

        if data.get(
            "match_time"
        ):

            summary += (
                f". Kick-off "
                f"{data['match_time']} "
                f"Tehran time"
            )

        summary += (
            ". Starting XI: "
            f"{home_line} "
            f"and "
            f"{away_line}."
        )

        news = RawNews(
            source_id="espn_matches",
            source="ESPN",
            title=(
                f"{data['home']} vs "
                f"{data['away']}: "
                f"confirmed starting lineups"
            ),
            summary=summary,
            language="en",
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
        # اطلاعات بازی
        # --------------------------------------------------------------

        news.result = ""

        news.goals = []

        news.assists = []

        news.yellow_cards = []

        news.red_cards = []

        news.lineup = copy.deepcopy(
            data["lineup"]
        )

        news.coach = data["coach"]

        news.stats = []

        news.tournament = (
            data["league"]
        )

        news.league = (
            data["league"]
        )

        news.stage = (
            data["stage"]
        )

        news.stadium = (
            data["stadium"]
        )

        news.referee = (
            data["referee"]
        )

        news.match_date = (
            data["match_date"]
        )

        news.match_time = (
            data["match_time"]
        )

        # --------------------------------------------------------------
        # کشور تیم‌ها
        # --------------------------------------------------------------

        news.home_country = (
            data.get(
                "home_country",
                "",
            )
        )

        news.away_country = (
            data.get(
                "away_country",
                "",
            )
        )

        # --------------------------------------------------------------
        # منبع
        # --------------------------------------------------------------

        news.source_category_hint = (
            getattr(
                self.source,
                "categories",
                None,
            )
        )

        # --------------------------------------------------------------
        # زمان‌دار بودن
        # --------------------------------------------------------------

        news.timely = True

        news.timely_key = (
            0,
            data["kickoff_ts"],
        )

        news.skip_story_repeat = True

        return news
