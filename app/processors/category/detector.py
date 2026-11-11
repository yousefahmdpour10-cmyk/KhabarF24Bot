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
# دسته‌هایی که source hint آن‌ها می‌تواند کمک‌کننده باشد.
#
# source hint فقط یک امتیاز کمکی است و نباید جای متن خبر را بگیرد.
# ----------------------------------------------------------------------

SOURCE_PRIOR_CATEGORIES = {
    "economy",
    "technology",
    "health",
    "weather",
}

SOURCE_PRIOR_SCORE = 3


# ----------------------------------------------------------------------
# Sport source hints
#
# این‌ها فقط برای تشخیص رشته توسط SportDetector معتبرند.
# CategoryDetector نباید صرفاً به خاطر این hintها خبر را ورزشی کند.
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
    "mma",
    "formula1",
    "formula_1",
    "motogp",
    "motorsport",
    "cycling",
    "swimming",
    "athletics",
    "golf",
    "baseball",
    "american_football",
    "rugby",
    "table_tennis",
    "badminton",
    "handball",
    "chess",
    "esports",
    "futsal",
    "weightlifting",
    "taekwondo",
    "karate",
    "judo",
    "gymnastics",
}


class CategoryDetector:
    """
    تشخیص دسته اصلی خبر.

    SportDetector قبل از CategoryDetector اجرا می‌شود.

    بنابراین:

    1. اگر SportDetector ورزش را معتبر تشخیص داده باشد:
       category = sport

    2. اگر SportDetector ورزش را تشخیص نداده باشد:
       source ورزشی به‌تنهایی نباید category=sport ایجاد کند.

    3. دسته‌های سلامت، هواشناسی، اقتصاد، فناوری و سیاست
       از روی محتوای واقعی خبر تشخیص داده می‌شوند.
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # ==============================================================
        # اگر SportDetector قبلاً رشته معتبر پیدا کرده،
        # ورزش قطعی است.
        # ==============================================================

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

        # ==============================================================
        # متن خبر
        # ==============================================================

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

        scores = defaultdict(int)

        # ==============================================================
        # امتیازدهی keywordها
        #
        # عنوان + خلاصه = 2
        # متن کامل     = 1
        #
        # این باعث می‌شود کلمات مهم عنوان وزن بیشتری داشته باشند.
        # ==============================================================

        for category, keywords in CATEGORY_KEYWORDS.items():

            for keyword in keywords:

                if not keyword:
                    continue

                # ------------------------------------------------------
                # عنوان و خلاصه
                # ------------------------------------------------------

                if keyword_in_text(
                    keyword,
                    primary_text,
                ):

                    scores[category] += 2

                # ------------------------------------------------------
                # متن کامل
                # ------------------------------------------------------

                elif content and keyword_in_text(
                    keyword,
                    content,
                ):

                    scores[category] += 1

        # ==============================================================
        # source hints
        # ==============================================================

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

        # ==============================================================
        # SPORT
        #
        # بسیار مهم:
        #
        # source ورزشی به‌تنهایی sport نمی‌سازد.
        #
        # SportDetector مسئول تشخیص ورزش است.
        #
        # بنابراین اینجا دیگر:
        #
        # Football360 + خبر غیرورزشی
        #
        # نباید فقط با source hint وارد sport شود.
        # ==============================================================

        # عمداً هیچ امتیازی به sport از source hint نمی‌دهیم.

        # ==============================================================
        # source prior برای دسته‌های تخصصی
        # ==============================================================

        for category in SOURCE_PRIOR_CATEGORIES:

            if category in normalized_hints:

                scores[category] += (
                    SOURCE_PRIOR_SCORE
                )

        # ==============================================================
        # حذف ایران در صورت نداشتن شواهد کافی
        #
        # وجود یک اشاره ضعیف به ایران نباید هر خبر را ایرانی کند.
        # ==============================================================

        if scores.get(
            "iran",
            0,
        ) < MIN_CATEGORY_SCORE:

            scores.pop(
                "iran",
                None,
            )

        # ==============================================================
        # انتخاب دسته
        # ==============================================================

        final_category = "general"

        valid_scores = {
            category: score
            for category, score in scores.items()
            if score >= MIN_CATEGORY_SCORE
        }

        if valid_scores:

            best_score = max(
                valid_scores.values()
            )

            tied_categories = {
                category
                for category, score
                in valid_scores.items()
                if score == best_score
            }

            # ----------------------------------------------------------
            # حل تساوی بر اساس اولویت ثابت
            # ----------------------------------------------------------

            final_category = next(
                (
                    category
                    for category
                    in CATEGORY_PRIORITY
                    if category in tied_categories
                ),
                sorted(
                    tied_categories
                )[0],
            )

        # ==============================================================
        # fallback محدود
        #
        # اگر هیچ دسته‌ای امتیاز کافی نگرفت:
        #
        # - sport هرگز صرفاً با source hint انتخاب نمی‌شود.
        # - دسته تخصصی منبع فقط وقتی پذیرفته می‌شود که
        #   حداقل یک نشانه واقعی در متن داشته باشد.
        # ==============================================================

        if final_category == "general":

            valid_categories = set(
                CATEGORY_KEYWORDS.keys()
            )

            valid_hints = (
                normalized_hints
                & valid_categories
            )

            # ----------------------------------------------------------
            # sport عمداً حذف می‌شود.
            #
            # چون SportDetector باید قبل از این مرحله تصمیم گرفته باشد.
            # ----------------------------------------------------------

            valid_hints.discard(
                "sport"
            )

            if len(valid_hints) == 1:

                hinted_category = next(
                    iter(valid_hints)
                )

                # فقط وقتی hint را قبول می‌کنیم که
                # خود متن حداقل یک نشانه از آن دسته داشته باشد.
                if scores.get(
                    hinted_category,
                    0,
                ) > 0:

                    final_category = (
                        hinted_category
                    )

        # ==============================================================
        # ثبت نتیجه
        # ==============================================================

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
