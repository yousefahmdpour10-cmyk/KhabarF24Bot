"""
Football Stadium Entity Extractor
"""

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor
from .dictionary import normalize_text


class StadiumEntityExtractor(BaseEntityExtractor):

    STADIUMS = {

        "Old Trafford": [
            "Old Trafford",
            "اولدترافورد",
            "اولد ترافورد",
        ],

        "Etihad Stadium": [
            "Etihad Stadium",
            "Etihad",
            "ورزشگاه اتحاد",
            "اتحاد",
        ],

        "Anfield": [
            "Anfield",
            "آنفیلد",
        ],

        "Santiago Bernabéu": [
            "Santiago Bernabéu",
            "Santiago Bernabeu",
            "Bernabeu",
            "سانتیاگو برنابئو",
            "برنابئو",
        ],

        "Camp Nou": [
            "Camp Nou",
            "Nou Camp",
            "نوکمپ",
            "کمپ نو",
        ],

        "Allianz Arena": [
            "Allianz Arena",
            "آلیانتس آرنا",
        ],

        "San Siro": [
            "San Siro",
            "Giuseppe Meazza",
            "سن سیرو",
            "جوزپه مه‌آتزا",
        ],
    }

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            news.stadiums = []
            return news

        news.stadiums = self.find_stadiums(text)

        return news

    def find_stadiums(
        self,
        text: str,
    ) -> list[str]:

        normalized_text = normalize_text(text).lower()

        found = []

        for canonical, aliases in self.STADIUMS.items():

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

    def find_single_stadium(
        self,
        text: str,
    ) -> str | None:

        stadiums = self.find_stadiums(text)

        return stadiums[0] if stadiums else None

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
