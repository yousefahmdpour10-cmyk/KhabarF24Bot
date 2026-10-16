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
from app.services.sports_api_client import EspnClient, FOLLOWED_LEAGUES
from app.utils.logger import logger

POLL_INTERVAL_SECONDS = 20 * 60
ACTIVE_HOURS_UTC = set(range(10, 24)) | {0, 1}
CACHE_TTL_SECONDS = 24 * 3600
TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))

# اگر True شود، بازیکنان ذخیره هم در پست می‌آیند (پست خیلی بلند می‌شود)
INCLUDE_SUBSTITUTES = False

# (اسم آمار در ESPN, برچسب فارسی)
STAT_LABELS = [
    ("possessionPct", "مالکیت توپ"),
    ("totalShots", "شوت"),
    ("shotsOnTarget", "شوت در چارچوب"),
    ("wonCorners", "کرنر"),
    ("foulsCommitted", "خطا"),
]

_ASSIST_RE = re.compile(r"Assisted by ([^.]+?)(?: with | following | after |\.|$)")

# حافظه‌ی مشترک بین چرخه‌ها (هر چرخه یک نمونه‌ی جدید fetcher ساخته می‌شود)
_cache: Dict[str, dict] = {}
_last_poll_at: Optional[float] = None
_shape_logged = False


def _to_int(value) -> Optional[int]:
    if isinstance(value, dict):
        value = value.get("displayValue", value.get("value"))
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _name_of(athlete: Optional[dict]) -> Optional[str]:
    athlete = athlete or {}
    return athlete.get("displayName") or athlete.get("fullName") or athlete.get("shortName")


