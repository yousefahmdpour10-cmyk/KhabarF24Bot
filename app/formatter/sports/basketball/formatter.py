"""
Basketball Formatter
KhabarF24

قالب‌بندی اخبار بسکتبال برای انتشار در تلگرام.

وظیفه این فایل فقط ساخت خروجی نهایی پست است.
استخراج و آماده‌سازی اطلاعات اختصاصی بسکتبال
بر عهده BasketballBuilder است.
"""

from app.models.raw_news import RawNews

from app.formatter.footer import build_footer
from app.formatter.hashtags import HashtagBuilder
from app.formatter.source_flags import get_flag

from app.formatter.sports.basketball.builder import BasketballBuilder

from app.formatter.icons import (
    TITLE,
    SOURCE,
)


# ============================================================
# BASKETBALL STICKERS
# ============================================================

STICKERS = {
    "sport": "🏀",
}


class BasketballFormatter:
    """
    Formatter اصلی اخبار بسکتبال.
    """

    SPORT_NAME = "بسکتبال"
    SPORT_ICON = STICKERS["sport"]

    def __init__(self):

        self.hashtags = HashtagBuilder()
        self.builder = BasketballBuilder()

    # ========================================================
    # FORMAT
    # ========================================================

    async def format(
        self,
        news: RawNews,
    ) -> str:
        """
        ساخت پست نهایی بسکتبال.
        """

        text = ""

        # ----------------------------------------------------
        # FLAG
        # ----------------------------------------------------

        flag = get_flag(
            news.source
        )

        # ----------------------------------------------------
        # HASHTAGS
        # ----------------------------------------------------

        hashtags = self.hashtags.build(
            news
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        text += "━━━━━━━━━━━━━━━━\n"

        text += (
            f"🔴 KhabarF24 | "
            f"{self.SPORT_ICON} "
            f"{self.SPORT_NAME}\n"
        )

        text += "━━━━━━━━━━━━━━━━\n\n"

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        if news.title:

            text += (
                f"{TITLE} "
                f"{news.title}\n\n"
            )

        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        details = self.build_details(
            news
        )

        if details:

            text += details
            text += "\n\n"

        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        text += (
            f"{SOURCE} "
            f"{flag} "
            f"{news.source}\n"
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

    # ========================================================
    # DETAILS
    # ========================================================

    def build_details(
        self,
        news: RawNews,
    ) -> str:
        """
        دریافت اطلاعات آماده‌شده از BasketballBuilder.

        Formatter هیچ اطلاعات ورزشی را خودش استخراج نمی‌کند.
        """

        return self.builder.build(
            news
        )
