"""
دریافت اخبار از وب‌سایت‌هایی که RSS ندارند
"""

from typing import List

import requests
from bs4 import BeautifulSoup

from app.fetchers.base_fetcher import BaseFetcher
from app.models.news import News


class WebsiteFetcher(BaseFetcher):
    """
    دریافت اخبار با Web Scraping
    """

    async def fetch(self) -> List[News]:

        response = requests.get(
            self.source.url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(response.text, "html.parser")

        news_list = []

        # هر سایت بعداً Parser مخصوص خودش را خواهد داشت.
        # فعلاً فقط اسکلت کلاس را می‌سازیم.

        return news_list