class SportsApiFetcher(BaseFetcher):

    def __init__(self, source):
        super().__init__(source)
        self.client = EspnClient()

    async def fetch(self) -> List[RawNews]:

        await self._maybe_poll()
        self._prune()

        return [self._make_news(data) for data in _cache.values()]

    # ------------------------------------------------------------------
    # دریافت
    # ------------------------------------------------------------------

    async def _maybe_poll(self) -> None:
        global _last_poll_at

        now = datetime.now(timezone.utc)

        if now.hour not in ACTIVE_HOURS_UTC:
            return

        if (
            _last_poll_at is not None
            and time.monotonic() - _last_poll_at < POLL_INTERVAL_SECONDS
        ):
            return

        _last_poll_at = time.monotonic()

        # ESPN روزها را بر اساس ساعت آمریکا می‌شمارد؛ در ساعت‌های اول
        # روز UTC دیروز را هم می‌گیریم تا بازی‌های دیروقت گم نشوند.
        dates = [now.strftime("%Y%m%d")]
        if now.hour <= 5:
            dates.append((now - timedelta(days=1)).strftime("%Y%m%d"))

        for slug, league_name in FOLLOWED_LEAGUES.items():

            for date in dates:

                events = await self.client.get_scoreboard(slug, date)

                finished = 0

                for event in events:

                    data = self._extract(event, league_name)

                    if not data:
                        continue

                    finished += 1

                    if data["key"] in _cache:
                        continue

                    summary = await self.client.get_summary(slug, data["event_id"])

                    if summary:
                        self._log_shape_once(summary)
                        self._apply_summary(data, summary)

                    _cache[data["key"]] = data

                logger.info(
                    f"EspnFetcher: {league_name} {date} -> {len(events)} بازی، "
                    f"{finished} تمام‌شده"
                )

        logger.info(f"EspnFetcher: {len(_cache)} بازی در حافظه")

    @staticmethod
    def _prune() -> None:
        cutoff = time.time() - CACHE_TTL_SECONDS
        for key in [k for k, d in _cache.items() if d["found_at"] < cutoff]:
            del _cache[key]

    @staticmethod
    def _log_shape_once(summary: dict) -> None:
        """
        اولین بار ساختار واقعی پاسخ را در لاگ می‌نویسیم، تا اگر ESPN
        ساختار را فرق داده باشد، بتوانیم نگاشت را دقیق اصلاح کنیم.
        """
        global _shape_logged
        if _shape_logged:
            return
        _shape_logged = True

        try:
            rosters = summary.get("rosters") or []
            roster_keys = list(rosters[0].keys()) if rosters else []
            first_player = (
                list((rosters[0].get("roster") or [{}])[0].keys()) if rosters else []
            )
            teams = (summary.get("boxscore") or {}).get("teams") or []
            stat_names = [
                s.get("name") for s in (teams[0].get("statistics") or [])
            ][:20] if teams else []
            key_events = summary.get("keyEvents") or []
            sample_event = (key_events[0].get("text") or "")[:120] if key_events else ""

            logger.info(f"ESPN shape: summary keys = {list(summary.keys())}")
            logger.info(f"ESPN shape: roster keys = {roster_keys}, player keys = {first_player}")
            logger.info(f"ESPN shape: stat names = {stat_names}")
            logger.info(
                f"ESPN shape: keyEvents = {len(key_events)}, sample text = {sample_event!r}"
            )
        except Exception as e:
            logger.warning(f"ESPN shape log failed -> {e}")

    # ------------------------------------------------------------------
    # استخراج از لیست بازی‌ها
    # ------------------------------------------------------------------

    @staticmethod
    def _extract(event: dict, league_name: str) -> Optional[dict]:

        competitions = event.get("competitions") or []
        comp = competitions[0] if competitions else {}

        status = (comp.get("status") or event.get("status") or {}).get("type") or {}

        if not (status.get("completed") or status.get("state") == "post"):
            return None

        competitors = comp.get("competitors") or []
        home = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away = next((c for c in competitors if c.get("homeAway") == "away"), None)

        if not home or not away:
            return None

        home_name = (home.get("team") or {}).get("displayName")
        away_name = (away.get("team") or {}).get("displayName")
        home_goals = _to_int(home.get("score"))
        away_goals = _to_int(away.get("score"))

        if not home_name or not away_name:
            return None
        if home_goals is None or away_goals is None:
            return None

        home_id = str((home.get("team") or {}).get("id", ""))
        away_id = str((away.get("team") or {}).get("id", ""))
        team_names = {home_id: home_name, away_id: away_name}

        title = f"{home_name} {home_goals}-{away_goals} {away_name}"
        result = f"{home_name} {home_goals} - {away_goals} {away_name}"

        status_name = (status.get("name") or "").upper()
        if "PEN" in status_name:
            pen_home = _to_int(home.get("shootoutScore"))
            pen_away = _to_int(away.get("shootoutScore"))
            if pen_home is not None and pen_away is not None:
                title += f" ({pen_home}-{pen_away} on penalties)"
                result += f" (پنالتی: {pen_home} - {pen_away})"
        elif "AET" in status_name or "EXTRA" in status_name:
            result += " (پس از وقت اضافه)"

        goals: List[str] = []
        yellow_cards: List[str] = []
        red_cards: List[str] = []

        for detail in comp.get("details") or []:

            if detail.get("shootout"):
                continue

            athletes = detail.get("athletesInvolved") or []
            player = _name_of(athletes[0]) if athletes else None
            player = player or "?"
            minute = (detail.get("clock") or {}).get("displayValue") or ""
            team = team_names.get(str((detail.get("team") or {}).get("id", "")), "")

            if detail.get("scoringPlay"):
                if detail.get("ownGoal"):
                    goals.append(f"{player} ({minute}) (o.g.)")
                else:
                    tag = " (pen.)" if detail.get("penaltyKick") else ""
                    goals.append(f"{player} ({minute}){tag} - {team}")

            elif detail.get("redCard"):
                red_cards.append(f"{player} ({minute}) - {team}")

            elif detail.get("yellowCard"):
                yellow_cards.append(f"{player} ({minute}) - {team}")

        match_date = match_time = None
        raw_date = event.get("date") or comp.get("date")
        if raw_date:
            try:
                dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                dt = dt.astimezone(TEHRAN_TZ)
                match_date = dt.strftime("%Y-%m-%d")
                match_time = dt.strftime("%H:%M")
            except ValueError:
                pass

        notes = comp.get("notes") or []
        stage = (notes[0].get("headline") if notes else None) or None

        event_id = str(event.get("id", ""))

        return {
            "key": f"{league_name}:{event_id}",
            "event_id": event_id,
            "found_at": time.time(),
            "home": home_name,
            "away": away_name,
            "home_id": home_id,
            "away_id": away_id,
            "home_goals": home_goals,
            "away_goals": away_goals,
            "title": title,
            "result": result,
            "league": league_name,
            "stage": stage,
            "stadium": (comp.get("venue") or {}).get("fullName"),
            "referee": None,
            "match_date": match_date,
            "match_time": match_time,
            "goals": goals,
            "assists": [],
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
            "lineup": None,
            "coach": None,
            "stats": [],
        }

    # ------------------------------------------------------------------
    # تکمیل با گزارش کامل بازی
    # ------------------------------------------------------------------

    @classmethod
    def _apply_summary(cls, data: dict, summary: dict) -> None:
        # هر بخش مستقل است؛ اگر یکی ساختار غیرمنتظره داشت، بقیه خراب نشوند
        for part in (cls._apply_info, cls._apply_rosters, cls._apply_stats, cls._apply_assists):
            try:
                part(data, summary)
            except Exception as e:
                logger.warning(f"EspnFetcher: بخش {part.__name__} ناموفق -> {e}")

    @staticmethod
    def _apply_info(data: dict, summary: dict) -> None:
        info = summary.get("gameInfo") or {}

        officials = info.get("officials") or []
        for official in officials:
            position = ((official.get("position") or {}).get("displayName") or "").lower()
            if "referee" in position and "assistant" not in position and "var" not in position:
                data["referee"] = official.get("fullName") or official.get("displayName")
                break

        if not data["stadium"]:
            data["stadium"] = (info.get("venue") or {}).get("fullName")

    @staticmethod
    def _apply_rosters(data: dict, summary: dict) -> None:

        lineup: Dict[str, dict] = {}

        for roster in summary.get("rosters") or []:

            side = roster.get("homeAway")
            if side not in ("home", "away"):
                continue

            def place(entry: dict) -> int:
                try:
                    return int(entry.get("formationPlace"))
                except (TypeError, ValueError):
                    return 99

            players = roster.get("roster") or []
            starters = sorted(
                [p for p in players if p.get("starter")], key=place
            )

            def line(entry: dict) -> Optional[str]:
                athlete = entry.get("athlete") or {}
                name = _name_of(athlete)
                if not name:
                    return None
                jersey = entry.get("jersey") or athlete.get("jersey")
                return f"{jersey} {name}" if jersey else name

            starting = [l for l in (line(p) for p in starters) if l]

            substitutes: List[str] = []
            if INCLUDE_SUBSTITUTES:
                substitutes = [
                    l for l in (
                        line(p) for p in players if not p.get("starter")
                    ) if l
                ]

            team_name = (roster.get("team") or {}).get("displayName") or data[side]

            formation = roster.get("formation")
            if isinstance(formation, dict):
                formation = formation.get("summary") or formation.get("name")
            if formation:
                team_name = f"{team_name} ({formation})"

            if starting:
                lineup[side] = {
                    "name": team_name,
                    "starting": starting,
                    "substitutes": substitutes,
                }

        if lineup:
            data["lineup"] = lineup

    @staticmethod
    def _apply_stats(data: dict, summary: dict) -> None:

        by_side: Dict[str, Dict[str, str]] = {}

        for team in (summary.get("boxscore") or {}).get("teams") or []:

            team_id = str((team.get("team") or {}).get("id", ""))
            side = team.get("homeAway")
            if side not in ("home", "away"):
                side = "home" if team_id == data["home_id"] else (
                    "away" if team_id == data["away_id"] else None
                )
            if not side:
                continue

            by_side[side] = {
                s.get("name"): s.get("displayValue")
                for s in team.get("statistics") or []
            }

        home = by_side.get("home")
        away = by_side.get("away")

        if not home or not away:
            return

        lines = []

        for key, label in STAT_LABELS:

            home_value = home.get(key)
            away_value = away.get(key)

            if home_value in (None, "") and away_value in (None, ""):
                continue

            def fmt(value) -> str:
                if value in (None, ""):
                    return "0"
                value = str(value)
                if key == "possessionPct" and not value.endswith("%"):
                    value += "%"
                return value

            lines.append(f"{label}: {fmt(home_value)} - {fmt(away_value)}")

        data["stats"] = lines

    @staticmethod
    def _apply_assists(data: dict, summary: dict) -> None:
        """
        ESPN پاس‌دهنده را جدا نمی‌دهد؛ در متن رویداد گل می‌آید
        ("... Assisted by X."). از همان متن بیرون می‌کشیم.
        """

        for event in summary.get("keyEvents") or []:

            kind = ((event.get("type") or {}).get("text") or "").lower()
            if "goal" not in kind or "own" in kind:
                continue

            match = _ASSIST_RE.search(event.get("text") or "")
            if not match:
                continue

            minute = (event.get("clock") or {}).get("displayValue") or ""
            team = (event.get("team") or {}).get("displayName") or ""
            data["assists"].append(f"{match.group(1).strip()} ({minute}) - {team}")

    # ------------------------------------------------------------------
    # ساخت RawNews
    # ------------------------------------------------------------------

    def _make_news(self, data: dict) -> RawNews:
        """
        هر بار یک RawNews «تازه» می‌سازیم، چون pipeline عنوان و خلاصه را
        تغییر می‌دهد و نباید نسخه‌ی تغییرکرده دوباره استفاده شود.
        """

        summary = (
            f"Full-time in the {data['league']}: "
            f"{data['home']} {data['home_goals']}-{data['away_goals']} {data['away']}."
        )
        if data["goals"]:
            summary += " Goals: " + "; ".join(data["goals"]) + "."

        news = RawNews(
            source_id="espn_matches",
            source="ESPN",
            title=data["title"],
            summary=summary,
            language="en",
        )

        # fetcher از رشته‌ی ورزشی مطمئن است؛ SportDetector نباید آن را عوض کند
        news.sport = "football"
        news.sport_name = "فوتبال"
        news.sport_emoji = "⚽"
        news.sport_hashtag = "#فوتبال"
        # تا main.py این را «خبر ورزشی» حساب کند
        news.category = "sport"

        # اسم این فیلدها دقیقاً همان‌هایی است که builder های فوتبال می‌خوانند
        news.result = data["result"]
        news.goals = list(data["goals"])
        news.assists = list(data["assists"])
        news.yellow_cards = list(data["yellow_cards"])
        news.red_cards = list(data["red_cards"])
        news.lineup = copy.deepcopy(data["lineup"])
        news.coach = data["coach"]
        news.stats = list(data["stats"])
        news.tournament = data["league"]
        news.league = data["league"]
        news.stage = data["stage"]
        news.stadium = data["stadium"]
        news.referee = data["referee"]
        news.match_date = data["match_date"]
        news.match_time = data["match_time"]

        news.source_category_hint = getattr(self.source, "categories", None)

        return news
