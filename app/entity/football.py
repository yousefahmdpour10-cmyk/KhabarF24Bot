"""
Football Entity Extractor

تشخیص و جمع‌آوری موجودیت‌های مرتبط با فوتبال.
"""

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor
from .teams import TeamEntityExtractor
from .people import PeopleEntityExtractor
from .leagues import LeagueEntityExtractor
from .tournaments import TournamentEntityExtractor
from .stadiums import StadiumEntityExtractor
from .referees import RefereeEntityExtractor


class FootballEntityExtractor(BaseEntityExtractor):

    FOOTBALL_KEYWORDS = [

        # English
        "football",
        "soccer",
        "premier league",
        "champions league",
        "europa league",
        "world cup",
        "la liga",
        "serie a",
        "bundesliga",
        "ligue 1",

        # Persian
        "فوتبال",
        "لیگ برتر",
        "لیگ قهرمانان",
        "لیگ اروپا",
        "جام جهانی",
        "لالیگا",
        "سری آ",
        "بوندسلیگا",
        "لیگ یک فرانسه",
    ]

    def __init__(self):

        self.team_extractor = TeamEntityExtractor()

        self.people_extractor = PeopleEntityExtractor()

        self.league_extractor = LeagueEntityExtractor()

        self.tournament_extractor = (
            TournamentEntityExtractor()
        )

        self.stadium_extractor = (
            StadiumEntityExtractor()
        )

        self.referee_extractor = (
            RefereeEntityExtractor()
        )

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            return news

        # ----------------------------------------
        # تشخیص اینکه خبر فوتبالی است یا نه
        # ----------------------------------------

        if not self.is_football(text):

            return news

        # ----------------------------------------
        # ثبت دسته
        # ----------------------------------------

        news.category = "football"

        # ----------------------------------------
        # استخراج تیم‌ها
        # ----------------------------------------

        news = self.team_extractor.extract(
            news
        )

        # ----------------------------------------
        # استخراج افراد
        # ----------------------------------------

        news = self.people_extractor.extract(
            news
        )

        # ----------------------------------------
        # استخراج لیگ
        # ----------------------------------------

        news = self.league_extractor.extract(
            news
        )

        # ----------------------------------------
        # استخراج تورنمنت
        # ----------------------------------------

        news = self.tournament_extractor.extract(
            news
        )

        # ----------------------------------------
        # استخراج ورزشگاه
        # ----------------------------------------

        news = self.stadium_extractor.extract(
            news
        )

        # ----------------------------------------
        # استخراج داور
        # ----------------------------------------

        news = self.referee_extractor.extract(
            news
        )

        return news

    def is_football(
        self,
        text: str,
    ) -> bool:

        normalized = text.lower()

        for keyword in self.FOOTBALL_KEYWORDS:

            if keyword.lower() in normalized:

                return True

        # اگر دو تیم شناخته‌شده در متن باشند،
        # احتمال فوتبالی بودن خبر بسیار زیاد است.

        teams = self.team_extractor.find_teams(
            text
        )

        if len(teams) >= 2:

            return True

        return False

    @staticmethod
    def _get_text(
        news: RawNews,
    ) -> str:

        parts = []

        if news.title:
            parts.append(
                news.title
            )

        if news.summary:
            parts.append(
                news.summary
            )

        if news.content:
            parts.append(
                news.content
            )

        return " ".join(parts)
