"""
کلاس پایه برای تمام دریافت‌کننده‌های خبر

تمام Fetcher ها باید از این کلاس ارث‌بری کنند.
"""

from abc import ABC, abstractmethod
from typing import List

from app.models.news import News
from app.models.news_source import NewsSource


class BaseFetcher(ABC):
    """
    کلاس پایه دریافت خبر
    """

    def __init__(self, source: NewsSource):
        self.source = source

    @abstractmethod
    async def fetch(self) -> List[News]:
        """
        دریافت خبرها از منبع

        Returns:
            List[News]
        """
        pass

    async def validate(self, news: News) -> bool:
        """
        اعتبارسنجی اولیه خبر
        """

        if not news.title:
            return False

        if len(news.title.strip()) < 10:
            return False

        return True

    async def normalize(self, news: News) -> News:
        """
        یکسان‌سازی داده‌ها
        """

        news.title = news.title.strip()

        if news.summary:
            news.summary = news.summary.strip()

        return news
