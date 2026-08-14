"""
Football League Entity Extractor
"""

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor
from .dictionary import (
    FOOTBALL_LEAGUES,
    find_league,
    normalize_text,
)


class LeagueEntityExtractor(BaseEntityExtractor):

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            news.leagues = []
            return news

        news.leagues = self.find_leagues(text)

        return news

    def find_leagues(
        self,
        text: str,
    ) -> list[str]:

        normalized_text = normalize_text(text).lower()

        found = []

        for canonical, aliases in FOOTBALL_LEAGUES.items():

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

    def find_single_league(
        self,
        text: str,
    ) -> str | None:

        return find_league(text)

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
