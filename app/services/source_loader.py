"""
Source Loader

بارگذاری منابع خبری از فایل‌های JSON
"""

import json
from pathlib import Path
from typing import List

from app.models.news_source import NewsSource
from app.utils.logger import logger


class SourceLoader:
    """
    بارگذاری منابع خبری
    """

    def __init__(
        self,
        source_dir: str = "data/sources",
    ):
        self.source_dir = Path(source_dir)

    def load(self) -> List[NewsSource]:
        """
        بارگذاری تمام منابع
        """

        sources: List[NewsSource] = []

        if not self.source_dir.exists():

            logger.warning(
                f"Source directory not found: {self.source_dir}"
            )

            return sources

        for file in self.source_dir.glob("*.json"):

            try:

                with open(
                    file,
                    "r",
                    encoding="utf-8",
                ) as f:

                    data = json.load(f)

                for item in data:

                    sources.append(
                        NewsSource(**item)
                    )

                logger.info(
                    f"Loaded {len(data)} sources from {file.name}"
                )

            except Exception as e:

                logger.exception(e)

        logger.info(
            f"Total sources loaded: {len(sources)}"
        )

        return sources
