"""
KhabarF24 Entity Manager
"""

from app.models.raw_news import RawNews

from .extractor import BaseEntityExtractor
from .football import FootballEntityExtractor


class EntityManager:

    def __init__(self):

        self.extractors: list[
            BaseEntityExtractor
        ] = [

            FootballEntityExtractor(),

        ]

    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        for extractor in self.extractors:

            news = extractor.extract(
                news
            )

        return news
