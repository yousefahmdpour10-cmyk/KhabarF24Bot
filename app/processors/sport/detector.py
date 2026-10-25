"""
Sport Detector

تشخیص رشته ورزشی با امتیازدهی به کلیدواژه‌ها،
برچسب منبع و الگوهای نتیجه مسابقات.
"""

import re
from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.sport.keywords import SPORTS
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text


WEAK_KEYWORDS = {
    "sport", "sports", "manager", "coach", "head coach",
    "transfer", "transfer news", "transfer window", "signing",
    "fixtures", "championship", "tournament", "league", "match",
    "club", "captain", "season", "win", "winner", "final",
    "finals", "draw", "goal", "goals", "player", "players",
    "athlete", "athletes",
}

MIN_SPORT_SCORE = 2

FOOTBALL_HINTS = {
    "football",
    "soccer",
    "premier_league",
    "champions_league",
    "europa_league",
}

FOOTBALL_SOURCE_IDS = {
    "bbc_football",
    "espn_soccer",
}

# نام تیم‌های شناخته‌شده برای تشخیص نتیجه مسابقات فوتبال فارسی
PERSIAN_FOOTBALL_TEAMS = (
    "استقلال",
    "پرسپولیس",
    "سپاهان",
    "تراکتور",
    "ذوب آهن",
    "ذوب‌آهن",
    "فولاد",
    "گل گهر",
    "گل‌گهر",
    "ملوان",
    "پیکان",
    "شمس آذر",
    "شمس‌آذر",
    "استقلال خوزستان",
    "مس رفسنجان",
    "مس شهر بابک",
    "خیبر خرم آباد",
    "خیبر خرم‌آباد",
    "چادرملو",
    "آلومینیوم اراک",
    "نساجی",
    "هوادار",
    "بایرن مونیخ",
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
    "اتلتیکو مادرید",
    "یوونتوس",
    "اینتر",
    "میلان",
    "پاری سن ژرمن",
    "پاری‌سن‌ژرمن",
    "دورتموند",
    "ناپولی",
)

# اعداد فارسی، عربی و لاتین در نتیجه مسابقات
DIGITS = "0-9۰-۹٠-٩"

SCORE_PATTERN = re.compile(
    rf"[{DIGITS}]+\s*[-–—:]\s*[{DIGITS}]+"
)


class SportDetector:
    """تشخیص رشته ورزشی و ثبت اطلاعات رشته."""

    async def process(self, news: RawNews) -> RawNews:
        existing_sport = getattr(news, "sport", None)

        if existing_sport and existing_sport in SPORTS:
            self._set_sport(news, existing_sport)

            logger.info(
                "Sport: %s (از قبل مشخص شده)",
                news.sport_name or existing_sport,
            )
            return news

        title = getattr(news, "title", "") or ""
        summary = getattr(news, "summary", "") or ""
        content = getattr(news, "content", "") or ""

        title_summary = f"{title} {summary}".strip()
        full_text = f"{title_summary} {content}".strip()

        scores = defaultdict(int)
        matched_keywords = defaultdict(list)

        # تشخیص رشته با استفاده از کلیدواژه‌ها
        for sport_id, sport_data in SPORTS.items():
            for keyword in sport_data.get("keywords", []):
                if not keyword:
                    continue

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

                normalized = keyword.strip().lower()
                weight = (
                    1 if normalized in WEAK_KEYWORDS else 2
                )

                if in_title_summary:
                    weight += 1

                scores[sport_id] += weight
                matched_keywords[sport_id].append(keyword)

        # سرنخ‌های دسته‌بندی منبع
        source_hints = (
            getattr(news, "source_category_hint", None) or []
        )

        source_hints = {
            str(hint).strip().lower()
            for hint in source_hints
            if hint
        }

        source_id = str(
            getattr(news, "source_id", "") or ""
        ).strip().lower()

        # منبعی که صریحاً فوتبال را مشخص کرده است.
        if (
            source_hints & FOOTBALL_HINTS
            or source_id in FOOTBALL_SOURCE_IDS
        ):
            scores["football"] += 3
            matched_keywords["football"].append(
                "football_source_hint"
            )

        # تشخیص نتیجه فوتبال فارسی:
        # وجود نتیجه به‌تنهایی کافی نیست؛ باید نام تیم فوتبال
        # یا نشانه معتبر فوتبال نیز در عنوان وجود داشته باشد.
        title_has_score = bool(SCORE_PATTERN.search(title))

        title_lower = title.lower()
        title_has_football_team = any(
            team.lower() in title_lower
            for team in PERSIAN_FOOTBALL_TEAMS
        )

        title_has_football_word = any(
            keyword_in_text(
                keyword,
                title,
            )
            for keyword in (
                "فوتبال",
                "football",
                "soccer",
                "گلزنی",
                "گلزنان",
                "گل زد",
                "گل به ثمر رساند",
            )
        )

        source_is_sports = bool(
            source_hints & {"sport", "sports"}
        )

        if title_has_score and (
            title_has_football_team
            or title_has_football_word
            or source_is_sports
        ):
            scores["football"] += 3
            matched_keywords["football"].append(
                "football_match_result"
            )

        # نام تیم در عنوان، حتی اگر شکل نوشتاری نتیجه متفاوت باشد.
        # برای جلوگیری از تشخیص اشتباه، این امتیاز فقط وقتی اضافه
        # می‌شود که عنوان نشانه فوتبالی یا نتیجه مسابقه داشته باشد.
        if title_has_football_team and (
            title_has_score or title_has_football_word
        ):
            scores["football"] += 2
            matched_keywords["football"].append(
                "football_team_in_title"
            )

        if not scores:
            self._clear_sport(news)
            return news

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        best_sport, best_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0

        if best_sport not in SPORTS:
            self._clear_sport(news)
            return news

        if best_score < MIN_SPORT_SCORE:
            self._clear_sport(news)
            return news

        # در صورت برابر بودن امتیازها، رشته را حدس نمی‌زنیم.
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

        self._set_sport(news, best_sport)

        logger.info(
            "Sport: %s | score=%s | keywords=%s",
            news.sport_name or best_sport,
            best_score,
            matched_keywords[best_sport][:8],
        )

        return news

    @staticmethod
    def _set_sport(news: RawNews, sport_id: str) -> None:
        """ثبت رشته و اطلاعات نمایشی آن."""

        selected = SPORTS[sport_id]

        news.sport = sport_id
        news.sport_name = selected.get("name")
        news.sport_emoji = selected.get("emoji")
        news.sport_hashtag = selected.get("hashtag")

    @staticmethod
    def _clear_sport(news: RawNews) -> None:
        """پاک‌کردن تشخیص رشته نامعتبر یا نامشخص."""

        news.sport = None
        news.sport_name = None
        news.sport_emoji = None
        news.sport_hashtag = None
