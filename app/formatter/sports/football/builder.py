"""
Football Builder
"""

from app.models.raw_news import RawNews

from .result import ResultBuilder
from .goals import GoalsBuilder
from .assists import AssistsBuilder
from .cards import CardsBuilder
from .lineup import LineupBuilder
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

        self.result = ResultBuilder()
        self.goals = GoalsBuilder()
        self.assists = AssistsBuilder()
        self.cards = CardsBuilder()
        self.lineup = LineupBuilder()
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
