"""
Football League Entity Extractor
"""

from app.models.raw_news import RawNews

from .dictionary import (
    FOOTBALL_LEAGUES,
    find_league,
    normalize_text,
)


class LeagueEntityExtractor:

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            return news

        leagues = self.find_leagues(text)

        if leagues:

            setattr(
                news,
                "leagues",
                leagues,
            )

        return news

    def find_leagues(
        self,
        text: str,
    ) -> list[str]:

        normalized_text = normalize_text(text)
        normalized_lower = normalized_text.lower()

        found = []

        for canonical, aliases in FOOTBALL_LEAGUES.items():

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

                if normalized_name.lower() in normalized_lower:

                    if canonical not in found:

                        found.append(
                            canonical
                        )

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

        title = getattr(
            news,
            "title",
            None,
        )

        summary = getattr(
            news,
            "summary",
            None,
        )

        content = getattr(
            news,
            "content",
            None,
        )

        if title:
            parts.append(
                str(title)
            )

        if summary:
            parts.append(
                str(summary)
            )

        if content:
            parts.append(
                str(content)
            )

        return " ".join(parts)
