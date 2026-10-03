"""
Google Translator Engine
"""

from deep_translator import GoogleTranslator

from app.utils.logger import logger
from .base import BaseTranslator


class GoogleTranslateEngine(BaseTranslator):

    async def translate(
        self,
        text: str,
        source: str,
        target: str,
    ) -> str:

        if not text.strip():
            return text

        try:

            translated = GoogleTranslator(
                source=source,
                target=target,
            ).translate(text)

            return translated

        except Exception as e:

            logger.exception(e)

            return text
