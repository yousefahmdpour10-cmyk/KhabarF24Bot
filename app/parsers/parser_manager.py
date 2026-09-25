"""
Parser Manager

انتخاب Parser مناسب برای هر منبع خبری
"""

from typing import Dict, Type

from app.models.news_source import NewsSource
from app.parsers.base_parser import BaseParser


class ParserManager:
    """
    مدیریت Parser ها
    """

    _parsers: Dict[str, Type[BaseParser]] = {}

    @classmethod
    def register(
        cls,
        source_id: str,
        parser: Type[BaseParser],
    ) -> None:
        """
        ثبت Parser
        """

        cls._parsers[source_id] = parser

    @classmethod
    def get(
        cls,
        source: NewsSource,
    ) -> BaseParser | None:
        """
        دریافت Parser مناسب
        """

        parser = cls._parsers.get(source.id)

        if parser is None:
            return None

        return parser(source)
