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


# --------------------------------------------------------------
# آستانه خبر فوری
# --------------------------------------------------------------

BREAKING_THRESHOLD = 25

DEFAULT_SOURCE_SCORE = 5


class ImportanceScorer:

    async def process(self, news: RawNews) -> RawNews:
        title = str(
            getattr(news, "title", "") or ""
        )

        summary = str(
            getattr(news, "summary", "") or ""
        )

        source = str(
            getattr(news, "source", "") or "Unknown"
        )

        source_id = getattr(
            news,
            "source_id",
            None,
        )

        # ------------------------------------------------------
        # متن مورد استفاده برای تشخیص اهمیت
        # ------------------------------------------------------

        text = f"{title} {summary}"

        # ------------------------------------------------------
        # امتیاز رویداد
        # ------------------------------------------------------

        event_score = self._calculate_event_score(text)

        # ------------------------------------------------------
        # امتیاز دسته‌بندی
        # ------------------------------------------------------

        category = getattr(
            news,
            "category",
            None,
        )

        category = str(
            category or ""
        ).strip().lower()

        category_score = CATEGORY_SCORES.get(
            category,
            0,
        )

        # ------------------------------------------------------
        # امتیاز منبع
        #
        # source_id در اولویت است.
        # اگر source_id در جدول دستی نباشد،
        # priority منبع به عنوان fallback استفاده می‌شود.
        # ------------------------------------------------------

        source_score = get_source_score(
            source=news,
            source_id=source_id,
            default=DEFAULT_SOURCE_SCORE,
        )

        # ------------------------------------------------------
        # امتیاز دسته‌بندی
        #
        # قبلاً این قسمت:
        #
        #     min(category_score, 3)
        #
        # بود و باعث می‌شد مثلاً economy با امتیاز 5
        # عملاً فقط 3 امتیاز بگیرد.
        #
        # اکنون سقف پایه 5 است.
        # ------------------------------------------------------

        category_bonus = min(
            category_score,
            5,
        )

        # ------------------------------------------------------
        # پاداش محدود منبع برای اقتصاد
        #
        # منابع اقتصادی معتبر می‌توانند کمی امتیاز اضافه بگیرند،
        # اما source_score به تنهایی نباید باعث شود هر خبر عادی
        # تبدیل به خبر مهم شود.
        #
        # source_score:
        # 7 یا کمتر → 0
        # 8 → 1
        # 9 یا 10 → 2
        # ------------------------------------------------------

        source_bonus = 0

        if category == "economy":
            source_bonus = min(
                2,
                max(
                    0,
                    source_score - 7,
                ),
            )

        # ------------------------------------------------------
        # امتیاز نهایی
        # ------------------------------------------------------

        score = (
            event_score
            + category_bonus
            + source_bonus
        )

        news.importance_score = score

        news.is_breaking = (
            score >= BREAKING_THRESHOLD
        )

        # ------------------------------------------------------
        # ذخیره امتیاز منبع
        # ------------------------------------------------------

        try:
            news.source_score = source_score
        except (
            AttributeError,
            TypeError,
        ):
            pass

        # ------------------------------------------------------
        # لاگ تشخیصی
        # ------------------------------------------------------

        logger.info(
            "Importance Score | source=%s | "
            "source_id=%s | total=%s | event=%s | "
            "category=%s | category_bonus=%s | "
            "source_score=%s | source_bonus=%s | "
            "breaking=%s",
            source,
            source_id or "unknown",
            score,
            event_score,
            category,
            category_bonus,
            source_score,
            source_bonus,
            news.is_breaking,
        )

        return news

    # ==========================================================
    # محاسبه امتیاز کلیدواژه‌ها
    # ==========================================================

    @staticmethod
    def _calculate_event_score(text: str) -> int:
        """
        محاسبه امتیاز رویداد با جلوگیری از
        امتیازدهی تکراری به کلیدواژه‌های هم‌پوشان.

        مثال:

        "قیمت طلای ۱۸ عیار امروز افزایش یافت"

        ممکن است چند کلیدواژه منطبق شوند.
        کلیدواژه‌های هم‌پوشان نباید چند بار برای
        یک مفهوم واحد امتیاز کامل بگیرند.
        """

        matches = []

        # ------------------------------------------------------
        # پیدا کردن کلیدواژه‌های موجود
        # ------------------------------------------------------

        for keyword, value in KEYWORD_SCORES.items():

            if keyword_in_text(
                keyword,
                text,
            ):
                matches.append(
                    (
                        keyword,
                        value,
                    )
                )

        # ------------------------------------------------------
        # ابتدا عبارت‌های طولانی‌تر بررسی شوند.
        #
        # مثلاً:
        #
        # "قیمت طلای ۱۸ عیار"
        #
        # قبل از:
        #
        # "قیمت طلا"
        #
        # بررسی می‌شود.
        # ------------------------------------------------------

        matches.sort(
            key=lambda item: len(item[0]),
            reverse=True,
        )

        accepted_keywords = []

        total_score = 0

        # ------------------------------------------------------
        # حذف هم‌پوشانی
        # ------------------------------------------------------

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
