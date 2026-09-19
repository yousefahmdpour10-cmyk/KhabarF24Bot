"""
Sports API Fetcher

بازی‌های تمام‌شده‌ی امروز از لیگ‌های دنبال‌شده را می‌گیرد و برای هرکدام
یک RawNews با نتیجه و گلزنان (برای FootballBuilder) می‌سازد.
"""

from datetime import datetime, timezone
from typing import List

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.services.sports_api_client import SportsApiClient
from app.utils.logger import logger


class SportsApiFetcher(BaseFetcher):

    def __init__(self, source):
        super().__init__(source)
        self.client = SportsApiClient()

    async def fetch(self) -> List[RawNews]:

        news_list: List[RawNews] = []

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        fixtures = await self.client.get_finished_fixtures(today)

        for fixture in fixtures:

            try:
                news = await self._build_news(fixture)
                if news:
                    news_list.append(news)

            except Exception as e:
                logger.error(f"SportsApiFetcher: خطا در ساخت خبر -> {e}")

        return news_list

    async def _build_news(self, fixture: dict) -> RawNews:

        teams = fixture.get("teams", {})
        goals_score = fixture.get("goals", {})
        fixture_info = fixture.get("fixture", {})
        league_name = fixture.get("_league_name", "")

        home_name = teams.get("home", {}).get("name", "")
        away_name = teams.get("away", {}).get("name", "")
        home_score = goals_score.get("home")
        away_score = goals_score.get("away")

        if not home_name or not away_name or home_score is None:
            return None

        title = f"{home_name} {home_score}-{away_score} {away_name}"

        news = RawNews(
            source_id="api_football",
            source="API-Football",
            title=title,
            summary=f"نتیجه‌ی نهایی دیدار {home_name} و {away_name} در {league_name}.",
            language="en",
        )

        # این‌ها مستقیم توسط SportDetector/CategoryDetector هم تشخیص داده
        # می‌شوند، ولی چون خودمان قطعی می‌دانیم فوتبال است، مستقیم ست
        # می‌کنیم تا وابسته به حدسِ کلیدواژه نباشد.
        news.sport = "football"
        news.sport_name = "فوتبال"
        news.sport_emoji = "⚽"
        news.sport_hashtag = "#فوتبال"

        news.result = f"{home_score} - {away_score}"
        news.tournament = league_name
        news.league = league_name

        venue = fixture_info.get("venue", {}) or {}
        news.stadium = venue.get("name")

        referee = fixture_info.get("referee")
        news.referee = referee

        fixture_date = fixture_info.get("date")  # ISO 8601
        if fixture_date:
            try:
                dt = datetime.fromisoformat(fixture_date.replace("Z", "+00:00"))
                news.match_date = dt.strftime("%Y-%m-%d")
                news.match_time = dt.strftime("%H:%M")
            except ValueError:
                pass

        fixture_id = fixture_info.get("id")
        if fixture_id:
            news.goals = await self._build_goals(fixture_id, home_name, away_name)

        return news

    async def _build_goals(
        self,
        fixture_id: int,
        home_name: str,
        away_name: str,
    ) -> List[str]:

        events = await self.client.get_fixture_events(fixture_id)

        goals = []

        for event in events:

            if event.get("type") != "Goal":
                continue

            player = event.get("player", {}).get("name", "؟")
            minute = event.get("time", {}).get("elapsed", "؟")
            team_name = event.get("team", {}).get("name", "")

            goals.append(f"{player} ({minute}') - {team_name}")

        return goals
