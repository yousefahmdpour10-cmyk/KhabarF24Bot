"""
Base Fetcher

تمام Fetcher های پروژه باید از این کلاس ارث‌بری کنند.
"""

from abc import ABC, abstractmethod
from typing import List

from app.models.raw_news import RawNews
from app.models.news_source import NewsSource


class BaseFetcher(ABC):
    """
    کلاس پایه برای دریافت خبر
    """

    def __init__(self, source: NewsSource):
        self.source = source

    @abstractmethod
    async def fetch(self) -> List[RawNews]:
        """
        دریافت خبرها
        """
        pass

    @property
    def source_name(self) -> str:
        return self.source.name

    @property
    def source_id(self) -> str:
        return self.source.id

    @property
    def source_type(self) -> str:
        return self.source.source_type
