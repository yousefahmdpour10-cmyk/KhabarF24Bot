
"""
app/ai/client.py

Gemini API Client
"""

import asyncio
import json
import random
from typing import Optional

import aiohttp

from config import settings
from app.utils.logger import logger


GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent"
)


class GeminiClient:
    DEFAULT_TIMEOUT = 60
    DEFAULT_RETRIES = 2
    MAX_RETRY_DELAY = 120

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ):
        self.timeout = timeout
        self.retries = max(1, retries)
        self.api_key = settings.GEMINI_API_KEY
        self.model = getattr(
            settings,
            "GEMINI_MODEL",
            "gemini-2.0-flash",
        )

    async def generate(self, prompt: str) -> Optional[str]:
        """ارسال prompt به Gemini و دریافت متن خروجی."""

        if not self.api_key:
            logger.error("GEMINI_API_KEY تنظیم نشده است")
            return None

        if not prompt or not prompt.strip():
            logger.warning("Gemini: prompt خالی است")
            return None

        url = GEMINI_ENDPOINT.format(model=self.model)

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
            },
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

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
                    headers=headers,
                ) as session:
                    async with session.post(
                        url,
                        json=payload,
                    ) as response:

                        if response.status == 200:
                            try:
                                data = await response.json(
                                    content_type=None
                                )
                            except (
                                ValueError,
                                aiohttp.ClientError,
                            ):
                                logger.error(
                                    "Gemini: پاسخ JSON قابل خواندن نیست"
                                )
                                return None

                            text = self._extract_text(data)

                            if text:
                                return text

                            logger.warning(
                                "Gemini: پاسخ موفق بود اما متن خروجی خالی است"
                            )
                            return None

                        body = await response.text()
                        body_preview = body[:1000]

                        if response.status == 429:
                            # ثبت علت واقعی محدودیت؛ کلید API ثبت نمی‌شود.
                            logger.warning(
                                "Gemini HTTP 429 | model=%s | "
                                "attempt=%s/%s | response=%s",
                                self.model,
                                attempt,
                                self.retries,
                                body_preview,
                            )

                            if attempt >= self.retries:
                                logger.warning(
                                    "Gemini rate limit؛ "
                                    "تعداد تلاش‌ها تمام شد"
                                )
                                return None

                            delay = self._retry_delay(
                                response.headers,
                                body,
                                attempt,
                            )

                            logger.warning(
                                "Gemini rate limit؛ "
                                "تلاش مجدد پس از %s ثانیه",
                                delay,
                            )

                            await asyncio.sleep(delay)
                            continue

                        if response.status in (400, 401, 403, 404):
                            logger.error(
                                "Gemini permanent HTTP error %s | "
                                "model=%s | response=%s",
                                response.status,
                                self.model,
                                body_preview,
                            )
                            return None

                        logger.warning(
                            "Gemini HTTP %s | attempt=%s/%s | response=%s",
                            response.status,
                            attempt,
                            self.retries,
                            body_preview,
                        )

            except asyncio.TimeoutError:
                logger.warning(
                    "Gemini timeout after %ss | attempt=%s/%s",
                    self.timeout,
                    attempt,
                    self.retries,
                )

            except aiohttp.ClientError as exc:
                logger.warning(
                    "Gemini connection error | attempt=%s/%s | %s",
                    attempt,
                    self.retries,
                    exc,
                )

            except Exception:
                logger.exception("Unexpected Gemini client error")
                return None

            if attempt < self.retries:
                delay = min(
                    15 * (2 ** (attempt - 1)),
                    60,
                )
                delay += random.uniform(0, 2)

                logger.warning(
                    "Gemini: تلاش مجدد پس از %.1f ثانیه",
                    delay,
                )
                await asyncio.sleep(delay)

        logger.error("Gemini: همه تلاش‌ها ناموفق بودند")
        return None

    @classmethod
    def _retry_delay(
        cls,
        headers,
        body: str,
        attempt: int,
    ) -> int:
        """محاسبه زمان انتظار بر اساس پاسخ سرویس."""

        retry_after = headers.get("Retry-After")

        if retry_after:
            try:
                return max(
                    1,
                    min(
                        int(float(retry_after)),
                        cls.MAX_RETRY_DELAY,
                    ),
                )
            except (ValueError, TypeError):
                pass

        try:
            data = json.loads(body)
            error = data.get("error", {})

            # گاهی اطلاعات محدودیت در پیام خطا مشخص است.
            message = str(error.get("message", ""))
            if message:
                logger.warning(
                    "Gemini error message: %s",
                    message[:500],
                )

            details = error.get("details", [])

            for item in details:
                if not isinstance(item, dict):
                    continue

                retry_delay = item.get("retryDelay")

                if retry_delay:
                    value = str(retry_delay).strip().lower()

                    if value.endswith("s"):
                        seconds = float(value[:-1])
                        return max(
                            1,
                            min(
                                int(seconds) + 1,
                                cls.MAX_RETRY_DELAY,
                            ),
                        )

        except (
            ValueError,
            TypeError,
            AttributeError,
        ):
            pass

        return min(
            10 * (2 ** (attempt - 1)),
            60,
        )

    @staticmethod
    def _extract_text(data: dict) -> Optional[str]:
        """استخراج متن از پاسخ Gemini."""

        try:
            candidates = data.get("candidates") or []

            if not candidates:
                prompt_feedback = data.get(
                    "promptFeedback",
                    {},
                )

                block_reason = prompt_feedback.get(
                    "blockReason",
                    "unknown",
                )

                logger.warning(
                    "Gemini: هیچ candidateای برنگشت | "
                    "block_reason=%s",
                    block_reason,
                )
                return None

            candidate = candidates[0]

            finish_reason = candidate.get(
                "finishReason",
                "unknown",
            )

            parts = (
                candidate.get("content", {})
                .get("parts", [])
            )

            texts = [
                part["text"]
                for part in parts
                if isinstance(part, dict)
                and isinstance(part.get("text"), str)
            ]

            result = "\n".join(texts).strip()

            if not result:
                logger.warning(
                    "Gemini: خروجی خالی است | finish_reason=%s",
                    finish_reason,
                )
                return None

            return result

        except (
            KeyError,
            IndexError,
            TypeError,
            AttributeError,
        ):
            logger.exception(
                "Unexpected Gemini response structure"
            )
            return None
