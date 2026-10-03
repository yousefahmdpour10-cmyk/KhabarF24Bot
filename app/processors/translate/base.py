"""
Base Translator
"""

from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    """
    کلاس پایه تمام موتورهای ترجمه
    """

    @abstractmethod
    async def translate(
        self,
        text: str,
        source: str,
        target: str,
    ) -> str:
        pass
