"""
Handball Formatter
"""

from app.models.raw_news import RawNews
from app.formatter.footer import build_footer
from app.formatter.hashtags import HashtagBuilder
from app.formatter.source_flags import get_flag
from app.formatter.icons import (
    TITLE,
    SUMMARY,
    SOURCE,
)

DEFAULT_EMOJI = "🤾"
DEFAULT_LABEL = "هندبال"


class HandballFormatter:

    def __init__(self):
        self.hashtags = HashtagBuilder()

    async def format(
        self,
        news: RawNews,
    ) -> str:

        flag = get_flag(news.source)
        hashtags = self.hashtags.build(news)

        emoji = getattr(news, "sport_emoji", None) or DEFAULT_EMOJI
        label = getattr(news, "sport_name", None) or DEFAULT_LABEL

        text = ""
        text += "━━━━━━━━━━━━━━━━\n"
        text += f"🔴 KhabarF24 | {emoji} {label}\n"
        text += "━━━━━━━━━━━━━━━━\n\n"
        text += f"{TITLE} {news.title}\n\n"

        if getattr(news, "summary", None):
            text += f"{SUMMARY} {news.summary}\n\n"

        text += f"{SOURCE} {flag} {news.source}\n"
        text += build_footer()

        if hashtags:
            text += "\n\n"
            text += hashtags

        return text
