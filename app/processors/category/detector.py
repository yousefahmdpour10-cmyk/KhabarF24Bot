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
# ورزش و هواشناسی عمداً قبل از سیاست و ایران قرار گرفته‌اند.
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

STRONG_SPORT_TERMS = (
    "فوتبال",
    "فوتبالی",
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

STRONG_WEATHER_TERMS = (
    "هواشناسی",
    "آب و هوا",
    "آب‌وهوا",
    "وضعیت هوا",
    "وضعیت آب و هوا",
    "وضعیت آب‌وهوا",
    "وضعیت جوی",
    "شرایط جوی",
    "ناپایداری جوی",
    "ناپایداری شدید جوی",
    "هوای ناپایدار",
    "شرایط جوی ناپایدار",
    "سامانه بارشی",
    "سامانه بارندگی",
    "سامانه جوی",
    "پیش‌بینی هوا",
    "پیش‌بینی آب و هوا",
    "پیش‌بینی آب‌وهوا",
    "بارش",
    "بارندگی",
    "بارش باران",
    "بارش شدید",
    "بارش سنگین",
    "بارش شدید باران",
    "بارش برف",
    "بارش شدید برف",
    "بارش رگباری",
    "رگبار",
    "رگبار باران",
    "باران",
    "برف",
    "رعدوبرق",
    "رعد و برق",
    "آذرخش",
    "صاعقه",
    "طوفان",
    "توفان",
    "طوفان شدید",
    "توفان سهمگین",
    "تندباد",
    "باد شدید",
    "بادهای شدید",
    "گردباد",
    "توفان استوایی",
    "توفان حاره‌ای",
    "هشدار هواشناسی",
    "اخطار هواشناسی",
    "هشدار جوی",
    "اخطار جوی",
    "هشدار آب‌وهوایی",
    "هشدار آب و هوایی",
    "هشدار بارندگی",
    "هشدار باران",
    "هشدار برف",
    "هشدار سیل",
    "اخطار سیل",
    "سیل",
    "سیلاب",
    "آب‌گرفتگی",
    "آبگرفتگی",
    "آب‌گرفتگی معابر",
    "آبگرفتگی معابر",
    "آبگرفتگی زمین‌های کم‌ارتفاع",
    "طغیان رودخانه",
    "طغیان رودخانه‌ها",
    "طغیان ناگهانی رودخانه",
    "سرریز رودخانه",
    "سطح آب رودخانه",
    "خشکسالی",
    "موج گرما",
    "موج سرما",
    "دمای هوا",
    "کاهش دما",
    "افزایش دما",
    "افت دما",
    "افزایش دمای هوا",
    "کاهش دمای هوا",
    "یخبندان",
    "سرمای شدید",
    "گرمای شدید",
    "دمای زیر صفر",
    "آلودگی هوا",
    "کیفیت هوا",
    "گرد و غبار",
    "گردوغبار",
    "ریزگرد",
    "مه",
    "مه غلیظ",
    "زلزله",
    "پس‌لرزه",
    "پس لرزه",
    "رانش زمین",
    "فوران آتشفشان",
    "آتشفشان",
    "آتش‌سوزی جنگل",
    "آتش سوزی جنگل",

    "Weather",
    "Weather Forecast",
    "Weather Warning",
    "Weather Alert",
    "Weather Conditions",
    "Severe Weather",
    "Storm",
    "Severe Storm",
    "Thunderstorm",
    "Heavy Rain",
    "Heavy Rainfall",
    "Rainfall",
    "Rain",
    "Heavy Snow",
    "Snowfall",
    "Snow",
    "Strong Winds",
    "High Winds",
    "Windstorm",
    "Tropical Storm",
    "Flood",
    "Flooding",
    "Flash Flood",
    "River Flooding",
    "River Overflow",
    "Drought",
    "Heatwave",
    "Heat Wave",
    "Cold Wave",
    "Cold Snap",
    "Temperature Drop",
    "Temperature Rise",
    "Freezing Conditions",
    "Air Pollution",
    "Dust Storm",
    "Dust",
    "Fog",
    "Earthquake",
    "Aftershock",
    "Landslide",
    "Volcanic Eruption",
    "Hurricane",
    "Tornado",
    "Wildfire",
)


class CategoryDetector:
    """تشخیص دسته خبر با استفاده از عنوان، خلاصه و متن خبر."""

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # --------------------------------------------------------------
        # SportDetector قبلاً ورزش را مشخص کرده باشد،
        # همان تشخیص قطعی است.
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
        # متن خبر
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

        full_text = (
            f"{primary_text} {content}"
        ).strip()

        scores = defaultdict(int)

        # --------------------------------------------------------------
        # امتیازدهی معمول CATEGORY_KEYWORDS
        # --------------------------------------------------------------

        for category, keywords in CATEGORY_KEYWORDS.items():

            for keyword in keywords:

                if not keyword:
                    continue

                if keyword_in_text(
                    keyword,
                    primary_text,
                ):

                    scores[category] += 2

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

            scores["sport"] += (
                3
                + min(
                    sport_primary_hits,
                    3,
                )
            )

        elif sport_full_hits >= 2:

            scores["sport"] += 3

        # --------------------------------------------------------------
        # تشخیص تقویتی هواشناسی
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

            scores["weather"] += (
                5
                + min(
                    weather_primary_hits,
                    4,
                )
            )

        elif weather_full_hits >= 2:

            scores["weather"] += 5

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

        if normalized_hints & {
            "sport",
            "sports",
            "football",
        }:

            scores["sport"] += 3

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
        # حذف تشخیص ضعیف ایران
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
        # تشخیص قطعی دسته‌های تخصصی
        # --------------------------------------------------------------
        #
        # این قسمت اصلاح اصلی است.
        #
        # اگر عنوان/خلاصه نشانه قوی هواشناسی داشته باشد،
        # ایران یا سیاست نباید بتوانند آن را شکست دهند.
        #
        # همین منطق برای فوتبال نیز اعمال می‌شود.
        #
        # مثال:
        #
        # «اختلاف دمای ۲۶ درجه‌ای در شهرهای ایران...»
        #
        # حتی اگر «ایران» چند بار تکرار شده باشد،
        # چون «دمای هوا» و «پیش‌بینی» وجود دارند،
        # دسته باید weather باشد.
        # --------------------------------------------------------------

        if weather_primary_hits >= 1:

            final_category = "weather"

            logger.info(
                "Category: weather | strong weather signal | "
                "primary_hits=%s | scores=%s",
                weather_primary_hits,
                dict(scores),
            )

            news.category = final_category

            return news

        # --------------------------------------------------------------
        # فوتبال تخصصی
        # --------------------------------------------------------------

        if sport_primary_hits >= 1:

            final_category = "sport"

            logger.info(
                "Category: sport | strong sport signal | "
                "primary_hits=%s | scores=%s",
                sport_primary_hits,
                dict(scores),
            )

            news.category = final_category

            return news

        # --------------------------------------------------------------
        # انتخاب عادی بر اساس امتیاز
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
        # استفاده از hint منبع فقط وقتی تشخیص محتوایی کافی نیست
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

            if "sport" in valid_hints:

                final_category = "sport"

            elif "weather" in valid_hints:

                final_category = "weather"

            elif len(valid_hints) == 1:

                final_category = next(
                    iter(
                        valid_hints
                    )
                )

        # --------------------------------------------------------------
        # ثبت دسته نهایی
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
