"""
Football Builder
"""

from app.models.raw_news import RawNews

from .match_info import MatchInfoBuilder
from .result import ResultBuilder
from .lineup import LineupBuilder
from .goals import GoalsBuilder
from .assists import AssistsBuilder
from .cards import CardsBuilder
from .coach import CoachBuilder
from .captain import CaptainBuilder
from .interview import InterviewBuilder
from .referee import RefereeBuilder
from .stadium import StadiumBuilder
from .stats import StatsBuilder
from .transfer import TransferBuilder
from .tournament import TournamentBuilder


class FootballBuilder:

    def __init__(self):

        self.match_info = MatchInfoBuilder()
        self.result = ResultBuilder()
        self.lineup = LineupBuilder()
        self.goals = GoalsBuilder()
        self.assists = AssistsBuilder()
        self.cards = CardsBuilder()
        self.coach = CoachBuilder()
        self.captain = CaptainBuilder()
        self.interview = InterviewBuilder()
        self.referee = RefereeBuilder()
        self.stadium = StadiumBuilder()
        self.stats = StatsBuilder()
        self.transfer = TransferBuilder()
        self.tournament = TournamentBuilder()

    def build(
        self,
        news: RawNews,
    ) -> str:

        lines = []

        builders = [

            self.match_info,

            self.result,

            self.lineup,

            self.goals,

            self.assists,

            self.cards,

            self.coach,

            self.captain,

            self.interview,

            self.referee,

            self.stadium,

            self.stats,

            self.transfer,

            self.tournament,

        ]

        for builder in builders:

            data = builder.build(news)

            if data:

                lines.extend(data)

        return "\n".join(lines)
