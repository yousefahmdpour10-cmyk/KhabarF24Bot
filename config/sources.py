"""
مدیریت منابع خبری

این فایل مسئول بارگذاری منابع خبری از فایل‌های JSON است.
"""

from pathlib import Path
import json
import logging
from typing import List

from app.models.news_source import NewsSource


logger = logging.getLogger(__name__)


# مسیر پوشه منابع
SOURCES_DIR = Path("data/sources")


def load_sources() -> List[NewsSource]:
    """
    تمام منابع خبری را از فایل‌های JSON بارگذاری می‌کند.
    """

    sources: List[NewsSource] = []

    if not SOURCES_DIR.exists():
        logger.warning("Sources directory not found: %s", SOURCES_DIR)
        return sources

    for json_file in sorted(SOURCES_DIR.glob("*.json")):

        try:

            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                logger.warning("%s is not a list.", json_file.name)
                continue

            for item in data:

                try:
                    source = NewsSource(**item)
                    sources.append(source)

                except Exception as error:
                    logger.error(
                        "Invalid source in %s : %s",
                        json_file.name,
                        error,
                    )

        except Exception as error:

            logger.error(
                "Cannot load %s : %s",
                json_file.name,
                error,
            )

    logger.info("%d news sources loaded.", len(sources))

    return sources
