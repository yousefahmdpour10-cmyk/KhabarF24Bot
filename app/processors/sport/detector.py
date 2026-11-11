"""
Sport Detector

تشخیص رشته ورزشی و مسابقه‌ی مربوط به آن برای هشتگ
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.sport.keywords import SPORTS
from app.processors.sport.league_detector import detect_league
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


# ----------------------------------------------------------------------
# تنظیمات
# ----------------------------------------------------------------------

MIN_SPORT_SCORE = 2


# ----------------------------------------------------------------------
# کلمات عمومی ورزشی
#
# این کلمات به‌تنهایی نباید خبر را ورزشی کنند.
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


# ----------------------------------------------------------------------
# نشانه‌های عمومی اما واقعی ورزشی
#
# این‌ها مثل «اخراج» یا «شکست» بیش از حد عمومی نیستند،
# اما به‌تنهایی هم نباید هر خبر را ورزشی کنند.
# ----------------------------------------------------------------------

SPORT_CONTEXT_WORDS = {
    "تیم ملی",
    "تیم ملی فوتبال",
    "باشگاه",
    "بازیکن",
    "بازیکنان",
    "مربی",
    "سرمربی",
    "کاپیتان",
    "فدراسیون فوتبال",
    "فدراسیون ورزشی",
    "ورزشگاه",
    "ترکیب",
    "ترکیب اصلی",
    "نیمکت",
    "تعویض",
    "گل",
    "گلزنی",
    "گلزن",
    "پنالتی",
    "مسابقه",
    "دیدار",
    "رقابت",
    "لیگ",
    "جام",
    "فینال",
    "نیمه نهایی",
    "نیمه‌نهایی",
    "مرحله گروهی",
    "مرحله حذفی",
    "قهرمانی",
    "مدال",
    "المپیک",
    "جهانی",
    "world cup",
    "national team",
    "football club",
    "sports",
    "sport",
}


def _normalize(value: str) -> str:
    """
    نرمال‌سازی ساده برای مقایسه کلیدواژه‌ها.
    """

    return (
        str(value or "")
        .strip()
        .lower()
        .replace("ي", "ی")
        .replace("ك", "ک")
        .replace("\u200c", "‌")
    )


def _own_names(sport_id: str, sport: dict) -> set:
    """
    نام مستقیم رشته.

    مثال:
    football / فوتبال
    basketball / بسکتبال
    """

    names = {
        _normalize(sport.get("name", "")),
        _normalize(sport_id.replace("_", " ")),
    }

    return {
        name
        for name in names
        if name
    }


def _is_generic_sport_keyword(keyword: str) -> bool:
    """
    آیا کلیدواژه بیش از حد عمومی است؟
    """

    normalized = _normalize(keyword)

    return normalized in {
        _normalize(item)
        for item in GENERIC_SPORT_WORDS
    }


def _contains_any(text: str, words) -> bool:
    """
    بررسی وجود حداقل یکی از کلمات.
    """

    for word in words:
        if word and keyword_in_text(word, text):
            return True

    return False


class SportDetector:
    """
    تشخیص رشته ورزشی.

    امتیازدهی:

    - نام مستقیم رشته: 3
    - strong keyword: 3
    - نام تیم/باشگاه/رقابت شاخص: 3
    - keyword معمولی: 1
    - keyword عمومی: 0

    نکته:
    منبع ورزشی به‌تنهایی باعث sport شدن خبر نمی‌شود.
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # ==============================================================
        # اگر یک fetcher معتبر مثل ESPN قبلاً رشته را مشخص کرده،
        # همان تشخیص را حفظ می‌کنیم.
        # ==============================================================

        existing_sport = getattr(news, "sport", None)

        if existing_sport:
            sport_data = SPORTS.get(existing_sport)

            if sport_data:
                news.sport_name = sport_data["name"]
                news.sport_emoji = sport_data["emoji"]
                news.sport_hashtag = sport_data["hashtag"]

            logger.info(
                "Sport: %s (از منبع مشخص شده)",
                getattr(
                    news,
                    "sport_name",
                    existing_sport,
                ),
            )

            return news

        # ==============================================================
        # متن مورد بررسی
        #
        # عنوان + خلاصه کافی است.
        # متن کامل عمداً وارد تشخیص نمی‌شود تا false positive زیاد نشود.
        # ==============================================================

        title = getattr(news, "title", "") or ""
        summary = getattr(news, "summary", "") or ""

        text = f"{title} {summary}".strip()

        if not text:
            self._clear_sport(news)
            return news

        # ==============================================================
        # امتیاز رشته‌ها
        # ==============================================================

        scores = defaultdict(int)

        # ==============================================================
        # تشخیص از روی SPORTS
        # ==============================================================

        for sport_id, sport in SPORTS.items():

            own_names = _own_names(
                sport_id,
                sport,
            )

            strong_keywords = {
                _normalize(keyword)
                for keyword in sport.get(
                    "strong_keywords",
                    [],
                )
                if keyword
            }

            # ----------------------------------------------------------
            # strong keywords
            #
            # این بخش را جداگانه بررسی می‌کنیم تا strong keyword
            # واقعاً امتیاز بالاتری بگیرد.
            # ----------------------------------------------------------

            for keyword in sport.get(
                "strong_keywords",
                [],
            ):

                if not keyword:
                    continue

                normalized = _normalize(keyword)

                if not keyword_in_text(
                    keyword,
                    text,
                ):
                    continue

                # نام خود رشته
                if normalized in own_names:
                    scores[sport_id] += 3

                # strong keyword
                else:
                    scores[sport_id] += 3

            # ----------------------------------------------------------
            # keywords معمولی
            # ----------------------------------------------------------

            for keyword in sport.get(
                "keywords",
                [],
            ):

                if not keyword:
                    continue

                normalized = _normalize(keyword)

                if not keyword_in_text(
                    keyword,
                    text,
                ):
                    continue

                # قبلاً در strong keywords امتیاز گرفته؛
                # دوباره امتیاز سنگین نده.
                if normalized in strong_keywords:
                    continue

                # نام مستقیم رشته
                if normalized in own_names:
                    scores[sport_id] += 3

                # کلمه عمومی
                elif _is_generic_sport_keyword(
                    normalized
                ):
                    continue

                # کلمه معمولی
                else:
                    scores[sport_id] += 1

        # ==============================================================
        # تشخیص hint منبع
        # ==============================================================

        hint_sport = self._hint_sport(news)

        # ==============================================================
        # تشخیص وجود context ورزشی
        #
        # برای منابعی مثل Football360 بسیار مهم است.
        #
        # اگر منبع ورزشی باشد اما متن واقعاً ورزشی نباشد،
        # صرفاً به خاطر منبع sport نمی‌شود.
        # ==============================================================

        has_sport_context = _contains_any(
            text,
            SPORT_CONTEXT_WORDS,
        )

        # ==============================================================
        # اگر hint ورزشی داریم، ولی متن برای آن رشته keyword دارد،
        # امتیاز آن را تقویت می‌کنیم.
        #
        # این کمک می‌کند:
        #
        # Football360 + فوتبال
        # Football360 + جام جهانی
        # Football360 + بارسلونا
        # Football360 + تیم ملی
        #
        # بدون اینکه Football360 + خبر سیاسی
        # خودکار sport شود.
        # ==============================================================

        if hint_sport:

            if scores.get(hint_sport, 0) > 0:

                if has_sport_context:
                    scores[hint_sport] += 1

            elif has_sport_context:

                # فقط یک امتیاز کمکی؛
                # چون منبع به‌تنهایی کافی نیست.
                scores[hint_sport] += 1

        # ==============================================================
        # اگر هیچ رشته‌ای امتیاز نگرفته
        # ==============================================================

        if not scores:

            self._clear_sport(news)

            logger.info(
                "Sport: none | source_hint=%s | title=%s",
                hint_sport,
                title[:80],
            )

            return news

        # ==============================================================
        # مرتب‌سازی رشته‌ها
        #
        # در صورت تساوی:
        # رشته‌ای که keyword تخصصی‌تری دارد بهتر است.
        # ==============================================================

        ranked = sorted(
            scores.items(),
            key=lambda item: (
                item[1],
                self._specificity_score(
                    item[0],
                    text,
                ),
            ),
            reverse=True,
        )

        best_sport, best_score = ranked[0]

        # ==============================================================
        # اگر امتیاز کافی نیست
        # ==============================================================

        if best_score < MIN_SPORT_SCORE:

            # فقط اگر:
            # 1) منبع hint مشخصی دارد
            # 2) متن حداقل یک نشانه ورزشی دارد
            # 3) خود رشته حداقل یک امتیاز دارد
            #
            # آن را قبول می‌کنیم.
            if (
                hint_sport
                and scores.get(hint_sport, 0) > 0
                and has_sport_context
            ):
                best_sport = hint_sport
                best_score = scores[hint_sport]

            else:
                self._clear_sport(news)

                logger.info(
                    "Sport: none | best_score=%s | source_hint=%s | title=%s",
                    best_score,
                    hint_sport,
                    title[:80],
                )

                return news

        # ==============================================================
        # جلوگیری از انتخاب اشتباه رشته در صورت اختلاف کم
        #
        # اگر hint منبع مثلاً football باشد و فوتبال هم امتیاز
        # قابل قبول داشته باشد، در تساوی یا اختلاف بسیار کم،
        # hint منبع می‌تواند کمک کند.
        # ==============================================================

        if (
            hint_sport
            and best_sport != hint_sport
        ):

            hint_score = scores.get(
                hint_sport,
                0,
            )

            if (
                hint_score >= MIN_SPORT_SCORE
                and best_score <= hint_score + 1
            ):
                best_sport = hint_sport
                best_score = hint_score

        # ==============================================================
        # ثبت تشخیص نهایی
        # ==============================================================

        sport_data = SPORTS.get(best_sport)

        if not sport_data:
            self._clear_sport(news)
            return news

        news.sport = best_sport
        news.sport_name = sport_data["name"]
        news.sport_emoji = sport_data["emoji"]
        news.sport_hashtag = sport_data["hashtag"]

        logger.info(
            "Sport: %s | score=%s | source_hint=%s | context=%s | title=%s",
            news.sport_name,
            best_score,
            hint_sport,
            has_sport_context,
            title[:80],
        )

        # ==============================================================
        # تشخیص لیگ / جام
        # ==============================================================

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

    # ==================================================================
    # تشخیص specificity
    # ==================================================================

    @staticmethod
    def _specificity_score(
        sport_id: str,
        text: str,
    ) -> int:

        sport = SPORTS.get(sport_id)

        if not sport:
            return 0

        score = 0

        for keyword in sport.get(
            "strong_keywords",
            [],
        ):

            if keyword and keyword_in_text(
                keyword,
                text,
            ):
                score += 2

        for keyword in sport.get(
            "keywords",
            [],
        ):

            if keyword and keyword_in_text(
                keyword,
                text,
            ):
                if not _is_generic_sport_keyword(keyword):
                    score += 1

        return score

    # ==================================================================
    # hint منبع
    # ==================================================================

    @staticmethod
    def _hint_sport(news):
        """
        رشته‌ای که source_category_hint مشخصاً معرفی می‌کند.

        مثال:

        ["sport", "football"]
            → football

        ["sport", "basketball"]
            → basketball

        نکته:
        hint به‌تنهایی برای ورزشی کردن خبر کافی نیست.
        """

        for hint in getattr(
            news,
            "source_category_hint",
            None,
        ) or []:

            normalized = _normalize(hint)

            if normalized in SPORTS:
                return normalized

        return None

    # ==================================================================
    # پاک کردن تشخیص قبلی
    # ==================================================================

    @staticmethod
    def _clear_sport(news):

        news.sport = None
        news.sport_name = None
        news.sport_emoji = None
        news.sport_hashtag = None
