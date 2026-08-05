"""
World News Template - Final Design
"""

from app.models.raw_news import RawNews
from app.formatter.templates.base import BaseTemplate
from app.formatter.source_flags import get_flag
from app.formatter.hashtags import HashtagBuilder


class WorldTemplate(BaseTemplate):

    def __init__(self):
        self.hashtags = HashtagBuilder()

    async def format(self, news: RawNews) -> str:
        flag = get_flag(news.source)
        hashtags = self.hashtags.build(news)

        # دسته‌بندی
        category_name = "جهان"
        category_emoji = "🌍"

        text = f"""━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {category_emoji} {category_name}
━━━━━━━━━━━━━━━━

📰 **{news.title}**

✍️ {news.summary or ""}

• 🗞️ {flag} {news.source}
━━━━━━━━━━━━━━━━
📢 @KhabarF24
"""
        if hashtags:
            text += f"\n{hashtags}"

        return text.strip()
