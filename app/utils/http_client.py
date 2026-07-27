# app/utils/http_client.py

"""
HTTP Client

مدیریت تمام درخواست‌های HTTP پروژه
"""

import asyncio
from typing import Optional

import aiohttp


class HTTPClient:
    """
    HTTP Client مشترک برای کل پروژه
    """

    DEFAULT_TIMEOUT = 20

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = 3,
    ):
        self.timeout = timeout
        self.retries = retries

    async def get(
        self,
        url: str,
        headers: Optional[dict] = None,
    ) -> Optional[str]:
        """
        ارسال درخواست GET

        Returns:
            متن صفحه یا None
        """

        request_headers = self.DEFAULT_HEADERS.copy()

        if headers:
            request_headers.update(headers)

        timeout = aiohttp.ClientTimeout(total=self.timeout)

        for attempt in range(self.retries):

            try:

                async with aiohttp.ClientSession(
                    timeout=timeout,
                    headers=request_headers,
                ) as session:

                    async with session.get(url) as response:

                        if response.status == 200:
                            return await response.text()

                        print(
                            f"HTTP {response.status} -> {url}"
                        )

            except asyncio.TimeoutError:

                print(f"Timeout -> {url}")

            except Exception as e:

                print(f"HTTP Error -> {e}")

            await asyncio.sleep(1)

        return None
