from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.category.keywords import CATEGORY_KEYWORDS
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


MIN_CATEGORY_SCORE = 2

# در صورت برابر بودن امتیازها، این ترتیب برای انتخاب دسته استفاده می‌شود.
CATEGORY_PRIORITY = (
    "sport",
    "politics",
    "economy",
    "technology",
    "health",
    "weather",
    "iran",
)


class CategoryDetector:
    """تشخیص دسته خبر با استفاده از عنوان، خلاصه و متن خبر."""

    async def process(self, news: RawNews) -> RawNews:
        # اگر منبع یا پردازشگر قبلی ورزش را مشخص کرده، همان اولویت دارد.
        detected_sport = getattr(news, "sport", None)

        if detected_sport:
            news.category = "sport"
            logger.info(
                "Category: sport | detected sport=%s",
                detected_sport,
            )
            return news

        title = getattr(news, "title", "") or ""
        summary = getattr(news, "summary", "") or ""
        content = getattr(news, "content", "") or ""

        # عنوان و خلاصه وزن بیشتری در تشخیص دارند؛ متن کامل کمک تکمیلی است.
        primary_text = f"{title} {summary}".strip()
        full_text = f"{primary_text} {content}".strip()

        scores = defaultdict(int)

        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if not keyword:
                    continue

                # تطبیق در عنوان و خلاصه
                if keyword_in_text(keyword, primary_text):
                    scores[category] += 2

                # متن کامل فقط امتیاز تکمیلی می‌گیرد.
                elif content and keyword_in_text(keyword, content):
                    scores[category] += 1

        # اگر خبر ورزشی از قبل مشخص نشده، کلیدواژه‌ها و برچسب منبع کمک می‌کنند.
        source_hints = getattr(news, "source_category_hint", None) or []
        normalized_hints = {
            str(item).strip().lower()
            for item in source_hints
            if item
        }

        if normalized_hints & {"sport", "sports", "football"}:
            scores["sport"] += 2

        # نام ایران به‌تنهایی نباید باعث شود دسته خبر «ایران» شود.
        # برای دسته iran باید نشانه‌های محتوایی کافی وجود داشته باشد.
        if scores.get("iran", 0) < MIN_CATEGORY_SCORE:
            scores.pop("iran", None)

        final_category = "general"

        if scores:
            best_score = max(scores.values())

            if best_score >= MIN_CATEGORY_SCORE:
                tied_categories = {
                    category
                    for category, score in scores.items()
                    if score == best_score
                }

                final_category = next(
                    (
                        category
                        for category in CATEGORY_PRIORITY
                        if category in tied_categories
                    ),
                    sorted(tied_categories)[0],
                )

        # برچسب منبع فقط در صورت نبود تشخیص محتوایی استفاده می‌شود.
        if final_category == "general":
            valid_categories = set(CATEGORY_KEYWORDS.keys())
            valid_hints = normalized_hints & valid_categories

            if "sport" in valid_hints:
                final_category = "sport"
            elif len(valid_hints) == 1:
                final_category = next(iter(valid_hints))

        news.category = final_category

        logger.info(
            "Category: %s | source=%s | scores=%s",
            final_category,
            getattr(news, "source", "Unknown"),
            dict(scores),
        )

        return news
