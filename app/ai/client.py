"""
app/ai/client.py

Gemini API Client
"""

import asyncio
from typing import Optional

import aiohttp

from config import settings
from app.utils.logger import logger

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


class GeminiClient:

    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = 2,
    ):
        self.timeout = timeout
        self.retries = retries
        self.api_key = settings.GEMINI_API_KEY
        self.model = getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")

    async def generate(self, prompt: str) -> Optional[str]:
        """
        ارسال یک prompt به Gemini و بازگرداندن متن خروجی مدل.
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

                        # محدودیت نرخ: معمولاً محدودیت "در هر دقیقه" است،
                        # پس باید حداقل حدود یک دقیقه صبر کنیم، نه چند
                        # ثانیه -- وگرنه retry هم بلافاصله همان خطا را
                        # می‌گیرد چون هنوز داخل همان پنجره‌ی زمانی هستیم.
                        if response.status == 429:
                            logger.warning(
                                "Gemini rate limit hit, waiting 65s before retry..."
                            )
                            await asyncio.sleep(65)
                            continue

                        body = await response.text()
                        logger.error(f"Gemini HTTP {response.status} -> {body[:300]}")

            except asyncio.TimeoutError:
                logger.error("Gemini timeout")

            except Exception as e:
                logger.error(f"Gemini error -> {e}")

            await asyncio.sleep(3)

        return None

    @staticmethod
    def _extract_text(data: dict) -> Optional[str]:
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            logger.error(f"Unexpected Gemini response shape: {data}")
            return None
