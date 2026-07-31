"""
Basketball Formatter
"""

from app.models.raw_news import RawNews


class BasketballFormatter:

    async def format(
        self,
        news: RawNews,
    ) -> str:

        return (
            "🏀 Basketball Formatter\n"
            f"{news.title}"
        )
