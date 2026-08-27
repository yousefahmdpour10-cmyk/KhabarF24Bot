"""
app/ai/content_generator.py

تولید تیتر فارسیِ روان و کامل + خلاصه‌ی فارسی برای یک خبر، با استفاده از
GeminiClient و پرامپت app/ai/prompts.py.

اگر فراخوانی AI به هر دلیلی شکست بخورد (کلید نامعتبر، rate limit، پاسخ
غیرمنتظره)، این فایل خبر را دست‌نخورده برمی‌گرداند ولی `news.content_generated`
را False می‌گذارد — تا لایه‌ی بالاتر (pipeline) تصمیم بگیرد که خبر
ترجمه‌نشده اصلاً منتشر نشود.
"""

import json
import re

from app.ai.client import GeminiClient
from app.ai.prompts import build_content_prompt
from app.models.raw_news import RawNews
from app.utils.logger import logger

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


class ContentGenerator:
    """تولید تیتر و خلاصه‌ی فارسیِ روان برای یک خبر خام."""

    def __init__(self):
        self.client = GeminiClient()

    async def process(self, news: RawNews) -> RawNews:
        source_text = news.content or news.summary or ""

        # پیش‌فرض: تا وقتی موفق نشده‌ایم ثابت‌شده، تولید محتوا ناموفق است
        news.content_generated = False

        if not news.title and not source_text:
            logger.warning("ContentGenerator: خبر بدون عنوان/متن، رد شد")
            return news

        prompt = build_content_prompt(news.title, source_text)
        raw_response = await self.client.generate(prompt)

        if not raw_response:
            logger.error("ContentGenerator: پاسخی از Gemini دریافت نشد")
            return news

        parsed = self._parse_json(raw_response)
        if not parsed:
            return news

        headline = (parsed.get("headline") or "").strip()
        summary = (parsed.get("summary") or "").strip()

        if not headline:
            logger.error("ContentGenerator: تیتر خالی از Gemini برگشت")
            return news

        news.title = headline
        if summary:
            news.summary = summary

        news.content_generated = True

        logger.info(f"ContentGenerator: تیتر تولید شد -> {headline[:60]}")

        return news

    @staticmethod
    def _parse_json(raw_text: str) -> dict | None:
        cleaned = _CODE_FENCE_RE.sub("", raw_text).strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.error(f"ContentGenerator: JSON نامعتبر از Gemini -> {raw_text[:200]}")
            return None

        if not isinstance(data, dict) or "headline" not in data or "summary" not in data:
            logger.error(f"ContentGenerator: ساختار JSON ناقص -> {data}")
            return None

        return data
