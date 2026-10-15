"""
تولید تیتر و خلاصه فارسی خبر با استفاده از Gemini.
"""

import json
import re

from app.ai.client import GeminiClient
from app.ai.prompts import build_content_prompt
from app.models.raw_news import RawNews
from app.utils.logger import logger


_CODE_FENCE_RE = re.compile(
    r"^```(?:json)?\s*|\s*```$",
    re.IGNORECASE | re.MULTILINE,
)


class ContentGenerator:
    """تولید تیتر و خلاصه فارسی روان برای خبر خام."""

    def __init__(self):
        self.client = GeminiClient()

    async def process(self, news: RawNews) -> RawNews:
        # متن محتوا و خلاصه را جداگانه دریافت می‌کنیم.
        content = str(getattr(news, "content", "") or "").strip()
        summary = str(getattr(news, "summary", "") or "").strip()

        # از متن طولانی‌تر برای تولید خروجی استفاده می‌کنیم.
        source_text = content if len(content) >= len(summary) else summary

        news.content_generated = False

        if not news.title and not source_text:
            logger.warning(
                "ContentGenerator: خبر بدون عنوان و متن رد شد"
            )
            return news

        prompt = build_content_prompt(
            str(news.title or "").strip(),
            source_text,
        )

        try:
            raw_response = await self.client.generate(prompt)
        except Exception:
            logger.exception(
                "ContentGenerator: خطا هنگام دریافت پاسخ از Gemini"
            )
            return news

        if not raw_response:
            logger.error(
                "ContentGenerator: پاسخی از Gemini دریافت نشد"
            )
            return news

        parsed = self._parse_json(raw_response)

        if not parsed:
            return news

        headline = str(parsed.get("headline") or "").strip()
        generated_summary = str(parsed.get("summary") or "").strip()

        if not headline or not generated_summary:
            logger.error(
                "ContentGenerator: تیتر یا خلاصه خالی از Gemini برگشت"
            )
            return news

        news.title = headline
        news.summary = generated_summary
        news.content_generated = True

        logger.info(
            f"ContentGenerator: تیتر تولید شد -> {headline[:60]}"
        )

        return news

    @staticmethod
    def _parse_json(raw_text: str) -> dict | None:
        cleaned = _CODE_FENCE_RE.sub("", raw_text).strip()

        try:
            data = json.loads(cleaned)
        except (json.JSONDecodeError, TypeError):
            logger.error(
                "ContentGenerator: JSON نامعتبر از Gemini -> "
                f"{str(raw_text)[:200]}"
            )
            return None

        if not isinstance(data, dict):
            logger.error(
                "ContentGenerator: خروجی Gemini یک شیء JSON نیست"
            )
            return None

        if "headline" not in data or "summary" not in data:
            logger.error(
                "ContentGenerator: ساختار JSON ناقص است"
            )
            return None

        return data
