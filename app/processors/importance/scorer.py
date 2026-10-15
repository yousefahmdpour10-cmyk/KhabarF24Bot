"""
Importance Scorer

محاسبه اهمیت واقعی رویداد و تشخیص خبر فوری
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text

from .category_scores import CATEGORY_SCORES
from .keywords import KEYWORD_SCORES
from .source_scores import SOURCE_SCORES


# فقط امتیاز رویداد و دسته در تشخیص خبر فوری نقش دارند.
# امتیاز منبع جداگانه محاسبه می‌شود.
BREAKING_THRESHOLD = 25


class ImportanceScorer:
    async def process(self, news: RawNews) -> RawNews:

        title = getattr(news, "title", "") or ""
        summary = getattr(news, "summary", "") or ""
        text = f"{title} {summary}"

        # امتیاز اهمیت رویداد
        event_score = self._calculate_event_score(text)

        # امتیاز دسته‌بندی
        category_score = CATEGORY_SCORES.get(
            getattr(news, "category", None),
            0,
        )

        # امتیاز منبع فقط برای ارزیابی داخلی اعتبار منبع است.
        # این امتیاز به‌تنهایی خبر را فوری نمی‌کند.
        source_score = SOURCE_SCORES.get(
            getattr(news, "source", None),
            0,
        )

        # امتیاز نهایی اهمیت خبر:
        # رویداد + سهم محدود دسته‌بندی
        # بدون افزودن امتیاز منبع
        score = event_score + min(category_score, 3)

        news.importance_score = score
        news.is_breaking = score >= BREAKING_THRESHOLD

        # اگر مدل این فیلد را داشته باشد، امتیاز منبع
        # برای گزارش‌گیری داخلی نیز ذخیره می‌شود.
        if hasattr(news, "source_score"):
            news.source_score = source_score

        logger.info(
            "Importance Score: %s | event=%s | category=%s | "
            "source_score=%s%s",
            score,
            event_score,
            category_score,
            source_score,
            " [BREAKING]" if news.is_breaking else "",
        )

        return news

    @staticmethod
    def _calculate_event_score(text: str) -> int:
        """
        محاسبه امتیاز رویداد.

        اگر چند عبارت کلیدواژه‌ای هم‌پوشانی داشته باشند،
        عبارت طولانی‌تر اولویت می‌گیرد تا یک مفهوم چند بار
        امتیاز کامل دریافت نکند.
        """

        matches = []

        for keyword, value in KEYWORD_SCORES.items():
            if keyword_in_text(keyword, text):
                matches.append(
                    (keyword, value)
                )

        # ابتدا عبارت‌های طولانی‌تر بررسی می‌شوند.
        matches.sort(
            key=lambda item: len(item[0]),
            reverse=True,
        )

        accepted_keywords = []
        total_score = 0

        for keyword, value in matches:

            # اگر عبارت کوتاه‌تر بخشی از عبارت پذیرفته‌شده
            # باشد، دوباره برای همان مفهوم امتیاز نمی‌گیرد.
            overlaps = any(
                keyword.lower() in accepted.lower()
                or accepted.lower() in keyword.lower()
                for accepted in accepted_keywords
            )

            if overlaps:
                continue

            accepted_keywords.append(keyword)
            total_score += value

        return total_score
