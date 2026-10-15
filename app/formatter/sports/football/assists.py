"""
Football Assists Builder
"""

from app.models.raw_news import RawNews


class AssistsBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        assists = getattr(news, "assists", [])

        for assist in assists:
            lines.append(f"🎯 {assist}")

        return lines
