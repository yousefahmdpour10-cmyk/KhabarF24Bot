"""
Football Hashtags Builder
"""

from app.models.raw_news import RawNews


class FootballHashtagsBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        hashtags = getattr(news, "hashtags", [])

        return hashtags
