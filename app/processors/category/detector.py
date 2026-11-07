from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.category.keywords import CATEGORY_KEYWORDS
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


MIN_CATEGORY_SCORE = 2


# ----------------------------------------------------------------------
# اولویت دسته‌ها
# ----------------------------------------------------------------------
# در صورت برابر بودن امتیازها، دسته تخصصی‌تر باید انتخاب شود.
#
# ورزش و هواشناسی عمداً قبل از سیاست و ایران قرار گرفته‌اند:
#
#   فوتبال → sport
#   هواشناسی → weather
#
# نباید صرفاً به خاطر وجود کلمات سیاسی یا نام ایران،
# دسته خبر اشتباه تشخیص داده شود.
#
CATEGORY_PRIORITY = (
    "sport",
    "weather",
    "economy",
    "technology",
    "health",
    "politics",
    "iran",
)


# ----------------------------------------------------------------------
# دسته‌های دارای اولویت از سمت منبع
# ----------------------------------------------------------------------
# منبعی که مشخصاً تک‌موضوعی است، می‌تواند امتیاز اولیه
# برای همان دسته دریافت کند.
#
# politics و iran عمداً در این بخش نیستند؛
# چون منابع چندموضوعی نباید باعث شوند همه خبرها
# سیاسی یا ایرانی تشخیص داده شوند.
#
SOURCE_PRIOR_CATEGORIES = {
    "economy",
    "technology",
    "health",
    "weather",
    "sport",
}

SOURCE_PRIOR_SCORE = 2


# ----------------------------------------------------------------------
# کلیدواژه‌های قوی فوتبال
# ----------------------------------------------------------------------
# این موارد برای تقویت تشخیص sport استفاده می‌شوند.
# هدف این نیست که هر خبری با یک کلمه مثل «بازی»
# ورزشی تشخیص داده شود؛ بنابراین فقط وقتی چند نشانه
# یا نشانه‌های مهم وجود داشته باشند، امتیاز بالا می‌رود.
#
STRONG_SPORT_TERMS = (
    "فوتبال",
    "لیگ",
    "جام",
    "تیم ملی",
    "بازیکن",
    "مربی",
    "سرمربی",
    "ترکیب",
    "دیدار",
    "مسابقه",
    "بازی",
    "گل",
    "دروازه",
    "استادیوم",
    "کاپیتان",
    "پنالتی",
    "آفساید",
    "تعویض",
    "کارت زرد",
    "کارت قرمز",
    "منچستریونایتد",
    "منچستر یونایتد",
    "منچسترسیتی",
    "منچستر سیتی",
    "لیورپول",
    "آرسنال",
    "چلسی",
    "تاتنهام",
    "رئال مادرید",
    "بارسلونا",
    "بایرن مونیخ",
    "پاری سن ژرمن",
    "پاریس سن ژرمن",
    "یوونتوس",
    "اینتر",
    "میلان",
    "رم",
    "اتلتیکو مادرید",
    "دورتموند",
    "لیگ برتر",
    "لیگ قهرمانان",
    "لیگ اروپا",
    "لیگ ملت‌ها",
    "جام جهانی",
    "یورو",
    "کوپا",
)


# ----------------------------------------------------------------------
# کلیدواژه‌های قوی هواشناسی
# ----------------------------------------------------------------------
# این دسته باید بر iran غلبه کند.
#
# مثال:
#
# «وضعیت آب‌وهوای تهران و کرج؛ پیش‌بینی بارش فردا»
#
# نباید به خاطر «تهران»، «کرج» یا «ایران»
# دسته iran دریافت کند.
#
STRONG_WEATHER_TERMS = (
    "هواشناسی",
    "آب و هوا",
    "آب‌وهوا",
    "وضعیت هوا",
    "پیش‌بینی هوا",
    "پیش‌بینی آب و هوا",
    "پیش‌بینی آب‌وهوا",
    "بارش",
    "بارندگی",
    "رگبار",
    "رعدوبرق",
    "رعد و برق",
    "برف",
    "باران",
    "تگرگ",
    "طوفان",
    "گرد و غبار",
    "گردوغبار",
    "دمای هوا",
    "دمای",
    "کاهش دما",
    "افزایش دما",
    "سامانه بارشی",
    "سامانه باران",
    "هشدار هواشناسی",
    "هشدار جوی",
    "جوی",
    "هوای",
)


