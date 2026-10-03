"""
Base Parser

تمام Parser های پروژه باید از این کلاس ارث‌بری کنند.
"""

from abc import ABC, abstractmethod
from typing import List

from bs4 import BeautifulSoup

from app.models.raw_news import RawNews
from app.models.news_source import NewsSource


class BaseParser(ABC):
    """
    کلاس پایه Parser
    """

    def __init__(self, source: NewsSource):
        self.source = source

    @abstractmethod
    async def parse(
        self,
        html: str,
    ) -> List[RawNews]:
        """
        تبدیل HTML به لیستی از خبرها
        """
        pass

    def soup(self, html: str) -> BeautifulSoup:
        """
        ساخت BeautifulSoup
        """

        return BeautifulSoup(
            html,
            "lxml",
        )

    def clean(self, text: str) -> str:
        """
        پاکسازی متن
        """

        return " ".join(
            text.strip().split()
        )
