"""
Category Detector

تشخیص دسته‌بندی اصلی خبر.

ترتیب اولویت:
politics
economy
technology
health
weather
iran
sport
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.category.keywords import CATEGORY_KEYWORDS
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


# حداقل امتیاز لازم برای انتخاب یک دسته
MIN_CATEGORY_SCORE = 2


# ----------------------------------------------------------------------
# اولویت دسته‌ها در صورت مساوی بودن امتیاز
# ----------------------------------------------------------------------

CATEGORY_PRIORITY = (
    "politics",
    "economy",
    "technology",
    "health",
    "weather",
    "iran",
    "sport",
)


# ----------------------------------------------------------------------
# دسته‌هایی که اگر منبع صراحتاً آن‌ها را اعلام کرده باشد،
# می‌توانند یک امتیاز اولیه دریافت کنند.
#
# این کار برای منابع تخصصی مثل منابع اقتصادی، فناوری و سلامت
# مفید است.
# ----------------------------------------------------------------------

SOURCE_PRIOR_CATEGORIES = {
    "economy",
    "technology",
    "health",
    "weather",
}

SOURCE_PRIOR_SCORE = 3


# ----------------------------------------------------------------------
# Sport source hint
# ----------------------------------------------------------------------

SPORT_HINTS = {
    "sport",
    "sports",
    "football",
    "basketball",
    "volleyball",
    "tennis",
    "wrestling",
    "boxing",
    "formula1",
    "formula_1",
    "motorsport",
    "baseball",
    "hockey",
}


class CategoryDetector:
    """
    تشخیص دسته اصلی خبر.

    نکته مهم:

    SportDetector قبل از CategoryDetector اجرا می‌شود.
    بنابراین اگر sport به‌صورت معتبر تشخیص داده شده باشد،
    دسته sport مستقیماً انتخاب می‌شود.

    اما اگر sport تشخیص داده نشده باشد، CategoryDetector
    نباید صرفاً با یک کلمه عمومی خبر را ورزشی کند.
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # --------------------------------------------------------------
        # اگر SportDetector قبلاً رشته معتبر پیدا کرده،
        # ورزش قطعی است.
        # --------------------------------------------------------------

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

        # --------------------------------------------------------------
        # متن اصلی
        # --------------------------------------------------------------

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

        primary_text = (
            f"{title} {summary}"
        ).strip()

        # برای تشخیص دسته، عنوان و خلاصه مهم‌تر هستند.
        # محتوا فقط به‌عنوان شواهد ضعیف‌تر استفاده می‌شود.
        full_text = (
            f"{primary_text} {content}"
        ).strip()

        scores = defaultdict(int)

        # --------------------------------------------------------------
        # امتیازدهی دسته‌ها
        # --------------------------------------------------------------

        for category, keywords in CATEGORY_KEYWORDS.items():

            for keyword in keywords:

                if not keyword:
                    continue

                # ------------------------------------------------------
                # عنوان + خلاصه
                # ------------------------------------------------------

                if keyword_in_text(
                    keyword,
                    primary_text,
                ):

                    scores[category] += 2

                # ------------------------------------------------------
                # متن کامل
                #
                # فقط اگر در عنوان/خلاصه نبود.
                # ------------------------------------------------------

                elif content and keyword_in_text(
                    keyword,
                    content,
                ):

                    scores[category] += 1

        # --------------------------------------------------------------
        # hint دسته منبع
        # --------------------------------------------------------------

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

        # --------------------------------------------------------------
        # ورزش
        #
        # فقط hint عمومی sport را به‌تنهایی برای دسته‌بندی کافی
        # نمی‌دانیم؛ SportDetector مسئول تشخیص رشته است.
        #
        # اگر خود SportDetector sport را پیدا نکرده،
        # یک خبر غیرورزشی نباید صرفاً به خاطر منبع ورزشی
        # sport شود.
        # --------------------------------------------------------------

        sport_hints = (
            normalized_hints
            & SPORT_HINTS
        )

        # اگر hint دقیق رشته وجود دارد، فقط یک امتیاز کمکی
        # می‌دهیم؛ نه اینکه مستقیماً دسته را sport کنیم.
        #
        # این باعث می‌شود Football360 در صورت وجود شواهد واقعی
        # ورزشی بهتر تشخیص داده شود، اما یک خبر غیرورزشی
        # صرفاً به خاطر منبع ورزشی وارد sport نشود.

        if sport_hints:

            scores["sport"] += 1

        # --------------------------------------------------------------
        # اولویت منبع برای دسته‌های تخصصی
        # --------------------------------------------------------------

        first_hint = ""

        if source_hints:

            first_hint = str(
                source_hints[0]
            ).strip().lower()

        if first_hint in SOURCE_PRIOR_CATEGORIES:

            scores[first_hint] += SOURCE_PRIOR_SCORE

        # --------------------------------------------------------------
        # ایران
        #
        # «ایران» به‌تنهایی نباید باعث شود هر خبری iran شود.
        #
        # بنابراین فقط وقتی امتیاز کافی ندارد، آن را حذف می‌کنیم.
        # --------------------------------------------------------------

        if scores.get(
            "iran",
            0,
        ) < MIN_CATEGORY_SCORE:

            scores.pop(
                "iran",
                None,
            )

        # --------------------------------------------------------------
        # انتخاب دسته
        # --------------------------------------------------------------

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

                # اولویت ثابت دسته‌ها
                # برای حل tie
                final_category = next(
                    (
                        category
                        for category in CATEGORY_PRIORITY
                        if category in tied_categories
                    ),
                    sorted(
                        tied_categories
                    )[0],
                )

        # --------------------------------------------------------------
        # fallback
        #
        # اگر هیچ دسته‌ای به حداقل امتیاز نرسید،
        # فقط hint معتبر منبع را بررسی می‌کنیم.
        #
        # sport در این قسمت عمداً استثنا دارد.
        # چون برای sport باید SportDetector تصمیم گرفته باشد.
        # --------------------------------------------------------------

        if final_category == "general":

            valid_categories = set(
                CATEGORY_KEYWORDS.keys()
            )

            valid_hints = (
                normalized_hints
                & valid_categories
            )

            # ورزش را فقط در صورت تشخیص واقعی SportDetector
            # قبول می‌کنیم.
            if "sport" in valid_hints:

                # بدون news.sport اینجا sport نمی‌کنیم.
                final_category = "general"

            elif len(valid_hints) == 1:

                final_category = next(
                    iter(valid_hints)
                )

        # --------------------------------------------------------------
        # ثبت نتیجه
        # --------------------------------------------------------------

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
