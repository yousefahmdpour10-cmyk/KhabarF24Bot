"""
Football Goals Builder
"""

from app.models.raw_news import RawNews


class GoalsBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        goals = getattr(news, "goals", [])

        for goal in goals:
            lines.append(f"🥅 {goal}")

        return lines
