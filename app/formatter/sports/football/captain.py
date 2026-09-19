"""
Football Captain Builder
"""

from app.models.raw_news import RawNews


class CaptainBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        captain = getattr(news, "captain", None)

        if captain:
            lines.append(f"©️ {captain}")

        return lines
