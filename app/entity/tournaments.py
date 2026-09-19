"""
Football Tournament Entity Extractor
"""

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor
from .dictionary import (
    FOOTBALL_TOURNAMENTS,
    find_tournament,
    normalize_text,
)


class TournamentEntityExtractor(BaseEntityExtractor):

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            news.tournaments = []
            return news

        news.tournaments = self.find_tournaments(text)

        return news

    def find_tournaments(
        self,
        text: str,
    ) -> list[str]:

        normalized_text = normalize_text(text).lower()

        found = []

        for canonical, aliases in FOOTBALL_TOURNAMENTS.items():

            for name in [canonical, *aliases]:

                normalized_name = normalize_text(name).lower()

                if (
                    normalized_name
                    and normalized_name in normalized_text
                ):
                    if canonical not in found:
                        found.append(canonical)

                    break

        return found

    def find_single_tournament(
        self,
        text: str,
    ) -> str | None:

        return find_tournament(text)

    @staticmethod
    def _get_text(
        news: RawNews,
    ) -> str:

        parts = []

        if news.title:
            parts.append(news.title)

        if news.summary:
            parts.append(news.summary)

        if news.content:
            parts.append(news.content)

        return " ".join(parts)
