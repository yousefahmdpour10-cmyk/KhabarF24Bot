"""
دریافت اخبار از API
"""

from typing import List

import requests

from app.fetchers.base_fetcher import BaseFetcher
from app.models.news import News


class APIFetcher(BaseFetcher):
    """
    دریافت اخبار از API
    """

    async def fetch(self) -> List[News]:

        response = requests.get(
            self.source.url,
            timeout=20,
        )

        data = response.json()

        news_list = []

        # هر API ساختار مخصوص خودش را دارد.
        # بعداً برای هر سرویس Parser جداگانه خواهیم نوشت.

        return news_list
