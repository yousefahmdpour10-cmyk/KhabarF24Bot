"""
Football Formatter
"""

from app.models.raw_news import RawNews
from app.formatter.header import build_header
from app.formatter.footer import build_footer
from app.formatter.hashtags import HashtagBuilder
from app.formatter.source_flags import get_flag
from .builder import FootballBuilder
from app.formatter.icons import (
    TITLE,
    SOURCE,
)


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

        text += build_header("⚽ فوتبال", getattr(news, "is_breaking", False))
        text += "\n\n"
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
