"""
News Summarizer
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger

from .rules import (
    MAX_SUMMARY_LENGTH,
    REMOVE_PHRASES,
)


class Summarizer:

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        summary = news.summary or news.title

        for phrase in REMOVE_PHRASES:

            summary = summary.replace(
                phrase,
                "",
            )

        summary = " ".join(
            summary.split()
        )

        if len(summary) > MAX_SUMMARY_LENGTH:

            summary = (
                summary[
                    :MAX_SUMMARY_LENGTH
                ].rstrip()
                + "..."
            )

        news.summary = summary

        logger.info(
            "Summary generated."
        )

        return news
