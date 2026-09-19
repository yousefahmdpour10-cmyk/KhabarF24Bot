"""
Football Referee Entity Extractor
"""

import re

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor


class RefereeEntityExtractor(BaseEntityExtractor):

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            news.referees = []
            return news

        news.referees = self.find_referees(text)

        return news

    def find_referees(
        self,
        text: str,
    ) -> list[str]:

        found = []

        patterns = [

            # English
            r"\breferee\s*[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",

            r"\bmatch referee\s*[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",

            # Persian
            r"داور\s*[:\-]\s*([آ-ی]{2,}(?:\s+[آ-ی]{2,}){1,3})",

            r"داور مسابقه\s*[:\-]\s*([آ-ی]{2,}(?:\s+[آ-ی]{2,}){1,3})",

            r"داور دیدار\s*[:\-]\s*([آ-ی]{2,}(?:\s+[آ-ی]{2,}){1,3})",
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            for match in matches:

                name = match.strip()

                if name and name not in found:
                    found.append(name)

        return found

    def find_single_referee(
        self,
        text: str,
    ) -> str | None:

        referees = self.find_referees(text)

        return referees[0] if referees else None

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
