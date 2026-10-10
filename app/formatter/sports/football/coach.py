"""
Football Coach Builder
"""

from app.models.raw_news import RawNews


class CoachBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        coach = getattr(news, "coach", None)

        if coach:
            lines.append(f"👔 {coach}")

        return lines
