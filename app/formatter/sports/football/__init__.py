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

from .builder import FootballBuilder


class FootballFormatter:

    def __init__(self):
        self.hashtags = HashtagBuilder()
        self.builder = FootballBuilder()

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

        details = self.build_details(news)
        if details:
            text += details
            text += "\n\n"

        text += f"{SOURCE} {flag} {news.source}\n"
        text += build_footer()

        if hashtags:
            text += "\n\n"
            text += hashtags

        return text

    def build_details(
        self,
        news: RawNews,
    ) -> str:
        return self.builder.build(news)
