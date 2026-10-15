"""
Football Cards Builder
"""

from app.models.raw_news import RawNews


class CardsBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        yellow = getattr(news, "yellow_cards", [])

        for card in yellow:
            lines.append(f"🟨 {card}")

        red = getattr(news, "red_cards", [])

        for card in red:
            lines.append(f"🟥 {card}")

        return lines
