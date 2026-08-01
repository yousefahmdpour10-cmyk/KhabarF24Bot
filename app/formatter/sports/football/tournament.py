"""
Football Tournament Builder
"""

from app.models.raw_news import RawNews


class TournamentBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        tournament = getattr(news, "tournament", None)

        if tournament:
            lines.append(f"🏆 {tournament}")

        return lines
