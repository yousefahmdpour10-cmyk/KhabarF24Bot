"""
Football Formatter
"""

from app.models.raw_news import RawNews

from app.formatter.footer import build_footer
from app.formatter.hashtags import HashtagBuilder
from app.formatter.source_flags import get_flag

from app.formatter.icons import (
    TITLE,
    SOURCE,
)


class FootballFormatter:

    def __init__(self):

        self.hashtags = HashtagBuilder()

    async def format(
        self,
        news: RawNews,
    ) -> str:

        text = ""

        hashtags = self.hashtags.build(news)

        flag = get_flag(news.source)

        text += "━━━━━━━━━━━━━━━━\n"
        text += "🔴 KhabarF24 | ⚽ فوتبال\n"
        text += "━━━━━━━━━━━━━━━━\n\n"

        text += f"{TITLE} {news.title}\n\n"

            def build_details(
        self,
        news: RawNews,
    ) -> str:

        lines = []

        # نتیجه مسابقه
        if getattr(news, "result", None):
            lines.append(f"🏆 {news.result}")

        # گلزنان
        goals = getattr(news, "goals", [])

        for goal in goals:
            lines.append(f"🥅 {goal}")

        # پاس گل
        assists = getattr(news, "assists", [])

        for assist in assists:
            lines.append(f"🎯 {assist}")

        # کارت زرد
        yellow_cards = getattr(news, "yellow_cards", [])

        for card in yellow_cards:
            lines.append(f"🟨 {card}")

        # کارت قرمز
        red_cards = getattr(news, "red_cards", [])

        for card in red_cards:
            lines.append(f"🟥 {card}")

        return "\n".join(lines)
