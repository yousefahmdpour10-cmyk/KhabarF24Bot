"""
Basketball Formatter
KhabarF24

قالب‌بندی اخبار بسکتبال برای انتشار در تلگرام.

قوانین:
- هدر دسته ورزشی شامل ایموجی + نام «بسکتبال» است.
- عناوین داخل پست با استیکر مفهومی نمایش داده می‌شوند.
- لیگ و تورنمنت جداگانه پشتیبانی می‌شوند.
- ترکیب، نتیجه، سالن، داور، آمار، کوارترها و مصاحبه‌ها
  می‌توانند به‌صورت بخش‌های مستقل وارد پست شوند.
- ساخت هشتگ در انتهای پست انجام می‌شود.
"""

from typing import Optional

from app.models.raw_news import RawNews

from app.formatter.footer import build_footer
from app.formatter.hashtags import HashtagBuilder
from app.formatter.source_flags import get_flag

from app.formatter.icons import (
    TITLE,
    SOURCE,
)


# ============================================================
# BASKETBALL STICKERS
# ============================================================

# نکته:
# شناسه واقعی استیکرها بعداً از سیستم Sticker/Asset پروژه
# خوانده می‌شود.
#
# فعلاً نام کلیدها استاندارد شده تا هیچ متن اضافی مثل
# «داوران:» یا «ترکیب:» وارد پست نشود.

STICKERS = {
    "sport": "🏀",
    "league": "🏆",
    "tournament": "🏆",
    "match": "🏀",
    "result": "🏁",
    "lineup": "👥",
    "players": "🏀",
    "coach": "👔",
    "captain": "©️",
    "referee": "👨‍⚖️",
    "arena": "🏟️",
    "time": "⏰",
    "stats": "📊",
    "quarters": "⏱️",
    "points": "🎯",
    "assists": "🅰️",
    "rebounds": "🔄",
    "fouls": "🚫",
    "interview": "🎙️",
    "transfer": "🔄",
}


