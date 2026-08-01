"""
Football Entity Extractor
"""

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor


class FootballEntityExtractor(BaseEntityExtractor):

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        # مرحله اول
        # فعلاً فقط خبر را برمی‌گردانیم

        return news
