"""
Base Template
"""

from abc import ABC, abstractmethod

from app.models.raw_news import RawNews


class BaseTemplate(ABC):

    @abstractmethod
    async def format(
        self,
        news: RawNews,
    ) -> str:
        """
        ساخت متن نهایی خبر
        """
        pass
