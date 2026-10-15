"""
Football Referee Builder
"""

from app.models.raw_news import RawNews


class RefereeBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        referee = getattr(news, "referee", None)

        if referee:
            lines.append(f"👨‍⚖️ {referee}")

        return lines
