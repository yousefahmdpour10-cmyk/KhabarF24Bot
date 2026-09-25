"""
Football Stadium Builder
"""

from app.models.raw_news import RawNews


class StadiumBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        stadium = getattr(news, "stadium", None)

        if stadium:
            lines.append(f"🏟️ {stadium}")

        return lines
