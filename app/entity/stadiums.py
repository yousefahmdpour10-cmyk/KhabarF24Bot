"""
Football Stadium Entity Extractor
"""

from app.models.raw_news import RawNews

from .dictionary import normalize_text


class StadiumEntityExtractor:

    STADIUMS = {

        "Old Trafford": [
            "Old Trafford",
            "اولدترافورد",
            "اولدترافورد",
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
            "نوکمپ",
            "کمپ نو",
        ],

        "Allianz Arena": [
            "Allianz Arena",
            "آلیانتس آرنا",
        ],

        "San Siro": [
            "San Siro",
            "سن سیرو",
        ],
    }

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        text = self._get_text(news)

        if not text:
            return news

        stadiums = self.find_stadiums(text)

        if stadiums:

            setattr(
                news,
                "stadiums",
                stadiums,
            )

        return news

    def find_stadiums(
        self,
        text: str,
    ) -> list[str]:

        normalized_text = normalize_text(
            text
        ).lower()

        found = []

        for canonical, aliases in self.STADIUMS.items():

            names = [
                canonical,
                *aliases,
            ]

            for name in names:

                normalized_name = normalize_text(
                    name
                ).lower()

                if not normalized_name:
                    continue

                if normalized_name in normalized_text:

                    if canonical not in found:

                        found.append(
                            canonical
                        )

                    break

        return found

    def find_single_stadium(
        self,
        text: str,
    ) -> str | None:

        stadiums = self.find_stadiums(text)

        if stadiums:

            return stadiums[0]

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
