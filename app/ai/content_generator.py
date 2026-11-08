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

# خبری که تیتر کوتاه (کمتر از ۳ کلمه) و متن بسیار کم دارد (مثل «N12»
# از فیدهای Google News) ارزش یک درخواست Gemini را ندارد.
MIN_TITLE_WORDS = 3
MIN_TEXT_CHARS = 40

# خروجی کوتاه‌تر از این بی‌کیفیت است (مثلاً تیتر و خلاصه هر دو «N12»)
MIN_HEADLINE_CHARS = 12
MIN_SUMMARY_CHARS = 25


class ContentGenerator:
    """تولید تیتر و خلاصه فارسی روان برای خبر خام."""

    def __init__(self):
        self.client = GeminiClient()

    @staticmethod
    def _too_little_input(title: str, text: str) -> bool:
        words = re.findall(r"\w+", title)

        return len(words) < MIN_TITLE_WORDS and len(text) < MIN_TEXT_CHARS

    @staticmethod
    def _good_enough(headline: str, summary: str) -> bool:
        return (
            len(headline) >= MIN_HEADLINE_CHARS
            and len(summary) >= MIN_SUMMARY_CHARS
            and headline.strip() != summary.strip()
        )

    async def process(self, news: RawNews) -> RawNews:
        # متن محتوا و خلاصه را جداگانه دریافت می‌کنیم.
        content = str(getattr(news, "content", "") or "").strip()
        summary = str(getattr(news, "summary", "") or "").strip()

        # از متن طولانی‌تر برای تولید خروجی استفاده می‌کنیم.
        source_text = content if len(content) >= len(summary) else summary

        news.content_generated = False
        news.ai_paused = False
        news.junk_content = False

        title_text = str(news.title or "").strip()

        if not title_text and not source_text:
            logger.warning(
                "ContentGenerator: خبر بدون عنوان و متن رد شد"
            )
            return news

        # قبل از نوبت‌دهی Gemini: خبرِ بی‌محتوا نه سهمیه مصرف می‌کند نه
        # منتظر نوبت می‌ماند.
        if self._too_little_input(title_text, source_text):
            news.junk_content = True
            logger.info(
                "ContentGenerator: متن خبر برای ترجمه کافی نیست -> %s",
                title_text[:60],
            )
            return news

        # خبر فوری از فاصله‌ی بین درخواست‌ها معاف است
        priority = bool(getattr(news, "is_breaking", False))

        wait = GeminiClient.wait_seconds(priority)

        if wait > 0:
            # نه خطا، نه درخواست: نوبت این خبر نیست. main.py با دیدن
            # ai_paused بقیه‌ی کاندیدهای این چرخه را بررسی نمی‌کند.
            news.ai_paused = True
            logger.info(
                "ContentGenerator: Gemini تا %.0f ثانیه‌ی دیگر آماده نیست "
                "(سهمیه‌ی روزانه را پخش می‌کنیم)",
                wait,
            )
            return news

        # پست بازی (نتیجه/ترکیب ESPN): تیتر + ترجمه‌ی اسم‌ها در یک درخواست
        if getattr(news, "match_phase", None):
            return await self._process_match(news, priority)

        prompt = build_content_prompt(
            title_text,
            source_text,
        )

        try:
            raw_response = await self.client.generate(
                prompt,
                priority=priority,
            )
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

        if not self._good_enough(headline, generated_summary):
            # دوباره امتحان‌کردنش فقط سهمیه می‌سوزاند
            news.junk_content = True
            logger.error(
                "ContentGenerator: خروجی بی‌کیفیت است (تیتر=%r)",
                headline[:40],
            )
            return news

        news.title = headline
        news.summary = generated_summary
        news.content_generated = True

        logger.info(
            f"ContentGenerator: تیتر تولید شد -> {headline[:60]}"
        )

        return news

    async def _process_match(self, news: RawNews, priority: bool) -> RawNews:
        """تیتر فارسی و فارسی اسم‌های یک پست بازی (قالبش را match_post.py می‌چیند)."""

        from app.ai.match_prompt import build_match_prompt

        try:
            raw_response = await self.client.generate(
                build_match_prompt(news),
                priority=priority,
            )
        except Exception:
            logger.exception("ContentGenerator: خطا هنگام دریافت پاسخ از Gemini")
            return news

        if not raw_response:
            logger.error("ContentGenerator: پاسخی از Gemini دریافت نشد")
            return news

        cleaned = _CODE_FENCE_RE.sub("", raw_response).strip()

        try:
            data = json.loads(cleaned)
        except (json.JSONDecodeError, TypeError):
            logger.error(
                "ContentGenerator: JSON نامعتبر از Gemini (بازی) -> "
                f"{str(raw_response)[:200]}"
            )
            return news

        headline = str(data.get("headline") or "").strip() if isinstance(data, dict) else ""

        if len(headline) < MIN_HEADLINE_CHARS:
            logger.error("ContentGenerator: تیتر بازی خالی یا بسیار کوتاه است")
            return news

        names = data.get("names") if isinstance(data.get("names"), dict) else {}

        news.title = headline
        news.summary = ""
        news.fa_names = {
            str(key).strip(): str(value).strip()
            for key, value in names.items()
            if str(key).strip() and str(value).strip()
        }
        news.content_generated = True

        logger.info(
            f"ContentGenerator: تیتر بازی تولید شد -> {headline[:60]} "
            f"({len(news.fa_names)} اسم)"
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
