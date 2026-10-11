"""
Sport Detector

تشخیص رشته ورزشی با امتیازدهی به کلیدواژه‌ها
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.sport.keywords import SPORTS
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


# کلیدواژه‌های عمومی و مبهم که به‌تنهایی
# برای تشخیص رشته ورزشی کافی نیستند.
WEAK_KEYWORDS = {
    "sport",
    "sports",
    "manager",
    "coach",
    "head coach",
    "transfer",
    "transfer news",
    "transfer window",
    "signing",
    "fixtures",
    "championship",
    "tournament",
    "league",
    "match",
    "club",
    "captain",
    "season",
    "win",
    "winner",
    "final",
    "finals",
    "draw",
    "goal",
    "goals",
    "player",
    "players",
    "athlete",
    "athletes",
}


# آستانه امتیاز برای تشخیص رشته
MIN_SPORT_SCORE = 2


class SportDetector:
    """
    تشخیص رشته ورزشی خبر.

    نکته:
    - رشته‌ای که از قبل توسط منبع معتبر مشخص شده حفظ می‌شود.
    - کلمات عمومی به‌تنهایی باعث تشخیص رشته نمی‌شوند.
    - نام رشته‌ها و نشانه‌های تخصصی امتیاز بیشتری می‌گیرند.
    - اگر رشته مشخص نشود، sport برابر None باقی می‌ماند.
      دسته اصلی خبر می‌تواند جداگانه در CategoryDetector تعیین شود.
    """

    async def process(self, news: RawNews) -> RawNews:

        # اگر رشته قبلاً توسط یک منبع معتبر تعیین شده،
        # آن را بازنویسی نمی‌کنیم.
        if getattr(news, "sport", None):
            logger.info(
                "Sport: %s (از قبل مشخص شده)",
                getattr(news, "sport_name", None)
                or news.sport,
            )
            return news

        title = getattr(news, "title", "") or ""
        summary = getattr(news, "summary", "") or ""
        content = getattr(news, "content", "") or ""

        # عنوان و خلاصه وزن بیشتری در تصمیم دارند.
        title_summary = f"{title} {summary}"
        full_text = f"{title_summary} {content}"

        scores = defaultdict(int)
        matched_keywords = defaultdict(list)

        for sport_id, sport_data in SPORTS.items():
            keywords = sport_data.get("keywords", [])

            for keyword in keywords:
                if not keyword:
                    continue

                # ابتدا عنوان و خلاصه بررسی می‌شوند.
                in_title_summary = keyword_in_text(
                    keyword,
                    title_summary,
                )

                in_full_text = (
                    in_title_summary
                    or keyword_in_text(keyword, full_text)
                )

                if not in_full_text:
                    continue

                normalized_keyword = keyword.strip().lower()

                # کلمات عمومی امتیاز کمی دارند.
                if normalized_keyword in WEAK_KEYWORDS:
                    weight = 1

                # نام صریح رشته یا اصطلاح تخصصی ورزشی
                # معمولاً از یک کلمه عمومی قابل‌اعتمادتر است.
                else:
                    weight = 2

                # تطبیق در عنوان یا خلاصه مهم‌تر است.
                if in_title_summary:
                    weight += 1

                scores[sport_id] += weight
                matched_keywords[sport_id].append(keyword)

        if not scores:
            self._clear_sport(news)
            return news

        # مرتب‌سازی بر اساس امتیاز؛ در صورت مساوی بودن،
        # نتیجه را بدون اختلاف معنادار قطعی اعلام نمی‌کنیم.
        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        best_sport, best_score = ranked[0]

        second_score = (
            ranked[1][1]
            if len(ranked) > 1
            else 0
        )

        # یک واژه عمومی یا یک تطبیق ضعیف کافی نیست.
        if best_score < MIN_SPORT_SCORE:
            self._clear_sport(news)
            return news

        # اگر چند رشته امتیاز یکسان گرفته‌اند،
        # رشته را حدس نمی‌زنیم.
        if second_score == best_score:
            logger.info(
                "Sport: نامشخص (امتیاز برابر بین رشته‌ها: %s)",
                {
                    sport_id: score
                    for sport_id, score in ranked
                    if score == best_score
                },
            )
            self._clear_sport(news)
            return news

        selected = SPORTS[best_sport]

        news.sport = best_sport
        news.sport_name = selected.get("name")
        news.sport_emoji = selected.get("emoji")
        news.sport_hashtag = selected.get("hashtag")

        logger.info(
            "Sport: %s | score=%s | keywords=%s",
            news.sport_name or best_sport,
            best_score,
            matched_keywords[best_sport][:8],
        )

        return news

    @staticmethod
    def _clear_sport(news: RawNews) -> None:
        """
        پاک‌کردن نتیجه رشته وقتی شواهد کافی نیست.
        دسته اصلی خبر در CategoryDetector تعیین می‌شود.
        """
        news.sport = None
        news.sport_name = None
        news.sport_emoji = None
        news.sport_hashtag = None
