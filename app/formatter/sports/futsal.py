"""
Futsal Formatter
"""

from app.models.raw_news import RawNews


class FutsalFormatter:

    async def format(
        self,
        news: RawNews,
    ) -> str:

        return (
            "🥅 Futsal Formatter\n"
            f"{news.title}"
        )
