"""
Football Transfer Builder
"""

from app.models.raw_news import RawNews


class TransferBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        transfer = getattr(news, "transfer", None)

        if transfer:
            lines.append(f"🔄 {transfer}")

        return lines
