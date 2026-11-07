"""
Importance Scorer
محاسبه اهمیت رویداد و تشخیص خبر فوری KhabarF24
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text

from .category_scores import CATEGORY_SCORES
from .keywords import KEYWORD_SCORES
from .source_scores import get_source_score


BREAKING_THRESHOLD = 25
DEFAULT_SOURCE_SCORE = 5


class ImportanceScorer:

    async def process(self, news: RawNews) -> RawNews:
        title = str(getattr(news, "title", "") or "")
        summary = str(getattr(news, "summary", "") or "")

        source = str(
            getattr(news, "source", "") or "Unknown"
        )

        source_id = getattr(
            news,
            "source_id",
            None,
        )

        text = f"{title} {summary}"

        # ----------------------------------------------------
        # اهمیت رویداد بر اساس کلیدواژه‌ها
        # ----------------------------------------------------

        event_score = self._calculate_event_score(text)

        # ----------------------------------------------------
        # امتیاز دسته‌بندی
        # ----------------------------------------------------

        category = getattr(
            news,
            "category",
            None,
        )

        category_score = CATEGORY_SCORES.get(
            category,
            0,
        )

        # ----------------------------------------------------
        # امتیاز منبع
        #
        # source_id در اولویت است.
        # اگر source_id در جدول دستی نباشد،
        # priority منبع به عنوان fallback استفاده می‌شود.
        #
        # این امتیاز فعلاً فقط برای ارزیابی داخلی
        # و گزارش‌گیری است و مستقیماً به
        # importance_score اضافه نمی‌شود.
        # ----------------------------------------------------

        source_score = get_source_score(
            source=news,
            source_id=source_id,
            default=DEFAULT_SOURCE_SCORE,
        )

        # ----------------------------------------------------
        # امتیاز نهایی اهمیت
        #
        # عمداً فرمول فعلی حفظ شده است تا رفتار
        # Breaking اخبار موجود تغییر نکند.
        # ----------------------------------------------------

        score = (
            event_score
            + min(category_score, 3)
        )

        news.importance_score = score

        news.is_breaking = (
            score >= BREAKING_THRESHOLD
        )

        # ----------------------------------------------------
        # ذخیره امتیاز منبع برای گزارش‌گیری
        # و سازگاری با مدل‌های مختلف
        # ----------------------------------------------------

        try:
            news.source_score = source_score
        except (AttributeError, TypeError):
            pass

        # ----------------------------------------------------
        # لاگ تشخیصی
        # ----------------------------------------------------

        logger.info(
            "Importance Score | source=%s | "
            "source_id=%s | total=%s | event=%s | "
            "category=%s | source_score=%s | breaking=%s",
            source,
            source_id or "unknown",
            score,
            event_score,
            category_score,
            source_score,
            news.is_breaking,
        )

        return news

    @staticmethod
    def _calculate_event_score(text: str) -> int:
        """
        محاسبه امتیاز رویداد با جلوگیری از
        امتیازدهی تکراری به کلیدواژه‌های هم‌پوشان.
        """

        matches = []

        for keyword, value in KEYWORD_SCORES.items():

            if keyword_in_text(
                keyword,
                text,
            ):
                matches.append(
                    (keyword, value)
                )

        # ابتدا کلیدواژه‌های طولانی‌تر بررسی شوند
        matches.sort(
            key=lambda item: len(item[0]),
            reverse=True,
        )

        accepted_keywords = []
        total_score = 0

        for keyword, value in matches:

            normalized_keyword = (
                keyword.casefold()
            )

            overlaps = any(
                normalized_keyword in (
                    accepted.casefold()
                )
                or accepted.casefold() in (
                    normalized_keyword
                )
                for accepted in accepted_keywords
            )

            if overlaps:
                continue

            accepted_keywords.append(
                keyword
            )

            total_score += value

        return total_score
