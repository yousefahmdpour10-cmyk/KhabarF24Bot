"""
Football Formatter
"""

from app.models.raw_news import RawNews

from app.formatter.footer import build_footer
from app.formatter.hashtags import HashtagBuilder
from app.formatter.source_flags import get_flag
from app.formatter.sports.football.builder import FootballBuilder
from app.formatter.icons import (
    TITLE,
    SOURCE,
)


class FootballFormatter:

    def __init__(self):

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

            def build_details(
    self,
    news: RawNews,
) -> str:

    return self.builder.build(news)