class CategoryDetector:
    """تشخیص دسته خبر با استفاده از عنوان، خلاصه و متن خبر."""

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # --------------------------------------------------------------
        # اگر SportDetector قبلاً ورزش را مشخص کرده باشد،
        # همان تشخیص اولویت قطعی دارد.
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
        # دریافت متن خبر
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

        # عنوان و خلاصه وزن بیشتری دارند.
        primary_text = (
            f"{title} {summary}"
        ).strip()

        # متن کامل برای تشخیص تکمیلی استفاده می‌شود.
        full_text = (
            f"{primary_text} {content}"
        ).strip()

        scores = defaultdict(int)

        # --------------------------------------------------------------
        # امتیازدهی معمول بر اساس CATEGORY_KEYWORDS
        # --------------------------------------------------------------

        for category, keywords in (
            CATEGORY_KEYWORDS.items()
        ):

            for keyword in keywords:

                if not keyword:
                    continue

                # عنوان و خلاصه
                if keyword_in_text(
                    keyword,
                    primary_text,
                ):

                    scores[category] += 2

                # متن کامل
                elif (
                    content
                    and keyword_in_text(
                        keyword,
                        content,
                    )
                ):

                    scores[category] += 1

        # --------------------------------------------------------------
        # تشخیص تقویتی فوتبال
        # --------------------------------------------------------------
        # اگر SportDetector قبلاً چیزی مشخص نکرده باشد،
        # این بخش از متن خبر برای جلوگیری از اشتباه
        # sport → politics / iran استفاده می‌کند.
        # --------------------------------------------------------------

        sport_primary_hits = sum(
            1
            for term in STRONG_SPORT_TERMS
            if keyword_in_text(
                term,
                primary_text,
            )
        )

        sport_full_hits = sum(
            1
            for term in STRONG_SPORT_TERMS
            if keyword_in_text(
                term,
                full_text,
            )
        )

        if sport_primary_hits:

            # وجود نشانه فوتبال در عنوان/خلاصه
            # اهمیت بالایی دارد.
            scores["sport"] += (
                3
                + min(
                    sport_primary_hits,
                    3,
                )
            )

        elif sport_full_hits >= 2:

            # حداقل دو نشانه در متن کامل
            # تشخیص ورزشی را تقویت می‌کند.
            scores["sport"] += 3

        # --------------------------------------------------------------
        # تشخیص تقویتی هواشناسی
        # --------------------------------------------------------------
        # این قسمت برای حل مشکل:
        #
        # هواشناسی → ایران
        #
        # اضافه شده است.
        # --------------------------------------------------------------

        weather_primary_hits = sum(
            1
            for term in STRONG_WEATHER_TERMS
            if keyword_in_text(
                term,
                primary_text,
            )
        )

        weather_full_hits = sum(
            1
            for term in STRONG_WEATHER_TERMS
            if keyword_in_text(
                term,
                full_text,
            )
        )

        if weather_primary_hits:

            # نشانه هواشناسی در عنوان/خلاصه
            # باید وزن زیادی داشته باشد.
            scores["weather"] += (
                4
                + min(
                    weather_primary_hits,
                    3,
                )
            )

        elif weather_full_hits >= 2:

            scores["weather"] += 4

        # --------------------------------------------------------------
        # برچسب موضوعی منبع
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
        # منبع ورزشی
        # --------------------------------------------------------------

        if normalized_hints & {
            "sport",
            "sports",
            "football",
        }:

            scores["sport"] += 3

        # --------------------------------------------------------------
        # منبع هواشناسی
        # --------------------------------------------------------------

        if normalized_hints & {
            "weather",
            "meteorology",
        }:

            scores["weather"] += 3

        # --------------------------------------------------------------
        # اولویت منبع تک‌موضوعی
        # --------------------------------------------------------------

        first_hint = (
            str(
                source_hints[0]
            ).strip().lower()
            if source_hints
            else ""
        )

        if (
            first_hint
            in SOURCE_PRIOR_CATEGORIES
        ):

            scores[first_hint] += (
                SOURCE_PRIOR_SCORE
            )

        # --------------------------------------------------------------
        # ایران نباید فقط به دلیل نام ایران،
        # تهران، کرج و... انتخاب شود.
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
        # انتخاب دسته نهایی
        # --------------------------------------------------------------

        final_category = "general"

        if scores:

            best_score = max(
                scores.values()
            )

            if (
                best_score
                >= MIN_CATEGORY_SCORE
            ):

                tied_categories = {
                    category
                    for category, score
                    in scores.items()
                    if score == best_score
                }

                # در صورت تساوی، CATEGORY_PRIORITY
                # تعیین‌کننده است.
                final_category = next(
                    (
                        category
                        for category
                        in CATEGORY_PRIORITY
                        if category
                        in tied_categories
                    ),
                    sorted(
                        tied_categories
                    )[0],
                )

        # --------------------------------------------------------------
        # استفاده از برچسب منبع فقط در صورت نبود
        # تشخیص محتوایی کافی
        # --------------------------------------------------------------

        if (
            final_category
            == "general"
        ):

            valid_categories = set(
                CATEGORY_KEYWORDS.keys()
            )

            valid_hints = (
                normalized_hints
                & valid_categories
            )

            # ورزش اولویت دارد.
            if "sport" in valid_hints:

                final_category = "sport"

            # سپس هواشناسی.
            elif (
                "weather"
                in valid_hints
            ):

                final_category = "weather"

            # اگر فقط یک دسته معتبر از منبع وجود داشت،
            # همان دسته استفاده می‌شود.
            elif len(
                valid_hints
            ) == 1:

                final_category = next(
                    iter(
                        valid_hints
                    )
                )

        # --------------------------------------------------------------
        # ثبت دسته
        # --------------------------------------------------------------

        news.category = final_category

        logger.info(
            "Category: %s | source=%s | scores=%s",
            final_category,
            getattr(
                news,
                "source",
                "Unknown",
            ),
            dict(scores),
        )

        return news
