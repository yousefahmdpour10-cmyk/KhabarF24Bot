"""
Football Stats Builder
"""

from app.models.raw_news import RawNews


class StatsBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        stats = getattr(news, "stats", [])

        for stat in stats:
            lines.append(f"📊 {stat}")

        return lines
