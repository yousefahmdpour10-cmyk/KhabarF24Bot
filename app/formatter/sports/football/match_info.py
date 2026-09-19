"""
Football Match Info Builder
"""

from app.models.raw_news import RawNews


class MatchInfoBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        date = getattr(
            news,
            "match_date",
            None,
        )

        time = getattr(
            news,
            "match_time",
            None,
        )

        stadium = getattr(
            news,
            "stadium",
            None,
        )

        referee = getattr(
            news,
            "referee",
            None,
        )

        tournament = getattr(
            news,
            "tournament",
            None,
        )

        stage = getattr(
            news,
            "stage",
            None,
        )

        if date:
            lines.append(
                f"📅 {date}"
            )

        if time:
            lines.append(
                f"🕒 {time}"
            )

        if tournament:
            lines.append(
                f"🏆 {tournament}"
            )

        if stage:
            lines.append(
                f"🔹 {stage}"
            )

        if stadium:
            lines.append(
                f"🏟️ {stadium}"
            )

        if referee:
            lines.append(
                f"👨‍⚖️ {referee}"
            )

        return lines
