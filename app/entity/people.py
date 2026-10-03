"""
Football People Entity Extractor
"""

import re

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor


class PeopleEntityExtractor(BaseEntityExtractor):

    ROLE_ALIASES = {

        "coach": [
            "coach",
            "manager",
            "head coach",
            "مربی",
            "سرمربی",
        ],

        "captain": [
            "captain",
            "کاپیتان",
        ],

        "player": [
            "player",
            "بازیکن",
        ],

        "interview": [
            "said",
            "says",
            "told",
            "interview",
            "مصاحبه",
            "گفت",
            "اظهار داشت",
        ],
    }

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            return news

        people = self.find_people(text)

        news.people = people

        return news

    def find_people(
        self,
        text: str,
    ) -> list[dict]:

        people = []

        english_pattern = re.compile(
            r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b"
        )

        persian_pattern = re.compile(
            r"\b[آ-ی]{2,}(?:\s+[آ-ی]{2,}){1,3}\b"
        )

        matches = []

        matches.extend(
            english_pattern.findall(text)
        )

        matches.extend(
            persian_pattern.findall(text)
        )

        for name in matches:

            name = name.strip()

            if len(name) < 3:
                continue

            if self._is_common_phrase(name):
                continue

            if any(
                person["name"] == name
                for person in people
            ):
                continue

            people.append(
                {
                    "name": name,
                    "role": self.detect_role(
                        name,
                        text,
                    ),
                }
            )

        return people

    def detect_role(
        self,
        name: str,
        text: str,
    ) -> str:

        for keyword in self.ROLE_ALIASES["coach"]:

            nearby = self._nearby_text(
                name,
                text,
            )

            if keyword.lower() in nearby.lower():

                return "coach"

        for keyword in self.ROLE_ALIASES["captain"]:

            nearby = self._nearby_text(
                name,
                text,
            )

            if keyword.lower() in nearby.lower():

                return "captain"

        for keyword in self.ROLE_ALIASES["interview"]:

            nearby = self._nearby_text(
                name,
                text,
            )

            if keyword.lower() in nearby.lower():

                return "interview"

        return "player"

    @staticmethod
    def _nearby_text(
        name: str,
        text: str,
        window: int = 120,
    ) -> str:

        index = text.lower().find(
            name.lower()
        )

        if index == -1:
            return ""

        start = max(
            0,
            index - window,
        )

        end = min(
            len(text),
            index + len(name) + window,
        )

        return text[start:end]

    @staticmethod
    def _is_common_phrase(
        text: str,
    ) -> bool:

        common_phrases = {

            "Manchester United",
            "Manchester City",
            "Real Madrid",
            "Paris Saint Germain",
            "Premier League",
            "Champions League",
            "World Cup",

            "منچستر یونایتد",
            "منچستر سیتی",
            "رئال مادرید",
            "پاری سن ژرمن",
            "پریمیر لیگ",
            "لیگ قهرمانان",
            "جام جهانی",
        }

        return text in common_phrases

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
