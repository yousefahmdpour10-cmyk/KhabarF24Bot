import asyncio

from news_fetcher import get_latest_news
from telegram_bot import send_message


async def main():
    news = get_latest_news()

    if not news:
        print("No news found.")
        return

    first_news = news[0]

    message = f"""📰 {first_news['title']}

🔗 {first_news['link']}
"""

    await send_message(message)


asyncio.run(main())
