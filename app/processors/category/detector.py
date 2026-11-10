from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.category.keywords import CATEGORY_KEYWORDS
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


MIN_CATEGORY_SCORE = 2

# --------------------------------------------------------------
# اولویت دسته‌ها در صورت برابر بودن امتیاز
# --------------------------------------------------------------
#
# ورزش آخر است چون SportDetector قبل از این مرحله ورزش را
# مشخص می‌کند.
#
# نکته مهم:
# source_category_hint برای منابع تخصصی مثل BBC Health و BBC
# Business امتیاز جداگانه دارد و در حالت عادی باعث می‌شود
# دسته تخصصی منبع، دسته عمومی مثل politics را شکست دهد.
#
CATEGORY_PRIORITY = (
    "politics",
    "economy",
    "technology",
    "health",
    "weather",
    "iran",
    "sport",
)


# --------------------------------------------------------------
# دسته‌های تخصصی که source hint آنها معتبر است.
# --------------------------------------------------------------
#
# مثال:
#
# BBC Health:
# ["health"]
#
# BBC Business:
# ["economy"]
#
# CoinDesk:
# ["economy", ...]
#
# این منابع عملاً درباره یک حوزه مشخص فعالیت می‌کنند.
#
SOURCE_PRIOR_CATEGORIES = {
    "economy",
    "technology",
    "health",
}

# قبلاً 2 بود.
#
# مشکل:
# BBC Health + کلمه "Government"
#
# politics = 2
# health   = 2
#
# و چون politics در CATEGORY_PRIORITY جلوتر بود،
# خبر سلامت اشتباهاً politics می‌شد.
#
# با 3:
#
# politics = 2
# health   = 3
#
# بنابراین health انتخاب می‌شود.
#
SOURCE_PRIOR_SCORE = 3


class CategoryDetector:
    """تشخیص دسته خبر با استفاده از عنوان، خلاصه و متن خبر."""

    async def process(self, news: RawNews) -> RawNews:

        # ------------------------------------------------------
        # اگر SportDetector قبلاً رشته ورزشی را مشخص کرده،
        # همان اولویت مطلق دارد.
        # ------------------------------------------------------

        detected_sport = getattr(
            news,
            "sport",
            None,
        )

        if detected_sport:
            news.category = "sport"

            logger.info(
                "Category: sport | detected sport=%s",
                detected_sport,
            )

            return news

        # ------------------------------------------------------
        # متن خبر
        # ------------------------------------------------------

        title = getattr(
            news,
            "title",
            "",
        ) or ""

        summary = getattr(
            news,
            "summary",
            "",
        ) or ""

        content = getattr(
            news,
            "content",
            "",
        ) or ""

        # عنوان و خلاصه وزن بیشتری دارند.
        primary_text = (
            f"{title} {summary}"
        ).strip()

        full_text = (
            f"{primary_text} {content}"
        ).strip()

        scores = defaultdict(int)

        # ------------------------------------------------------
        # امتیازدهی بر اساس محتوای خبر
        # ------------------------------------------------------

        for category, keywords in CATEGORY_KEYWORDS.items():

            for keyword in keywords:

                if not keyword:
                    continue

                # ----------------------------------------------
                # عنوان + خلاصه
                # ----------------------------------------------

                if keyword_in_text(
                    keyword,
                    primary_text,
                ):
                    scores[category] += 2

                # ----------------------------------------------
                # متن کامل
                # ----------------------------------------------

                elif (
                    content
                    and keyword_in_text(
                        keyword,
                        content,
                    )
                ):
                    scores[category] += 1

        # ------------------------------------------------------
        # source category hints
        # ------------------------------------------------------
        #
        # مثال:
        #
        # BBC Health:
        # ["health"]
        #
        # Football360:
        # ["sport", "football"]
        #
        # BBC Business:
        # ["economy"]
        #
        # برای ورزش فقط به عنوان کمک استفاده می‌شود،
        # چون SportDetector قبلاً فرصت تشخیص داشته است.
        # ------------------------------------------------------

        source_hints = getattr(
            news,
            "source_category_hint",
            None,
        ) or []

        normalized_hints = {
            str(item).strip().lower()
            for item in source_hints
            if item
        }

        # ------------------------------------------------------
        # ورزش
        # ------------------------------------------------------

        if normalized_hints & {
            "sport",
            "sports",
            "football",
        }:
            scores["sport"] += 2

        # ------------------------------------------------------
        # منبع تخصصی
        # ------------------------------------------------------
        #
        # این بخش مهم‌ترین اصلاح است.
        #
        # BBC Health:
        # health +3
        #
        # BBC Business:
        # economy +3
        #
        # در نتیجه کلمات عمومی مثل Government نمی‌توانند
        # به‌سادگی یک خبر سلامت را سیاسی کنند.
        # ------------------------------------------------------

        first_hint = (
            str(source_hints[0]).strip().lower()
            if source_hints
            else ""
        )

        if first_hint in SOURCE_PRIOR_CATEGORIES:
            scores[first_hint] += SOURCE_PRIOR_SCORE

        # ------------------------------------------------------
        # دسته ایران
        # ------------------------------------------------------
        #
        # صرف وجود نام ایران نباید خبر را ایرانی کند.
        #
        # حداقل دو امتیاز محتوایی لازم است.
        # ------------------------------------------------------

        if scores.get("iran", 0) < MIN_CATEGORY_SCORE:
            scores.pop("iran", None)

        # ------------------------------------------------------
        # انتخاب دسته
        # ------------------------------------------------------

        final_category = "general"

        if scores:

            best_score = max(
                scores.values()
            )

            if best_score >= MIN_CATEGORY_SCORE:

                tied_categories = {
                    category
                    for category, score in scores.items()
                    if score == best_score
                }

                # در تساوی از ترتیب اولویت استفاده می‌کنیم.
                final_category = next(
                    (
                        category
                        for category in CATEGORY_PRIORITY
                        if category in tied_categories
                    ),
                    sorted(tied_categories)[0],
                )

        # ------------------------------------------------------
        # fallback به source hint
        # ------------------------------------------------------
        #
        # فقط زمانی که محتوای خبر هیچ دسته‌ای را
        # به حداقل امتیاز نرسانده باشد.
        # ------------------------------------------------------

        if final_category == "general":

            valid_categories = set(
                CATEGORY_KEYWORDS.keys()
            )

            valid_hints = (
                normalized_hints
                & valid_categories
            )

            if "sport" in valid_hints:

                final_category = "sport"

            elif len(valid_hints) == 1:

                final_category = next(
                    iter(valid_hints)
                )

        news.category = final_category

        logger.info(
            "Category: %s | source=%s | "
            "source_hints=%s | scores=%s",
            final_category,
            getattr(
                news,
                "source",
                "Unknown",
            ),
            list(normalized_hints),
            dict(scores),
        )

        return news
