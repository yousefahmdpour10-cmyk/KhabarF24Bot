import asyncio

from news_fetcher import get_latest_news
from telegram_bot import send_message
from database.published_news import (
    is_published,
    mark_as_published,
)


async def main():
    news = get_latest_news()

    if not news:
        print("No news found.")
        return

    for item in news:

        if is_published(item["link"]):
            continue

        message = f"""📰 {item['title']}

🔗 {item['link']}
"""

        await send_message(message)

        mark_as_published(item["link"])

        print("✅ New article published.")

        break


asyncio.run(main())
