"""
Football Interview Builder
"""

from app.models.raw_news import RawNews


class InterviewBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        interview = getattr(news, "interview", None)

        if interview:
            lines.append(f"🎙️ {interview}")

        return lines
