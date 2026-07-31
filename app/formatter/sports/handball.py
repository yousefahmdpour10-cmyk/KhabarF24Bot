"""
Handball Formatter
"""

from app.models.raw_news import RawNews


class HandballFormatter:

    async def format(
        self,
        news: RawNews,
    ) -> str:

        return (
            "🤾 Handball Formatter\n"
            f"{news.title}"
        )
