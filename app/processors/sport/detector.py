"""
Sport Detector

تشخیص رشته ورزشی (و مسابقه‌ی مربوط به آن برای هشتگ)
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.sport.keywords import SPORTS
from app.processors.sport.league_detector import detect_league
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


# ----------------------------------------------------------------------
# حداقل امتیاز لازم برای تشخیص رشته ورزشی
# ----------------------------------------------------------------------

# یک کلیدواژه عمومی نباید به‌تنهایی خبر را ورزشی کند.
MIN_SPORT_SCORE = 2


# ----------------------------------------------------------------------
# کلمات عمومی که به‌تنهایی نشانه کافی برای ورزش نیستند
# ----------------------------------------------------------------------

GENERIC_SPORT_WORDS = {
    "اخراج",
    "برکناری",
    "مصدومیت",
    "مصدوم",
    "آسیب",
    "آسیب دیدگی",
    "شکست",
    "پیروزی",
    "برد",
    "باخت",
    "رکورد",
    "قهرمان",
    "قهرمانی",
    "بازگشت",
    "دیدار",
    "مقابل",
    "انتقال",
    "انتقالات",
    "سرمربی",
    "مربی",
    "کاپیتان",
    "بازیکن",
    "داور",
    "فدراسیون",
    "رقابت",
    "مسابقه",
    "تور",
    "لیگ",
    "جام",
    "فینال",
    "نیمه نهایی",
    "نیمه‌نهایی",
}


def _own_names(sport_id: str, sport: dict) -> set:
    """
    اسم خود رشته (فارسی و انگلیسی).

    مثلاً:
    volleyball / والیبال
    basketball / بسکتبال
    """

    names = {
        str(sport.get("name", "")).strip().lower(),
        sport_id.replace("_", " ").strip().lower(),
    }

    return {name for name in names if name}


def _is_generic_sport_keyword(keyword: str) -> bool:
    """
    مشخص می‌کند یک کلیدواژه بیش از حد عمومی است.

    این کلمات فقط وقتی همراه با نشانه‌های تخصصی رشته باشند
    می‌توانند به تشخیص ورزش کمک کنند.
    """

    normalized = str(keyword or "").strip().lower()

    return normalized in {
        item.lower()
        for item in GENERIC_SPORT_WORDS
    }


class SportDetector:
    """
    تشخیص رشته ورزشی.

    امتیازدهی:

    - نام مستقیم رشته: 3 امتیاز
    - کلیدواژه تخصصی/قوی: 2 امتیاز
    - کلیدواژه معمولی: 1 امتیاز
    - کلیدواژه عمومی ورزشی: به‌تنهایی کافی نیست

    نکته مهم:
    کلماتی مثل «اخراج»، «مصدومیت»، «شکست» و «پیروزی»
    نباید یک خبر سیاسی، اقتصادی، سلامت یا هر خبر غیرورزشی
    را فقط به خاطر وجود این کلمات ورزشی کنند.
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # --------------------------------------------------------------
        # اگر fetcher مطمئنی مثل ESPN رشته را قبلاً مشخص کرده،
        # همان تشخیص را حفظ می‌کنیم.
        # --------------------------------------------------------------

        if getattr(news, "sport", None):

            logger.info(
                "Sport: %s (از منبع مشخص شده)",
                getattr(
                    news,
                    "sport_name",
                    news.sport,
                ),
            )

            return news

        title = getattr(news, "title", "") or ""
        summary = getattr(news, "summary", "") or ""

        # فقط عنوان + خلاصه.
        # متن کامل عمداً وارد تشخیص رشته نمی‌شود.
        text = f"{title} {summary}".strip()

        scores = defaultdict(int)

        # --------------------------------------------------------------
        # تشخیص رشته از روی متن
        # --------------------------------------------------------------

        for sport_id, sport in SPORTS.items():

            own_names = _own_names(
                sport_id,
                sport,
            )

            strong_keywords = {
                str(keyword).strip().lower()
                for keyword in sport.get(
                    "strong_keywords",
                    [],
                )
                if keyword
            }

            for keyword in sport.get(
                "keywords",
                [],
            ):

                if not keyword:
                    continue

                keyword_normalized = (
                    str(keyword)
                    .strip()
                    .lower()
                )

                if not keyword_in_text(
                    keyword,
                    text,
                ):
                    continue

                # ------------------------------------------------------
                # نام مستقیم رشته
                # فوتبال / football
                # بسکتبال / basketball
                # ------------------------------------------------------

                if keyword_normalized in own_names:

                    scores[sport_id] += 3

                # ------------------------------------------------------
                # کلیدواژه تخصصی رشته
                # NBA / UFC / Wimbledon / pitcher / ...
                # ------------------------------------------------------

                elif keyword_normalized in strong_keywords:

                    scores[sport_id] += 2

                # ------------------------------------------------------
                # کلیدواژه‌های عمومی
                # ------------------------------------------------------

                elif _is_generic_sport_keyword(
                    keyword_normalized
                ):

                    # این کلمات به‌تنهایی نباید رشته را
                    # ورزشی تشخیص دهند.
                    scores[sport_id] += 0

                else:

                    scores[sport_id] += 1

        # --------------------------------------------------------------
        # hint منبع
        # --------------------------------------------------------------

        hint_sport = self._hint_sport(news)

        # --------------------------------------------------------------
        # انتخاب بهترین رشته
        # --------------------------------------------------------------

        if scores:

            best = max(
                scores,
                key=scores.get,
            )

            best_score = scores[best]

            # ----------------------------------------------------------
            # اگر امتیاز کافی نیست:
            #
            # فقط hint منبع را زمانی قبول می‌کنیم که خود منبع
            # مشخصاً تک‌رشته‌ای باشد و این خبر حداقل یک نشانه
            # ورزشی واقعی داشته باشد.
            # ----------------------------------------------------------

            if best_score < MIN_SPORT_SCORE:

                if hint_sport and best_score > 0:

                    best = hint_sport
                    best_score = MIN_SPORT_SCORE

                else:

                    best = None

            # ----------------------------------------------------------
            # اگر متن چند رشته را نشان دهد:
            #
            # hint منبع فقط وقتی برنده می‌شود که امتیاز متن
            # برای رشته دیگر خیلی ضعیف باشد.
            # ----------------------------------------------------------

            elif (
                hint_sport
                and best != hint_sport
                and best_score <= 2
            ):

                hint_score = scores.get(
                    hint_sport,
                    0,
                )

                if (
                    hint_score >= 2
                    or best_score <= 1
                ):

                    best = hint_sport

            # ----------------------------------------------------------
            # ثبت تشخیص
            # ----------------------------------------------------------

            if best:

                news.sport = best
                news.sport_name = SPORTS[best]["name"]
                news.sport_emoji = SPORTS[best]["emoji"]
                news.sport_hashtag = SPORTS[best]["hashtag"]

                logger.info(
                    "Sport: %s | score=%s | source_hint=%s",
                    news.sport_name,
                    scores.get(
                        best,
                        best_score,
                    ),
                    hint_sport,
                )

                # ------------------------------------------------------
                # تشخیص لیگ / جام
                # ------------------------------------------------------

                if not getattr(
                    news,
                    "league",
                    None,
                ):

                    league = detect_league(text)

                    if league:

                        news.league = league

                        logger.info(
                            "League: %s",
                            league,
                        )

                return news

        # --------------------------------------------------------------
        # نکته بسیار مهم:
        #
        # قبلاً اینجا اگر hint_sport وجود داشت، بدون هیچ نشانه متنی
        # خبر را ورزشی می‌کردیم.
        #
        # این رفتار حذف شده است.
        #
        # بنابراین:
        #
        # Football360 + خبر سیاسی
        # Football360 + خبر اقتصادی
        # Football360 + خبر سلامت
        #
        # فقط به دلیل منبع، sport نمی‌شوند.
        # --------------------------------------------------------------

        news.sport = None
        news.sport_name = None
        news.sport_emoji = None
        news.sport_hashtag = None

        return news

    @staticmethod
    def _hint_sport(news):
        """
        رشته‌ای که دسته‌های منبع مشخصاً نام می‌برند.

        مثال:
        ["sport", "football", "transfer"] → football

        برای منابع فارسی نیز معتبر است.

        مثال:
        Football360:
        ["sport", "football"] → football

        اما فقط وجود hint منبع به‌تنهایی برای ورزشی کردن
        یک خبر کافی نیست.
        """

        for hint in getattr(
            news,
            "source_category_hint",
            None,
        ) or []:

            normalized = str(
                hint
            ).strip().lower()

            if normalized in SPORTS:

                return normalized

        return None
