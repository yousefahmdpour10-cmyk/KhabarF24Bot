"""
Football Teams Entity Extractor
"""

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor
from .dictionary import (
    FOOTBALL_TEAMS,
    find_team,
    normalize_text,
)


class TeamEntityExtractor(BaseEntityExtractor):

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            return news

        teams = self.find_teams(text)

        news.teams = teams

        return news

    def find_teams(
        self,
        text: str,
    ) -> list[str]:

        normalized_text = normalize_text(text)
        normalized_lower = normalized_text.lower()

        found = []

        for canonical, aliases in FOOTBALL_TEAMS.items():

            names = [
                canonical,
                *aliases,
            ]

            for name in names:

                normalized_name = normalize_text(
                    name
                )

                if not normalized_name:
                    continue

                if (
                    normalized_name.lower()
                    in normalized_lower
                ):

                    if canonical not in found:

                        found.append(
                            canonical
                        )

                    break

        return found

    def find_single_team(
        self,
        text: str,
    ) -> str | None:

        return find_team(text)

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
