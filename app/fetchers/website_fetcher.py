"""
Website Fetcher

دریافت خبر از وب‌سایت‌هایی که RSS ندارند.
"""

from typing import List

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.logger import logger


class WebsiteFetcher(BaseFetcher):
    """
    دریافت خبر از وب‌سایت
    """

    async def fetch(self) -> List[RawNews]:
        """
        این کلاس در نسخه پایه فقط یک اسکلت است.

        هر سایت در آینده Parser اختصاصی خودش را خواهد داشت.
        """

        logger.info(f"Fetching website: {self.source.name}")

        news_list: List[RawNews] = []

        try:

            if not self.source.supports_scraping:

                logger.warning(
                    f"{self.source.name} does not support scraping."
                )

                return news_list

            # Parser اختصاصی هر سایت
            #
            # مثال:
            #
            # if self.source.id == "vahid":
            #     ...
            #
            # elif self.source.id == "hengaw":
            #     ...
            #
            # elif self.source.id == "romano":
            #     ...

        except Exception as e:

            logger.exception(e)

        return news_list
