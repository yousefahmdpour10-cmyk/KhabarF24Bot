"""
Base Entity Extractor
"""

from abc import ABC, abstractmethod

from app.models.raw_news import RawNews


class BaseEntityExtractor(ABC):

    @abstractmethod
    def extract(
        self,
        news: RawNews,
    ) -> RawNews:

        pass
