"""
Iran News Template
"""

from app.models.raw_news import RawNews
from app.formatter.templates.base import BaseTemplate
from app.formatter.icons import (
    TITLE,
    SUMMARY,
    SOURCE,
)
from app.formatter.footer import build_footer
from app.formatter.source_flags import get_flag
from app.formatter.hashtags import HashtagBuilder


class IranTemplate(BaseTemplate):

    def __init__(self):
        self.hashtags = HashtagBuilder()

    async def format(
        self,
        news: RawNews,
    ) -> str:

        flag = get_flag(news.source)
        hashtags = self.hashtags.build(news)

        text = ""
        text += "━━━━━━━━━━━━━━━━\n"
        text += "🔴 KhabarF24 | 🇮🇷 ایران\n"
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
