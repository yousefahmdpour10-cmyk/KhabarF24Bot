"""
Language Detector
تشخیص زبان خبر
"""

from langdetect import DetectorFactory
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from app.models.raw_news import RawNews
from app.utils.logger import logger

# برای اینکه نتیجه همیشه ثابت باشد
DetectorFactory.seed = 0


class LanguageDetector:
    """
    تشخیص زبان خبر
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        text = f"{news.title} {news.summary}".strip()

        if not text:
            news.language = "unknown"
            logger.info("Language: unknown (empty text)")
            return news

        try:
            news.language = detect(text)
            logger.info(f"Language: {news.language}")

        except LangDetectException:
            news.language = "unknown"
            logger.warning("Language detection failed")

        return news
