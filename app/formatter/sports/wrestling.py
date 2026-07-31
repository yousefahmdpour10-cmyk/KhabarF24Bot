"""
Wrestling Formatter
"""

from app.models.raw_news import RawNews


class WrestlingFormatter:

    async def format(
        self,
        news: RawNews,
    ) -> str:

        return (
            "🤼 Wrestling Formatter\n"
            f"{news.title}"
        )
