"""
Basketball Formatter
KhabarF24

Formatter سطح بالای بسکتبال.

این فایل نقش رابط بین سیستم اصلی Sports
و موتور اختصاصی بسکتبال را دارد.

جزئیات تخصصی بسکتبال در:
    app/formatter/sports/basketball/
قرار دارند.
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


class BasketballFormatter:
    """
    Formatter اصلی اخبار بسکتبال.

    این کلاس مانند FootballFormatter فقط
    لایه اتصال به موتور تخصصی بسکتبال است.
    """

    def __init__(self):

        self.hashtags = HashtagBuilder()
        self.builder = BasketballBuilder()

    async def format(
        self,
        news: RawNews,
    ) -> str:
        """
        ساخت پست نهایی خبر بسکتبال.
        """

        text = ""

        # ====================================================
        # HASHTAGS
        # ====================================================

        hashtags = self.hashtags.build(news)

        # ====================================================
        # SOURCE FLAG
        # ====================================================

        flag = get_flag(
            news.source
        )

        # ====================================================
        # HEADER
        # ====================================================

        text += "━━━━━━━━━━━━━━━━\n"
        text += "🔴 KhabarF24 | 🏀 بسکتبال\n"
        text += "━━━━━━━━━━━━━━━━\n\n"

        # ====================================================
        # TITLE
        # ====================================================

        text += (
            f"{TITLE} {news.title}\n\n"
        )

        # ====================================================
        # BASKETBALL DETAILS
        # ====================================================

        details = self.build_details(
            news
        )

        if details:

            text += details
            text += "\n\n"

        # ====================================================
        # SOURCE
        # ====================================================

        text += (
            f"{SOURCE} {flag} "
            f"{news.source}\n"
        )

        # ====================================================
        # FOOTER
        # ====================================================

        text += build_footer()

        # ====================================================
        # HASHTAGS
        # ====================================================

        if hashtags:

            text += "\n\n"
            text += hashtags

        return text

    def build_details(
        self,
        news: RawNews,
    ) -> str:
        """
        ساخت بخش تخصصی خبر بسکتبال.

        تمام منطق مربوط به:
            - نتیجه
            - ترکیب
            - بازیکنان
            - تیم‌ها
            - لیگ
            - تورنمنت
            - مصاحبه
            - آمار
            - رویدادهای بسکتبال

        در BasketballBuilder مدیریت می‌شود.
        """

        return self.builder.build(
            news
        )
