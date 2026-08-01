"""
KhabarF24 Entity Manager
"""

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor
from .teams import TeamEntityExtractor
from .people import PeopleEntityExtractor
from .leagues import LeagueEntityExtractor
from .tournaments import TournamentEntityExtractor
from .stadiums import StadiumEntityExtractor
from .referees import RefereeEntityExtractor


class EntityManager:

    def __init__(self):

        self.extractors: list[
            BaseEntityExtractor
        ] = [

            TeamEntityExtractor(),

            PeopleEntityExtractor(),

            LeagueEntityExtractor(),

            TournamentEntityExtractor(),

            StadiumEntityExtractor(),

            RefereeEntityExtractor(),
        ]

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        for extractor in self.extractors:

            news = extractor.extract(
                news
            )

        return news
