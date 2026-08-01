"""
Football Referee Entity Extractor
"""

import re

from app.models.raw_news import RawNews


class RefereeEntityExtractor:

    REFEREE_KEYWORDS = [
        "referee",
        "match referee",
        "official",
        "داور",
        "داور مسابقه",
        "داور دیدار",
    ]

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            return news

        referees = self.find_referees(text)

        if referees:

            setattr(
                news,
                "referees",
                referees,
            )

        return news

    def find_referees(
        self,
        text: str,
    ) -> list[str]:

        found = []

        # --------------------------------------------------
        # English referee patterns
        # --------------------------------------------------

        english_patterns = [

            r"referee\s*[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",

            r"match referee\s*[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",

            r"referee\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",

        ]

        # --------------------------------------------------
        # Persian referee patterns
        # --------------------------------------------------

        persian_patterns = [

            r"داور\s*[:\-]\s*([آ-ی]{2,}(?:\s+[آ-ی]{2,}){1,3})",

            r"داور مسابقه\s*[:\-]\s*([آ-ی]{2,}(?:\s+[آ-ی]{2,}){1,3})",

            r"داور دیدار\s*[:\-]\s*([آ-ی]{2,}(?:\s+[آ-ی]{2,}){1,3})",

        ]

        patterns = (
            english_patterns
            + persian_patterns
        )

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            for match in matches:

                name = match.strip()

                if (
                    name
                    and name not in found
                ):

                    found.append(
                        name
                    )

        return found

    def find_single_referee(
        self,
        text: str,
    ) -> str | None:

        referees = self.find_referees(
            text
        )

        if referees:

            return referees[0]

        return None

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
