"""
دریافت اخبار از API
"""

from typing import List

import requests

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.logger import logger


class APIFetcher(BaseFetcher):
    """
    دریافت اخبار از API
    """

    async def fetch(self) -> List[RawNews]:
        """
        دریافت داده از API

        ساختار هر API متفاوت است؛ بنابراین Parser اختصاصی
        هر سرویس در مراحل بعد اضافه خواهد شد.
        """

        news_list: List[RawNews] = []

        if not self.source.url:
            logger.warning(
                f"API URL is empty: {self.source.name}"
            )
            return news_list

        try:

            response = requests.get(
                self.source.url,
                timeout=20,
            )

            response.raise_for_status()

            data = response.json()

            # --------------------------------------------------
            # فعلاً Parser عمومی نداریم.
            # برای هر API، Parser اختصاصی اضافه خواهد شد.
            # --------------------------------------------------

            if not isinstance(data, (dict, list)):
                logger.warning(
                    f"Invalid API response: {self.source.name}"
                )
                return news_list

            return news_list

        except Exception as e:

            logger.exception(
                f"API fetch error for {self.source.name}: {e}"
            )

            return news_list
