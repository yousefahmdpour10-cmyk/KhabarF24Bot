"""
Sports API Fetcher

نتیجه‌ی بازی‌های تمام‌شده‌ی لیگ‌های دنبال‌شده را با جزئیات می‌گیرد:
گلزنان، پاس گل، کارت‌ها، ترکیب، مربی و آمار.

چون پلن رایگان فقط ۱۰۰ درخواست در روز دارد:
- فقط هر ~۴۰ دقیقه و فقط در ساعت‌های فعال بازی‌ها به API درخواست می‌دهیم؛
- برای هر بازی حداکثر ۳ درخواست جزئیات می‌زنیم، به این ترتیب اولویت:
  رویدادها (گل/پاس/کارت) ← ترکیب و مربی ← آمار. اگر سهمیه تمام شود،
  بازی‌های بعدی فقط با همان چیزهایی که گرفته شده منتشر می‌شوند؛
- نتیجه‌ی بازی‌های پیداشده در حافظه می‌ماند و هر چرخه دوباره به pipeline
  داده می‌شود (بدون درخواست جدید). تکراری‌ها را DuplicateChecker حذف
  می‌کند و اگر ترجمه‌ی AI شکست بخورد، همان بازی چرخه‌ی بعد دوباره
  امتحان می‌شود.
"""

import copy
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.services.sports_api_client import SportsApiClient, budget_left
from app.utils.logger import logger

POLL_INTERVAL_SECONDS = 40 * 60
ACTIVE_HOURS_UTC = set(range(11, 24)) | {0, 1}
CACHE_TTL_SECONDS = 24 * 3600
RESERVED_REQUESTS = 6   # همیشه چند درخواست برای لیست بازی‌ها نگه می‌داریم
TEHRAN_TZ = timezone(timedelta(hours=3, minutes=30))

# اگر True شود، لیست بازیکنان ذخیره هم در پست می‌آید (پست خیلی بلند می‌شود)
INCLUDE_SUBSTITUTES = False

# آمارهایی که در پست نشان داده می‌شوند: (اسم در API, برچسب فارسی)
STAT_LABELS = [
    ("Ball Possession", "مالکیت توپ"),
    ("Total Shots", "شوت"),
    ("Shots on Goal", "شوت در چارچوب"),
    ("Corner Kicks", "کرنر"),
    ("Fouls", "خطا"),
]

_ROUND_RE = re.compile(r"(?:Regular Season|League Stage) - (\d+)", re.IGNORECASE)

# حافظه‌ی مشترک بین چرخه‌ها (هر چرخه یک نمونه‌ی جدید fetcher ساخته می‌شود)
_cache: Dict[int, dict] = {}
_last_poll_at: Optional[float] = None


def _minute_text(event: dict) -> str:
    info = event.get("time") or {}
    minute = info.get("elapsed")
    extra = info.get("extra")
    return f"{minute}+{extra}" if extra else f"{minute}"


