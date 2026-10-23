"""
Importance Scorer
محاسبه اهمیت رویداد و تشخیص خبر فوری KhabarF24
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text

from .category_scores import CATEGORY_SCORES
from .keywords import KEYWORD_SCORES
from .source_scores import SOURCE_SCORES


BREAKING_THRESHOLD = 25
DEFAULT_SOURCE_SCORE = 5


SOURCE_ALIASES = {
    "Hengaw": (
        "Hengaw",
        "Hengaw News",
        "Hengaw Organization",
        "Hengaw Organization for Human Rights",
    ),
    "Iran International": (
        "Iran International",
        "IranIntl",
        "Iran Intl",
    ),
    "Israel 14": (
        "Israel 14",
        "Israel 14 News",
        "Channel 14",
        "Now 14",
        "חדשות 14",
    ),
    "Varzesh3": (
        "Varzesh3",
        "Varzesh 3",
        "Varzesh3.com",
        "ورزش سه",
    ),
}


def _normalize_source_name(name: str) -> str:
    """یکسان‌سازی نام منبع برای مقایسه."""

    return " ".join(
        str(name or "").casefold().replace("_", " ").split()
    )


def _get_source_score(source_name: str) -> int:
    """پیداکردن امتیاز منبع با نام دقیق یا نام جایگزین."""

    normalized = _normalize_source_name(source_name)

    # ابتدا تطبیق مستقیم نام
    for name, score in SOURCE_SCORES.items():
        if _normalize_source_name(name) == normalized:
            return score

    # سپس تطبیق نام‌های جایگزین
    for canonical_name, aliases in SOURCE_ALIASES.items():
        normalized_aliases = {
            _normalize_source_name(alias)
            for alias in aliases
        }

        if normalized in normalized_aliases:
            for name, score in SOURCE_SCORES.items():
                if _normalize_source_name(name) == _normalize_source_name(
                    canonical_name
                ):
                    return score

            # اگر کلید اصلی وجود نداشت، امتیاز یکی از نام‌های جایگزین
            for name, score in SOURCE_SCORES.items():
                if _normalize_source_name(name) in normalized_aliases:
                    return score

    # تطبیق محدود برای نام‌هایی که پسوند اضافی دارند
    for name, score in SOURCE_SCORES.items():
        candidate = _normalize_source_name(name)

        if len(candidate) >= 5 and (
            normalized.startswith(candidate + " ")
            or candidate.startswith(normalized + " ")
        ):
            return score

    return DEFAULT_SOURCE_SCORE


class ImportanceScorer:

    async def process(self, news: RawNews) -> RawNews:
        title = str(getattr(news, "title", "") or "")
        summary = str(getattr(news, "summary", "") or "")
        source = str(getattr(news, "source", "") or "Unknown")

        text = f"{title} {summary}"

        # اهمیت رویداد بر اساس کلیدواژه‌ها
        event_score = self._calculate_event_score(text)

        # امتیاز دسته‌بندی
        category = getattr(news, "category", None)
        category_score = CATEGORY_SCORES.get(category, 0)

        # امتیاز منبع؛ فقط برای ارزیابی داخلی و گزارش‌گیری
        source_score = _get_source_score(source)

        # امتیاز نهایی مستقل از اعتبار منبع
        score = event_score + min(category_score, 3)

        news.importance_score = score
        news.is_breaking = score >= BREAKING_THRESHOLD

        # برای سازگاری با مدل‌های مختلف
        try:
            news.source_score = source_score
        except (AttributeError, TypeError):
            pass

        logger.info(
            "Importance Score | source=%s | total=%s | event=%s | "
            "category=%s | source_score=%s | breaking=%s",
            source,
            score,
            event_score,
            category_score,
            source_score,
            news.is_breaking,
        )

        return news

    @staticmethod
    def _calculate_event_score(text: str) -> int:
        """محاسبه امتیاز رویداد با جلوگیری از امتیازدهی تکراری."""

        matches = []

        for keyword, value in KEYWORD_SCORES.items():
            if keyword_in_text(keyword, text):
                matches.append((keyword, value))

        matches.sort(
            key=lambda item: len(item[0]),
            reverse=True,
        )

        accepted_keywords = []
        total_score = 0

        for keyword, value in matches:
            normalized_keyword = keyword.casefold()

            overlaps = any(
                normalized_keyword in accepted.casefold()
                or accepted.casefold() in normalized_keyword
                for accepted in accepted_keywords
            )

            if overlaps:
                continue

            accepted_keywords.append(keyword)
            total_score += value

        return total_score
