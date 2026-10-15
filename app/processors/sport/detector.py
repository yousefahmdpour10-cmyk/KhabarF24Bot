"""
Sport Detector

تشخیص رشته ورزشی با امتیازدهی به کلیدواژه‌ها
و استفاده از دسته‌بندی منبع به‌عنوان سرنخ.
"""

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


class SportDetector:

    async def process(self, news: RawNews) -> RawNews:
        existing_sport = getattr(news, "sport", None)

        if existing_sport and existing_sport in SPORTS:
            selected = SPORTS[existing_sport]
            news.sport_name = (
                getattr(news, "sport_name", None)
                or selected.get("name")
            )
            news.sport_emoji = (
                getattr(news, "sport_emoji", None)
                or selected.get("emoji")
            )
            news.sport_hashtag = (
                getattr(news, "sport_hashtag", None)
                or selected.get("hashtag")
            )
            logger.info(
                "Sport: %s (از قبل مشخص شده)",
                news.sport_name,
            )
            return news

        title = getattr(news, "title", "") or ""
        summary = getattr(news, "summary", "") or ""
        content = getattr(news, "content", "") or ""

        title_summary = f"{title} {summary}"
        full_text = f"{title_summary} {content}"

        scores = defaultdict(int)
        matched_keywords = defaultdict(list)

        # تشخیص رشته با استفاده از کلیدواژه‌ها
        for sport_id, sport_data in SPORTS.items():
            keywords = sport_data.get("keywords", [])

            for keyword in keywords:
                if not keyword:
                    continue

                in_title = keyword_in_text(
                    keyword, title_summary
                )
                in_content = (
                    in_title
                    or keyword_in_text(keyword, full_text)
                )

                if not in_content:
                    continue

                normalized = keyword.strip().lower()

                weight = (
                    1 if normalized in WEAK_KEYWORDS else 2
                )

                if in_title:
                    weight += 1

                scores[sport_id] += weight
                matched_keywords[sport_id].append(keyword)

        # استفاده از دسته‌بندی منبع به‌عنوان سرنخ تکمیلی
        source_hints = getattr(
            news, "source_category_hint", []
        ) or []

        source_hints = {
            str(hint).strip().lower()
            for hint in source_hints
            if hint
        }

        source_id = str(
            getattr(news, "source_id", "") or ""
        ).strip().lower()

        football_hints = {
            "football",
            "soccer",
            "premier_league",
            "champions_league",
            "europa_league",
        }

        # فقط برچسب‌های صریح فوتبال امتیاز می‌گیرند؛
        # برچسب عمومی sport برای تعیین فوتبال کافی نیست.
        if (
            source_hints & football_hints
            or source_id in {
                "bbc_football",
                "espn_soccer",
            }
        ):
            scores["football"] += 2
            matched_keywords["football"].append(
                "source_category_hint"
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
        second_score = (
            ranked[1][1] if len(ranked) > 1 else 0
        )

        if best_sport not in SPORTS:
            self._clear_sport(news)
            return news

        if best_score < MIN_SPORT_SCORE:
            self._clear_sport(news)
            return news

        # اگر دو رشته امتیاز برابر داشته باشند،
        # از انتخاب تصادفی رشته جلوگیری می‌کنیم.
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
        news.sport = None
        news.sport_name = None
        news.sport_emoji = None
        news.sport_hashtag = None
