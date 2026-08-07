"""
app/ai/client.py

Gemini API Client

مشابه سبک app/utils/http_client.py (retry, timeout, aiohttp session) ولی
مخصوص درخواست POST/JSON به Gemini، چون HTTPClient فقط GET رو پوشش می‌دهد.

نیازمند در .env:
    GEMINI_API_KEY=...
    GEMINI_MODEL=gemini-2.0-flash   (اختیاری، مقدار پیش‌فرض همین است)
"""

import asyncio
from typing import Optional

import aiohttp

from app.config import settings
from app.utils.logger import logger

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


class GeminiClient:
    """
    کلاینت ساده برای فراخوانی Gemini API (free tier).
    فقط یک وظیفه دارد: گرفتن یک prompt متنی و برگرداندن پاسخ خام متنی مدل.
    Parse کردن JSON خروجی مدل، مسئولیت لایه‌ی بالاتر (content_generator) است.
    """

    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = 3,
    ):
        self.timeout = timeout
        self.retries = retries
        self.api_key = settings.GEMINI_API_KEY
        self.model = getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")

    async def generate(self, prompt: str) -> Optional[str]:
        """
        ارسال یک prompt به Gemini و بازگرداندن متن خروجی مدل.

        Returns:
            متن پاسخ مدل یا None در صورت خطا/عدم موفقیت پس از retries.
        """
        if not self.api_key:
            logger.error("GEMINI_API_KEY تنظیم نشده است")
            return None

        url = GEMINI_ENDPOINT.format(model=self.model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
        }
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        for attempt in range(self.retries):
            try:
                async with aiohttp.ClientSession(
                    timeout=timeout,
                    headers=headers,
                ) as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            return self._extract_text(data)

                        # Rate limit: بی‌فایده است بلافاصله retry کنیم، کمی صبر می‌کنیم.
                        if response.status == 429:
                            logger.warning("Gemini rate limit hit, waiting...")
                            await asyncio.sleep(5)
                            continue

                        body = await response.text()
                        logger.error(f"Gemini HTTP {response.status} -> {body[:300]}")

            except asyncio.TimeoutError:
                logger.error("Gemini timeout")

            except Exception as e:
                logger.error(f"Gemini error -> {e}")

            await asyncio.sleep(1)

        return None

    @staticmethod
    def _extract_text(data: dict) -> Optional[str]:
        """استخراج متن ساده از ساختار پاسخ Gemini."""
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            logger.error(f"Unexpected Gemini response shape: {data}")
            return None
