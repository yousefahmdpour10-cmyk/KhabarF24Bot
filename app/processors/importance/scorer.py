"""
Importance Scorer

محاسبه اهمیت خبر و تشخیص Breaking.

امتیاز نهایی از سه بخش تشکیل می‌شود:
1. Event Score     → اهمیت خودِ رویداد و کلیدواژه‌های آن
2. Category Bonus  → اهمیت ذاتی دسته خبر
3. Source Bonus    → اعتبار منبع، فقط در دسته‌های مناسب

نکته:
Source Score به‌تنهایی نباید یک خبر معمولی را Breaking کند.
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text

from .category_scores import CATEGORY_SCORES
from .keywords import KEYWORD_SCORES
from .source_scores import get_source_score


# ----------------------------------------------------------------------
# تنظیمات اصلی
# ----------------------------------------------------------------------

BREAKING_THRESHOLD = 25
DEFAULT_SOURCE_SCORE = 5


# دسته‌هایی که اعتبار منبع برای آن‌ها می‌تواند
# در اهمیت نهایی نقش داشته باشد.
SOURCE_BONUS_CATEGORIES = {
    "politics",
    "iran",
    "economy",
    "health",
    "weather",
    "technology",
}


class ImportanceScorer:
    """
    محاسبه امتیاز اهمیت خبر.

    فرمول:

        total =
            event_score
            + category_bonus
            + source_bonus

    Breaking زمانی فعال می‌شود که امتیاز به
    BREAKING_THRESHOLD برسد.
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        title = str(
            getattr(
                news,
                "title",
                "",
            ) or ""
        )

        summary = str(
            getattr(
                news,
                "summary",
                "",
            ) or ""
        )

        source = str(
            getattr(
                news,
                "source",
                "",
            ) or "Unknown"
        )

        source_id = getattr(
            news,
            "source_id",
            None,
        )

        # --------------------------------------------------------------
        # فقط عنوان + خلاصه
        #
        # متن کامل عمداً وارد امتیازدهی نمی‌شود؛
        # چون ممکن است ده‌ها کلیدواژه کم‌اهمیت داخل متن
        # وجود داشته باشد و امتیاز خبر را مصنوعی بالا ببرد.
        # --------------------------------------------------------------

        text = f"{title} {summary}".strip()

        # --------------------------------------------------------------
        # 1. امتیاز خود رویداد
        # --------------------------------------------------------------

        event_score = self._calculate_event_score(text)

        # --------------------------------------------------------------
        # 2. دسته خبر
        # --------------------------------------------------------------

        category = str(
            getattr(
                news,
                "category",
                None,
            ) or ""
        ).strip().lower()

        category_score = CATEGORY_SCORES.get(
            category,
            0,
        )

        # --------------------------------------------------------------
        # 3. امتیاز منبع
        # --------------------------------------------------------------

        source_score = get_source_score(
            source=news,
            source_id=source_id,
            default=DEFAULT_SOURCE_SCORE,
        )

        # --------------------------------------------------------------
        # Category Bonus
        #
        # قبلاً همه دسته‌ها حداکثر 5 امتیاز می‌گرفتند.
        #
        # اینجا برای دسته‌های بسیار مهم اجازه می‌دهیم
        # حداکثر 6 امتیاز وارد محاسبه شود.
        #
        # نتیجه:
        #
        # politics = 6
        # iran     = 6
        # health   = 6
        # weather  = 6
        # economy  = 5
        # technology = 3
        # sport    = 3
        # general  = 1
        # --------------------------------------------------------------

        category_bonus = min(
            category_score,
            6,
        )

        # --------------------------------------------------------------
        # 4. Source Bonus
        #
        # منبع معتبر به‌تنهایی خبر را Breaking نمی‌کند.
        #
        # فقط برای دسته‌های مهم فعال است.
        #
        # score >= 9 → +2
        # score >= 8 → +1
        # کمتر از 8 → +0
        #
        # برای ورزش عمداً غیرفعال است تا خبرهای معمول ورزشی
        # به خاطر اعتبار منبع بیش از حد بالا نروند.
        # --------------------------------------------------------------

        source_bonus = 0

        if category in SOURCE_BONUS_CATEGORIES:

            if source_score >= 9:
                source_bonus = 2

            elif source_score >= 8:
                source_bonus = 1

        # --------------------------------------------------------------
        # امتیاز نهایی
        # --------------------------------------------------------------

        score = (
            event_score
            + category_bonus
            + source_bonus
        )

        news.importance_score = score

        news.is_breaking = (
            score >= BREAKING_THRESHOLD
        )

        # --------------------------------------------------------------
        # ذخیره امتیاز منبع روی مدل
        # --------------------------------------------------------------

        try:
            news.source_score = source_score

        except (
            AttributeError,
            TypeError,
        ):
            pass

        logger.info(
            "Importance Score | "
            "source=%s | "
            "source_id=%s | "
            "total=%s | "
            "event=%s | "
            "category=%s | "
            "category_bonus=%s | "
            "source_score=%s | "
            "source_bonus=%s | "
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

    @staticmethod
    def _calculate_event_score(
        text: str,
    ) -> int:
        """
        محاسبه امتیاز رویداد از روی کلیدواژه‌های اهمیت.

        کلیدواژه‌های طولانی‌تر اولویت دارند تا عبارت‌های
        عمومی‌تر باعث دوباره‌شماری نشوند.

        مثال:

        «شیوع آنفلوآنزا»

        نباید همزمان امتیاز:
        شیوع
        آنفلوآنزا
        شیوع بیماری
        ...
        را به شکل مصنوعی چند برابر دریافت کند.
        """

        matches = []

        # --------------------------------------------------------------
        # پیدا کردن کلیدواژه‌های موجود
        # --------------------------------------------------------------

        for keyword, value in KEYWORD_SCORES.items():

            if not keyword:
                continue

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

        # --------------------------------------------------------------
        # عبارت‌های طولانی‌تر اول بررسی شوند.
        # --------------------------------------------------------------

        matches.sort(
            key=lambda item: len(
                item[0]
            ),
            reverse=True,
        )

        accepted_keywords = []
        total_score = 0

        # --------------------------------------------------------------
        # حذف overlap
        # --------------------------------------------------------------

        for keyword, value in matches:

            normalized_keyword = str(
                keyword
            ).casefold()

            overlaps = any(
                normalized_keyword in accepted.casefold()
                or accepted.casefold() in normalized_keyword
                for accepted in accepted_keywords
            )

            if overlaps:
                continue

            accepted_keywords.append(
                keyword
            )

            total_score += value

        return total_score
