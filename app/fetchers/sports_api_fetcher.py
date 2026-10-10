"""
Sports API Fetcher

نتیجه‌ی بازی‌های تمام‌شده‌ی لیگ‌های دنبال‌شده را (با گلزنان) می‌گیرد.

چون پلن رایگان فقط ۱۰۰ درخواست در روز دارد:
- فقط هر ~۴۰ دقیقه و فقط در ساعت‌های فعال بازی‌ها به API درخواست می‌دهیم؛
- نتیجه‌ی بازی‌های پیداشده در حافظه نگه داشته می‌شود و هر چرخه دوباره
  به pipeline داده می‌شود (بدون درخواست جدید). تکراری‌ها را
  DuplicateChecker حذف می‌کند و اگر ترجمه‌ی AI شکست بخورد، همان بازی
  چرخه‌ی بعد دوباره امتحان می‌شود.
"""

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

_ROUND_RE = re.compile(r"(?:Regular Season|League Stage) - (\d+)", re.IGNORECASE)

# حافظه‌ی مشترک بین چرخه‌ها (هر چرخه یک نمونه‌ی جدید fetcher ساخته می‌شود)
_cache: Dict[int, dict] = {}
_last_poll_at: Optional[float] = None


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

                if budget_left() > RESERVED_REQUESTS:
                    data["goals"] = await self._build_goals(data["fixture_id"])

                _cache[data["fixture_id"]] = data

        logger.info(f"SportsApiFetcher: {len(_cache)} بازی در حافظه")

    @staticmethod
    def _prune() -> None:
        cutoff = time.time() - CACHE_TTL_SECONDS
        for fid in [f for f, d in _cache.items() if d["found_at"] < cutoff]:
            del _cache[fid]

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
        result = f"{home_goals} - {away_goals}"

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
        }

    async def _build_goals(self, fixture_id: int) -> List[str]:

        events = await self.client.get_fixture_events(fixture_id)

        lines: List[str] = []

        for event in events:

            if event.get("type") != "Goal":
                continue

            detail = event.get("detail", "")

            if detail == "Missed Penalty":
                continue

            player = (event.get("player") or {}).get("name") or "?"
            team = (event.get("team") or {}).get("name", "")
            time_info = event.get("time") or {}
            minute = time_info.get("elapsed")
            extra = time_info.get("extra")
            minute_text = f"{minute}+{extra}" if extra else f"{minute}"

            tag = ""
            if detail == "Penalty":
                tag = " (pen.)"
            elif detail == "Own Goal":
                tag = " (o.g.)"

            lines.append(f"{player} ({minute_text}'){tag} - {team}")

        return lines

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

        news.result = data["result"]
        news.goals = list(data["goals"])
        news.tournament = data["league"]
        news.league = data["league"]
        news.stage = data["stage"]
        news.stadium = data["stadium"]
        news.referee = data["referee"]
        news.match_date = data["match_date"]
        news.match_time = data["match_time"]

        news.source_category_hint = getattr(self.source, "categories", None)

        return news
