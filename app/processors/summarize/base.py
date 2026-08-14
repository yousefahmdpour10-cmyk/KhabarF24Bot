"""
Base Summarizer
"""

from abc import ABC, abstractmethod


class BaseSummarizer(ABC):

    @abstractmethod
    async def summarize(
        self,
        text: str,
    ) -> str:
        pass
