"""
KhabarF24 Weather Template
قالب اختصاصی اخبار هواشناسی
"""

from app.models.raw_news import RawNews


class WeatherTemplate:

    async def format(
        self,
        news: RawNews,
    ) -> str:

        title = (
            getattr(news, "title", "")
            or ""
        ).strip()

        summary = (
            getattr(news, "summary", "")
            or ""
        ).strip()

        source = (
            getattr(news, "source", "")
            or ""
        ).strip()

        source_country = (
            getattr(news, "country", "")
            or ""
        ).strip().upper()

        # ---------------------------------------------
        # Country flag
        # ---------------------------------------------

        flags = {
            "IR": "🇮🇷",
            "US": "🇺🇸",
            "GB": "🇬🇧",
            "FR": "🇫🇷",
            "DE": "🇩🇪",
            "IT": "🇮🇹",
            "ES": "🇪🇸",
            "TR": "🇹🇷",
            "QA": "🇶🇦",
            "AE": "🇦🇪",
            "SA": "🇸🇦",
        }

        flag = flags.get(
            source_country,
            "",
        )

        # ---------------------------------------------
        # Source
        # ---------------------------------------------

        source_line = source

        if flag:
            source_line = f"{flag} {source}"

        # ---------------------------------------------
        # Build post
        # ---------------------------------------------

        parts = [
            "━━━━━━━━━━━━━━━━",
            "🔴 KhabarF24 | 🌤️ هواشناسی",
            "━━━━━━━━━━━━━━━━",
            "",
        ]

        if title:
            parts.extend([
                f"📰 {title}",
                "",
            ])

        if summary:
            parts.extend([
                f"✍️ {summary}",
                "",
            ])

        if source_line:
            parts.extend([
                f"🗞️ {source_line}",
            ])

        parts.extend([
            "━━━━━━━━━━━━━━━━",
            "📢 @KhabarF24",
            "",
            "#هواشناسی",
        ])

        return "\n".join(parts)
