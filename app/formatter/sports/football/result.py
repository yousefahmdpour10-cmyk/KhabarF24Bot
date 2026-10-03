"""
Football Result Builder
"""

from app.models.raw_news import RawNews


class ResultBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        result = getattr(
            news,
            "result",
            None,
        )

        if result:

            lines.append(
                f"🏆 {result}"
            )

        return lines