class BasketballFormatter:
    """
    Formatter اصلی اخبار بسکتبال.
    """

    SPORT_NAME = "بسکتبال"
    SPORT_ICON = STICKERS["sport"]

    def __init__(self):
        self.hashtags = HashtagBuilder()

    async def format(
        self,
        news: RawNews,
    ) -> str:
        """
        ساخت پست نهایی بسکتبال.
        """

        text = ""

        flag = get_flag(news.source)

        # ----------------------------------------------------
        # HASHTAGS
        # ----------------------------------------------------

        hashtags = self.hashtags.build(news)

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        text += "━━━━━━━━━━━━━━━━\n"
        text += (
            f"🔴 KhabarF24 | "
            f"{self.SPORT_ICON} {self.SPORT_NAME}\n"
        )
        text += "━━━━━━━━━━━━━━━━\n\n"

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        if news.title:
            text += f"{TITLE} {news.title}\n\n"

        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        details = self.build_details(news)

        if details:
            text += details
            text += "\n"

        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        text += (
            f"{SOURCE} {flag} {news.source}\n"
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        text += build_footer()

        # ----------------------------------------------------
        # HASHTAGS
        # ----------------------------------------------------

        if hashtags:
            text += "\n\n"
            text += hashtags

        return text

    def build_details(
        self,
        news: RawNews,
    ) -> str:
        """
        ساخت بخش جزئیات خبر.

        این متد عمداً مستقل نگه داشته شده تا Builder بسکتبال
        بتواند بعداً اطلاعات مسابقه را بدون تغییر Formatter
        اصلی تولید کند.
        """

        details = []

        data = news.raw_data or {}

        # ----------------------------------------------------
        # LEAGUE
        # ----------------------------------------------------

        league = data.get("league")

        if league:
            details.append(
                f"{STICKERS['league']} {league}"
            )

        # ----------------------------------------------------
        # TOURNAMENT
        # ----------------------------------------------------

        tournament = data.get("tournament")

        if tournament:
            details.append(
                f"{STICKERS['tournament']} {tournament}"
            )

        # ----------------------------------------------------
        # MATCH
        # ----------------------------------------------------

        home_team = data.get("home_team")
        away_team = data.get("away_team")

        if home_team and away_team:
            details.append(
                f"{STICKERS['match']} "
                f"{home_team} 🆚 {away_team}"
            )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        result = data.get("result")

        if result:
            details.append(
                f"{STICKERS['result']} {result}"
            )

        # ----------------------------------------------------
        # ARENA
        # ----------------------------------------------------

        arena = data.get("arena")

        if arena:
            details.append(
                f"{STICKERS['arena']} {arena}"
            )

        # ----------------------------------------------------
        # DATE / TIME
        # ----------------------------------------------------

        match_time = data.get("match_time")

        if match_time:
            details.append(
                f"{STICKERS['time']} {match_time}"
            )

        # ----------------------------------------------------
        # REFEREE
        # ----------------------------------------------------

        referees = data.get("referees")

        if referees:
            if isinstance(referees, list):
                referee_text = "، ".join(
                    str(item)
                    for item in referees
                )
            else:
                referee_text = str(referees)

            details.append(
                f"{STICKERS['referee']} "
                f"{referee_text}"
            )

        # ----------------------------------------------------
        # LINEUP
        # ----------------------------------------------------

        lineup = data.get("lineup")

        if lineup:
            details.append(
                f"{STICKERS['lineup']}\n"
                f"{lineup}"
            )

        # ----------------------------------------------------
        # QUARTERS
        # ----------------------------------------------------

        quarters = data.get("quarters")

        if quarters:
            details.append(
                f"{STICKERS['quarters']}\n"
                f"{quarters}"
            )

        # ----------------------------------------------------
        # STATS
        # ----------------------------------------------------

        stats = data.get("stats")

        if stats:
            details.append(
                f"{STICKERS['stats']}\n"
                f"{stats}"
            )

        # ----------------------------------------------------
        # POINTS
        # ----------------------------------------------------

        points = data.get("points")

        if points:
            details.append(
                f"{STICKERS['points']} {points}"
            )

        # ----------------------------------------------------
        # ASSISTS
        # ----------------------------------------------------

        assists = data.get("assists")

        if assists:
            details.append(
                f"{STICKERS['assists']} {assists}"
            )

        # ----------------------------------------------------
        # REBOUNDS
        # ----------------------------------------------------

        rebounds = data.get("rebounds")

        if rebounds:
            details.append(
                f"{STICKERS['rebounds']} {rebounds}"
            )

        # ----------------------------------------------------
        # FOULS
        # ----------------------------------------------------

        fouls = data.get("fouls")

        if fouls:
            details.append(
                f"{STICKERS['fouls']} {fouls}"
            )

        # ----------------------------------------------------
        # COACH
        # ----------------------------------------------------

        coach = data.get("coach")

        if coach:
            details.append(
                f"{STICKERS['coach']} {coach}"
            )

        # ----------------------------------------------------
        # CAPTAIN
        # ----------------------------------------------------

        captain = data.get("captain")

        if captain:
            details.append(
                f"{STICKERS['captain']} {captain}"
            )

        # ----------------------------------------------------
        # INTERVIEW
        # ----------------------------------------------------

        pre_match_interview = data.get(
            "pre_match_interview"
        )

        if pre_match_interview:
            details.append(
                f"{STICKERS['interview']}\n"
                f"{pre_match_interview}"
            )

        post_match_interview = data.get(
            "post_match_interview"
        )

        if post_match_interview:
            details.append(
                f"{STICKERS['interview']}\n"
                f"{post_match_interview}"
            )

        # ----------------------------------------------------
        # TRANSFER
        # ----------------------------------------------------

        transfer = data.get("transfer")

        if transfer:
            details.append(
                f"{STICKERS['transfer']} {transfer}"
            )

        return "\n\n".join(details)
