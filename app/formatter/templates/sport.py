"""
Sport Template Manager
"""

from app.models.raw_news import RawNews

from app.formatter.templates.base import BaseTemplate

from app.formatter.sports.football import FootballFormatter
from app.formatter.sports.basketball import BasketballFormatter
from app.formatter.sports.volleyball import VolleyballFormatter
from app.formatter.sports.tennis import TennisFormatter
from app.formatter.sports.wrestling import WrestlingFormatter
from app.formatter.sports.futsal import FutsalFormatter
from app.formatter.sports.handball import HandballFormatter
from app.formatter.sports.generic import GenericSportFormatter


class SportTemplate(BaseTemplate):

    def __init__(self):

        self.formatters = {

            "football": FootballFormatter(),

            "basketball": BasketballFormatter(),

            "volleyball": VolleyballFormatter(),

            "tennis": TennisFormatter(),

            "wrestling": WrestlingFormatter(),

            "futsal": FutsalFormatter(),

            "handball": HandballFormatter(),

        }

        # پیش‌فرض دیگر فوتبال نیست -- هر رشته‌ای که فرمتر اختصاصی
        # ندارد (شنا، بوکس، فرمول یک، دوومیدانی و ...) از این فرمتر
        # عمومی استفاده می‌کند که خودش هدر را دقیقاً بر اساس رشته‌ی
        # واقعی تشخیص‌داده‌شده می‌سازد.
        self.default_formatter = GenericSportFormatter()

    async def format(
        self,
        news: RawNews,
    ) -> str:

        sport = (getattr(news, "sport", None) or "").lower()

        formatter = self.formatters.get(
            sport,
            self.default_formatter,
        )

        return await formatter.format(news)
