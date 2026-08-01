"""
Entity Manager
"""

from app.models.raw_news import RawNews

from .football import FootballEntityExtractor


class EntityManager:

    def __init__(self):

        self.football = FootballEntityExtractor()

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        sport = getattr(
            news,
            "sport",
            "",
        ).lower()

        if sport == "football":

            news = self.football.extract(news)

        return news
