"""
Tennis Formatter
"""

from app.models.raw_news import RawNews


class TennisFormatter:

    async def format(
        self,
        news: RawNews,
    ) -> str:

        return (
            "🎾 Tennis Formatter\n"
            f"{news.title}"
        )
