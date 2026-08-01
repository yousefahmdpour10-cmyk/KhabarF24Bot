"""
KhabarF24 Entity Manager
"""

from app.models.raw_news import RawNews

from .teams import TeamEntityExtractor
from .people import PeopleEntityExtractor
from .leagues import LeagueEntityExtractor
from .tournaments import TournamentEntityExtractor
from .stadiums import StadiumEntityExtractor
from .referees import RefereeEntityExtractor


class EntityManager:

    def __init__(self):

        self.teams = TeamEntityExtractor()
        self.people = PeopleEntityExtractor()
        self.leagues = LeagueEntityExtractor()
        self.tournaments = TournamentEntityExtractor()
        self.stadiums = StadiumEntityExtractor()
        self.referees = RefereeEntityExtractor()

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        news = self.teams.extract(news)

        news = self.people.extract(news)

        news = self.leagues.extract(news)

        news = self.tournaments.extract(news)

        news = self.stadiums.extract(news)

        news = self.referees.extract(news)

        return news
