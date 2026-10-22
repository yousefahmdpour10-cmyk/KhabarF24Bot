"""
app/ai/client.py

Gemini API Client

سهمیه‌ی رایگان Gemini روزانه (مثلاً ۵۰۰ درخواست) است. برای اینکه این
سهمیه در چند ساعت اول نسوزد و بقیه‌ی روز کانال ساکت نماند:
- بین درخواست‌های عادی حداقل GEMINI_MIN_INTERVAL_SECONDS فاصله می‌گذاریم
  (پیش‌فرض ۱۷۵ ثانیه ≈ ۴۹۰ درخواست در روز)؛ خبر فوری از این فاصله معاف است؛
- اگر Gemini گفت سهمیه‌ی روزانه تمام شده و ساعت‌ها باید صبر کرد، تا آن
  زمان اصلاً درخواست نمی‌فرستیم (به‌جای ۱۲۰ ثانیه صبر و تلاش بی‌فایده).
"""

import asyncio
import json
import random
import re
import time
from typing import Optional

import aiohttp

from config import settings
from app.utils.logger import logger


GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent"
)

# حداقل فاصله‌ی دو درخواست عادی (ثانیه). ۸۶۴۰۰ / ۱۷۵ ≈ ۴۹۴ درخواست در روز.
MIN_INTERVAL_SECONDS = float(
    getattr(settings, "GEMINI_MIN_INTERVAL_SECONDS", 175)
)

# اگر زمان انتظار پیشنهادیِ Gemini از این بیشتر بود، یعنی سهمیه‌ی
# روزانه تمام شده (نه محدودیت چند‌ثانیه‌ای در دقیقه).
LONG_BLOCK_THRESHOLD_SECONDS = 10 * 60
MAX_BLOCK_SECONDS = 8 * 3600

_RETRY_IN_RE = re.compile(
    r"retry in\s+(?:(\d+)h)?(?:(\d+)m)?(?:([\d.]+)s)?",
    re.IGNORECASE,
)

# وضعیت مشترک بین همه‌ی نمونه‌ها (زمان‌ها با time.monotonic)
_next_call_at: float = 0.0
_blocked_until: float = 0.0


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

    # ------------------------------------------------------------------
    # نوبت‌دهی
    # ------------------------------------------------------------------

    @staticmethod
    def wait_seconds(priority: bool = False) -> float:
        """
        چند ثانیه تا اجازه‌ی درخواست بعدی؟ صفر یعنی همین الان آزاد است.
        priority=True (خبر فوری) فقط به بلوک سهمیه‌ی روزانه تن می‌دهد،
        نه به فاصله‌ی بین درخواست‌ها.
        """
        now = time.monotonic()
        wait = max(0.0, _blocked_until - now)

        if not priority:
            wait = max(wait, _next_call_at - now)

        return wait

    @staticmethod
    def _block_for(seconds: float) -> None:
        global _blocked_until

        seconds = min(seconds + 30, MAX_BLOCK_SECONDS)
        _blocked_until = time.monotonic() + seconds

        hours, rest = divmod(int(seconds), 3600)

        logger.warning(
            "Gemini: سهمیه‌ی روزانه تمام شده؛ تا حدود %s ساعت و %s دقیقه‌ی "
            "دیگر درخواستی ارسال نمی‌شود.",
            hours,
            rest // 60,
        )

    # ------------------------------------------------------------------
    # ارسال
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        priority: bool = False,
    ) -> Optional[str]:
        """ارسال prompt به Gemini و دریافت متن خروجی."""
        global _next_call_at

        if not self.api_key:
            logger.error("GEMINI_API_KEY تنظیم نشده است")
            return None

        if not prompt or not prompt.strip():
            logger.warning("Gemini: prompt خالی است")
            return None

        if self.wait_seconds(priority) > 0:
            # فراخواننده باید قبلاً wait_seconds را چک کرده باشد؛
            # این فقط برای محافظت است.
            return None

        # از همین لحظه نوبت درخواست بعدی عقب می‌رود
        _next_call_at = time.monotonic() + MIN_INTERVAL_SECONDS

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
                            logger.warning(
                                "Gemini HTTP 429 | model=%s | "
                                "attempt=%s/%s | response=%s",
                                self.model,
                                attempt,
                                self.retries,
                                body_preview,
                            )

                            seconds = self._retry_seconds(
                                response.headers,
                                body,
                            )

                            # سهمیه‌ی روزانه تمام شده: صبر چند‌ثانیه‌ای
                            # فایده ندارد، تا ریست شدن مکث می‌کنیم.
                            if (
                                seconds is not None
                                and seconds > LONG_BLOCK_THRESHOLD_SECONDS
                            ):
                                self._block_for(seconds)
                                return None

                            if attempt >= self.retries:
                                logger.warning(
                                    "Gemini rate limit؛ "
                                    "تعداد تلاش‌ها تمام شد"
                                )
                                return None

                            delay = self._retry_delay(seconds, attempt)

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

    # ------------------------------------------------------------------
    # تحلیل پاسخ خطا
    # ------------------------------------------------------------------

    @staticmethod
    def _retry_seconds(headers, body: str) -> Optional[float]:
        """
        زمان انتظاری که خود Gemini پیشنهاد داده (ثانیه)، یا None.
        سه منبع: هدر Retry-After، فیلد retryDelay در details، و متن
        پیام ("Please retry in 4h34m42.9s").
        """

        retry_after = headers.get("Retry-After") if headers else None

        if retry_after:
            try:
                return float(retry_after)
            except (ValueError, TypeError):
                pass

        try:
            data = json.loads(body)
            details = (data.get("error") or {}).get("details") or []

            for item in details:
                if not isinstance(item, dict):
                    continue

                value = str(item.get("retryDelay", "")).strip().lower()

                if value.endswith("s"):
                    return float(value[:-1])

        except (ValueError, TypeError, AttributeError):
            pass

        match = _RETRY_IN_RE.search(body or "")

        if match and any(match.groups()):
            hours, minutes, seconds = match.groups()
            return (
                int(hours or 0) * 3600
                + int(minutes or 0) * 60
                + float(seconds or 0)
            )

        return None

    @classmethod
    def _retry_delay(cls, seconds: Optional[float], attempt: int) -> int:
        """زمان انتظار برای محدودیت کوتاه (در دقیقه)."""

        if seconds is not None:
            return max(1, min(int(seconds) + 1, cls.MAX_RETRY_DELAY))

        return min(10 * (2 ** (attempt - 1)), 60)

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
