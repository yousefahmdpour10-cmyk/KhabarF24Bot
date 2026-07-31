"""
Volleyball Formatter
"""

from app.models.raw_news import RawNews


class VolleyballFormatter:

    async def format(
        self,
        news: RawNews,
    ) -> str:

        return (
            "🏐 Volleyball Formatter\n"
            f"{news.title}"
        )