class SportsApiFetcher(BaseFetcher):

    def __init__(self, source):
        super().__init__(source)
        self.client = SportsApiClient()

    async def fetch(self) -> List[RawNews]:

        await self._maybe_poll()
        self._prune()

        return [self._make_news(data) for data in _cache.values()]

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

        if budget_left() <= RESERVED_REQUESTS:
            logger.warning("SportsApiFetcher: سهمیه‌ی امروز تقریباً تمام است")
            return

        _last_poll_at = time.monotonic()

        dates = [now.strftime("%Y-%m-%d")]
        if now.hour <= 1:
            # بازی‌هایی که دیروز شروع شده و بعد از نیمه‌شب UTC تمام شده‌اند
            dates.append((now - timedelta(days=1)).strftime("%Y-%m-%d"))

        for date in dates:

            fixtures = await self.client.get_finished_fixtures(date)

            for fx in fixtures:

                data = self._extract(fx)

                if not data or data["fixture_id"] in _cache:
                    continue

                await self._enrich(data)
                _cache[data["fixture_id"]] = data

        logger.info(f"SportsApiFetcher: {len(_cache)} بازی در حافظه")

    @staticmethod
    def _prune() -> None:
        cutoff = time.time() - CACHE_TTL_SECONDS
        for fid in [f for f, d in _cache.items() if d["found_at"] < cutoff]:
            del _cache[fid]

    # ------------------------------------------------------------------
    # استخراج اطلاعات پایه از لیست بازی‌ها (بدون درخواست اضافه)
    # ------------------------------------------------------------------

    @staticmethod
    def _extract(fx: dict) -> Optional[dict]:

        fixture = fx.get("fixture") or {}
        league = fx.get("league") or {}
        teams = fx.get("teams") or {}
        score = fx.get("goals") or {}

        fixture_id = fixture.get("id")
        home = (teams.get("home") or {}).get("name")
        away = (teams.get("away") or {}).get("name")
        home_goals = score.get("home")
        away_goals = score.get("away")

        if not fixture_id or not home or not away:
            return None
        if home_goals is None or away_goals is None:
            return None

        status = (fixture.get("status") or {}).get("short", "FT")
        title = f"{home} {home_goals}-{away_goals} {away}"
        result = f"{home} {home_goals} - {away_goals} {away}"

        if status == "PEN":
            pen = (fx.get("score") or {}).get("penalty") or {}
            if pen.get("home") is not None and pen.get("away") is not None:
                title += f" ({pen['home']}-{pen['away']} on penalties)"
                result += f" (پنالتی: {pen['home']} - {pen['away']})"
        elif status == "AET":
            result += " (پس از وقت اضافه)"

        match_date = match_time = None
        raw_date = fixture.get("date")
        if raw_date:
            try:
                dt = datetime.fromisoformat(raw_date).astimezone(TEHRAN_TZ)
                match_date = dt.strftime("%Y-%m-%d")
                match_time = dt.strftime("%H:%M")
            except ValueError:
                pass

        round_text = league.get("round") or ""
        match = _ROUND_RE.search(round_text)
        stage = f"هفته {match.group(1)}" if match else (round_text or None)

        return {
            "fixture_id": fixture_id,
            "found_at": time.time(),
            "home": home,
            "away": away,
            "home_id": (teams.get("home") or {}).get("id"),
            "away_id": (teams.get("away") or {}).get("id"),
            "home_goals": home_goals,
            "away_goals": away_goals,
            "title": title,
            "result": result,
            "league": fx.get("_league_name", ""),
            "stage": stage,
            "stadium": (fixture.get("venue") or {}).get("name"),
            "referee": fixture.get("referee"),
            "match_date": match_date,
            "match_time": match_time,
            "goals": [],
            "assists": [],
            "yellow_cards": [],
            "red_cards": [],
            "lineup": None,
            "coach": None,
            "stats": [],
        }

    # ------------------------------------------------------------------
    # جزئیات هر بازی (هرکدام یک درخواست)
    # ------------------------------------------------------------------

    async def _enrich(self, data: dict) -> None:

        fid = data["fixture_id"]

        if budget_left() > RESERVED_REQUESTS:
            self._apply_events(data, await self.client.get_fixture_events(fid))

        if budget_left() > RESERVED_REQUESTS:
            self._apply_lineups(data, await self.client.get_fixture_lineups(fid))

        if budget_left() > RESERVED_REQUESTS:
            self._apply_stats(data, await self.client.get_fixture_statistics(fid))

    @staticmethod
    def _apply_events(data: dict, events: List[dict]) -> None:

        for event in events:

            etype = event.get("type")
            detail = event.get("detail") or ""
            low = detail.lower()
            player = (event.get("player") or {}).get("name") or "?"
            team = (event.get("team") or {}).get("name", "")
            minute = _minute_text(event)

            if etype == "Goal":

                if detail == "Missed Penalty":
                    continue

                tag = ""
                if detail == "Penalty":
                    tag = " (pen.)"
                elif detail == "Own Goal":
                    tag = " (o.g.)"

                data["goals"].append(f"{player} ({minute}'){tag} - {team}")

                assist = (event.get("assist") or {}).get("name")
                if assist and detail != "Own Goal":
                    data["assists"].append(f"{assist} ({minute}') - {team}")

            elif etype == "Card":

                line = f"{player} ({minute}') - {team}"

                if "second yellow" in low:
                    data["red_cards"].append(line + " (دو کارت زرد)")
                elif "red" in low:
                    data["red_cards"].append(line)
                elif "yellow" in low:
                    data["yellow_cards"].append(line)

    @staticmethod
    def _side(data: dict, team_id) -> Optional[str]:
        if team_id is not None and team_id == data["home_id"]:
            return "home"
        if team_id is not None and team_id == data["away_id"]:
            return "away"
        return None

    @staticmethod
    def _player_line(entry: dict) -> Optional[str]:
        player = (entry or {}).get("player") or {}
        name = player.get("name")
        if not name:
            return None
        number = player.get("number")
        return f"{number} {name}" if number is not None else name

    @classmethod
    def _apply_lineups(cls, data: dict, response: List[dict]) -> None:

        lineup: Dict[str, dict] = {}
        coaches: Dict[str, str] = {}

        for item in response:

            team = item.get("team") or {}
            side = cls._side(data, team.get("id"))

            if not side:
                continue

            starting = [
                line for line in (
                    cls._player_line(p) for p in item.get("startXI") or []
                ) if line
            ]

            substitutes: List[str] = []
            if INCLUDE_SUBSTITUTES:
                substitutes = [
                    line for line in (
                        cls._player_line(p) for p in item.get("substitutes") or []
                    ) if line
                ]

            name = team.get("name") or data[side]
            formation = item.get("formation")
            if formation:
                name = f"{name} ({formation})"

            lineup[side] = {
                "name": name,
                "starting": starting,
                "substitutes": substitutes,
            }

            coach = (item.get("coach") or {}).get("name")
            if coach:
                coaches[side] = coach

        if lineup:
            data["lineup"] = lineup

        parts = [
            f"{coaches[side]} ({data[side]})"
            for side in ("home", "away")
            if side in coaches
        ]
        if parts:
            data["coach"] = " / ".join(parts)

    @classmethod
    def _apply_stats(cls, data: dict, response: List[dict]) -> None:

        by_side: Dict[str, dict] = {}

        for item in response:

            side = cls._side(data, (item.get("team") or {}).get("id"))

            if side:
                by_side[side] = {
                    s.get("type"): s.get("value")
                    for s in item.get("statistics") or []
                }

        home = by_side.get("home")
        away = by_side.get("away")

        if not home or not away:
            return

        lines = []

        for key, label in STAT_LABELS:

            home_value = home.get(key)
            away_value = away.get(key)

            if home_value is None and away_value is None:
                continue

            lines.append(
                f"{label}: "
                f"{home_value if home_value is not None else 0}"
                f" - "
                f"{away_value if away_value is not None else 0}"
            )

        data["stats"] = lines

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
            source_id="api_football",
            source="API-Football",
            title=data["title"],
            summary=summary,
            language="en",
        )

        # fetcher از رشته‌ی ورزشی مطمئن است؛ SportDetector نباید آن را عوض کند
        news.sport = "football"
        news.sport_name = "فوتبال"
        news.sport_emoji = "⚽"
        news.sport_hashtag = "#فوتبال"

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
