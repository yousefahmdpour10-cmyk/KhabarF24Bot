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


def _own_names(sport_id: str, sport: dict) -> set:
    """اسم خود رشته (فارسی و انگلیسی)؛ مثلاً «والیبال» و "volleyball"."""

    names = {
        str(sport.get("name", "")).lower(),
        sport_id.replace("_", " ").lower(),
    }

    return {name for name in names if name}


class SportDetector:
    """
    تشخیص رشته ورزشی

    هر کلیدواژه‌ی عادی ۱ امتیاز دارد، ولی خودِ اسم رشته (مثل «والیبال»)
    ۲ امتیاز. قبلاً اگر دو رشته امتیاز برابر می‌گرفتند، اولین رشته‌ی
    فهرست (فوتبال) برنده می‌شد؛ برای همین «لیگ برتر والیبال» فوتبال
    تشخیص داده می‌شد.
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        # اگر fetcher مطمئنی (مثل ESPN) رشته را از قبل مشخص کرده، آن را
        # با حدسِ کلیدواژه‌ای خراب نمی‌کنیم.
        if getattr(news, "sport", None):
            logger.info(
                f"Sport: {getattr(news, 'sport_name', news.sport)} (از منبع مشخص شده)"
            )
            return news

        text = f"{news.title} {news.summary}"

        scores = defaultdict(int)

        for sport_id, sport in SPORTS.items():

            own = _own_names(sport_id, sport)

            for keyword in sport["keywords"]:

                if keyword_in_text(keyword, text):

                    scores[sport_id] += 2 if keyword.lower() in own else 1

        hint_sport = self._hint_sport(news)

        if scores:

            best = max(
                scores,
                key=scores.get,
            )

            # شواهد ضعیف (فقط یک کلیدواژه‌ی عادی، مثل اسم یک بازیکن) در
            # برابر منبعی که مشخصاً درباره‌ی یک رشته است: منبع را قبول کن
            # (مثلاً خبر رئال مادرید که «نادال» دارد، «تنیس» نشود).
            if hint_sport and best != hint_sport and scores[best] <= 1:
                best = hint_sport

            news.sport = best

            news.sport_name = SPORTS[best]["name"]

            news.sport_emoji = SPORTS[best]["emoji"]

            news.sport_hashtag = SPORTS[best]["hashtag"]

            logger.info(
                f"Sport: {news.sport_name}"
            )

            # مسابقه (لیگ یا جام) برای هشتگ دوم پست
            if not getattr(news, "league", None):
                league = detect_league(text)

                if league:
                    news.league = league
                    logger.info(f"League: {league}")

        elif hint_sport:

            # هیچ کلیدواژه‌ای پیدا نشد ولی منبع مشخصاً فوتبالی (یا ...) است
            news.sport = hint_sport
            news.sport_name = SPORTS[hint_sport]["name"]
            news.sport_emoji = SPORTS[hint_sport]["emoji"]
            news.sport_hashtag = SPORTS[hint_sport]["hashtag"]

            logger.info(f"Sport: {news.sport_name} (از دسته‌ی منبع)")

            if not getattr(news, "league", None):
                league = detect_league(text)

                if league:
                    news.league = league

        else:

            news.sport = None

            news.sport_name = None

            news.sport_emoji = None

            news.sport_hashtag = None

        return news

    @staticmethod
    def _hint_sport(news):
        """
        رشته‌ای که دسته‌های منبع مشخصاً نام می‌برند (مثلاً ["sport",
        "football", "transfer"] ← football). منابع فارسی را کنار
        می‌گذاریم، چون خبرگزاری‌ها و سایت‌های فارسی چندرشته‌ای‌اند.
        """

        if str(getattr(news, "language", "") or "").lower() == "fa":
            return None

        for hint in getattr(news, "source_category_hint", None) or []:
            if hint in SPORTS:
                return hint

        return None
