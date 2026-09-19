"""
Sport Template Manager
"""

from app.models.raw_news import RawNews

from app.formatter.templates.base import BaseTemplate

from app.formatter.sports.football import FootballFormatter
from app.formatter.sports.basketball import BasketballFormatter
from app.formatter.sports.volleyball import VolleyballFormatter
from app.formatter.sports.tennis import TennisFormatter
from app.formatter.sports.wrestling import WrestlingFormatter
from app.formatter.sports.futsal import FutsalFormatter
from app.formatter.sports.handball import HandballFormatter


class SportTemplate(BaseTemplate):

    def __init__(self):

        self.formatters = {

            "football": FootballFormatter(),

            "basketball": BasketballFormatter(),

            "volleyball": VolleyballFormatter(),

            "tennis": TennisFormatter(),

            "wrestling": WrestlingFormatter(),

            "futsal": FutsalFormatter(),

            "handball": HandballFormatter(),

        }

    async def format(
        self,
        news: RawNews,
    ) -> str:

        sport = getattr(
            news,
            "sport",
            "football",
        ).lower()

        formatter = self.formatters.get(
            sport,
            FootballFormatter(),
        )

        return await formatter.format(news)
