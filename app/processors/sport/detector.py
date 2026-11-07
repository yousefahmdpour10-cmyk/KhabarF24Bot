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


# حداقل امتیاز لازم برای تشخیص یک رشته ورزشی.
# یک کلیدواژه ضعیف به‌تنهایی نباید خبر را ورزشی کند.
MIN_SPORT_SCORE = 2


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


class SportDetector:
    """
    تشخیص رشته ورزشی.

    امتیازدهی:
    - نام مستقیم رشته: 3 امتیاز
    - کلیدواژه تخصصی/قوی: 2 امتیاز
    - کلیدواژه عمومی‌تر: 1 امتیاز

    برای جلوگیری از تشخیص اشتباه، امتیاز نهایی باید حداقل
    MIN_SPORT_SCORE باشد.
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # اگر fetcher مطمئنی (مثل ESPN) رشته را از قبل مشخص کرده،
        # آن را با حدس کلیدواژه‌ای خراب نمی‌کنیم.
        if getattr(news, "sport", None):
            logger.info(
                "Sport: %s (از منبع مشخص شده)",
                getattr(news, "sport_name", news.sport),
            )
            return news

        title = getattr(news, "title", "") or ""
        summary = getattr(news, "summary", "") or ""

        # عنوان و خلاصه برای تشخیص رشته کافی هستند و نباید متن کامل
        # باعث ورود کلیدواژه‌های تصادفی و بی‌ربط شود.
        text = f"{title} {summary}".strip()

        scores = defaultdict(int)

        for sport_id, sport in SPORTS.items():

            own_names = _own_names(sport_id, sport)

            # کلیدواژه‌های قوی‌تر هر رشته.
            strong_keywords = set(
                str(keyword).strip().lower()
                for keyword in sport.get("strong_keywords", [])
                if keyword
            )

            for keyword in sport.get("keywords", []):

                if not keyword:
                    continue

                keyword_normalized = str(keyword).strip().lower()

                if not keyword_in_text(keyword, text):
                    continue

                # نام مستقیم رشته:
                # فوتبال / football / بسکتبال / basketball ...
                if keyword_normalized in own_names:
                    scores[sport_id] += 3

                # نشانه تخصصی رشته:
                # MLB / pitcher / NBA / Wimbledon / UFC ...
                elif keyword_normalized in strong_keywords:
                    scores[sport_id] += 2

                # سایر کلیدواژه‌ها
                else:
                    scores[sport_id] += 1

        hint_sport = self._hint_sport(news)

        if scores:

            best = max(
                scores,
                key=scores.get,
            )

            best_score = scores[best]

            # اگر شواهد کافی برای هیچ رشته‌ای وجود ندارد،
            # صرفاً به خاطر یک کلمه عمومی نباید ورزش تشخیص داده شود.
            if best_score < MIN_SPORT_SCORE:

                # فقط در صورتی از hint منبع استفاده می‌کنیم که
                # منبع واقعاً تک‌رشته‌ای باشد.
                if hint_sport:
                    best = hint_sport
                    best_score = MIN_SPORT_SCORE
                else:
                    best = None

            # اگر منبع مشخصاً متعلق به یک رشته است و شواهد متنی
            # برای رشته دیگری بسیار ضعیف است، hint منبع اولویت دارد.
            elif hint_sport and best != hint_sport and best_score <= 2:

                hint_score = scores.get(hint_sport, 0)

                if hint_score >= 2 or best_score <= 1:
                    best = hint_sport

            if best:

                news.sport = best
                news.sport_name = SPORTS[best]["name"]
                news.sport_emoji = SPORTS[best]["emoji"]
                news.sport_hashtag = SPORTS[best]["hashtag"]

                logger.info(
                    "Sport: %s | score=%s | source_hint=%s",
                    news.sport_name,
                    scores.get(best, best_score),
                    hint_sport,
                )

                # مسابقه / لیگ / جام برای هشتگ دوم پست
                if not getattr(news, "league", None):

                    league = detect_league(text)

                    if league:
                        news.league = league

                        logger.info(
                            "League: %s",
                            league,
                        )

                return news

        elif hint_sport:

            # هیچ کلیدواژه‌ای پیدا نشده ولی منبع مشخصاً
            # درباره یک رشته خاص است.
            news.sport = hint_sport
            news.sport_name = SPORTS[hint_sport]["name"]
            news.sport_emoji = SPORTS[hint_sport]["emoji"]
            news.sport_hashtag = SPORTS[hint_sport]["hashtag"]

            logger.info(
                "Sport: %s (از دسته‌ی منبع)",
                news.sport_name,
            )

            if not getattr(news, "league", None):

                league = detect_league(text)

                if league:
                    news.league = league

            return news

        # هیچ تشخیص معتبر ورزشی وجود ندارد.
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

        منابع فارسی را عمداً کنار می‌گذاریم، چون بسیاری از
        خبرگزاری‌های فارسی چندرشته‌ای هستند.
        """

        if str(getattr(news, "language", "") or "").lower() == "fa":
            return None

        for hint in getattr(news, "source_category_hint", None) or []:

            normalized = str(hint).strip().lower()

            if normalized in SPORTS:
                return normalized

        return None
