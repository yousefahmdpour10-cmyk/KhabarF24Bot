# app/utils/http_client.py

"""
HTTP Client
مدیریت درخواست‌های HTTP پروژه KhabarF24
"""

import asyncio
import logging
from typing import Optional

import aiohttp


logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client مشترک برای دریافت RSS و صفحات وب."""

    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRIES = 3

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml,"
            "application/rss+xml,application/atom+xml,"
            "text/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ):
        self.timeout = timeout
        self.retries = max(1, retries)

    async def get(
        self,
        url: str,
        headers: Optional[dict] = None,
    ) -> Optional[str]:
        """
        ارسال GET و بازگرداندن متن پاسخ.

        در صورت شکست درخواست، None برمی‌گرداند.
        """

        request_headers = self.DEFAULT_HEADERS.copy()

        if headers:
            request_headers.update(headers)

        timeout = aiohttp.ClientTimeout(
            total=self.timeout,
            connect=10,
            sock_connect=10,
            sock_read=self.timeout,
        )

        for attempt in range(1, self.retries + 1):
            try:
                async with aiohttp.ClientSession(
                    timeout=timeout,
                    headers=request_headers,
                    auto_decompress=True,
                    read_bufsize=64 * 1024,
                ) as session:
                    async with session.get(
                        url,
                        allow_redirects=True,
                    ) as response:

                        if response.status == 200:
                            return await response.text(
                                errors="replace"
                            )

                        logger.warning(
                            "HTTP %s | attempt=%s/%s | url=%s",
                            response.status,
                            attempt,
                            self.retries,
                            url,
                        )

                        # خطاهای دائمی معمولاً با تلاش مجدد رفع نمی‌شوند.
                        if response.status in (400, 401, 403, 404, 410):
                            return None

                        # بدنه پاسخ خوانده شود تا اتصال به‌درستی بسته شود.
                        await response.read()

            except asyncio.TimeoutError:
                logger.warning(
                    "HTTP timeout | attempt=%s/%s | url=%s",
                    attempt,
                    self.retries,
                    url,
                )

            except aiohttp.ClientError as exc:
                logger.warning(
                    "HTTP client error | attempt=%s/%s | url=%s | error=%s",
                    attempt,
                    self.retries,
                    url,
                    exc,
                )

            except Exception:
                logger.exception(
                    "Unexpected HTTP error | url=%s",
                    url,
                )
                return None

            if attempt < self.retries:
                await asyncio.sleep(min(attempt * 2, 6))

        return None
