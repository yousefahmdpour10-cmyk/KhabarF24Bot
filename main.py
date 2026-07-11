import asyncio

from news_fetcher import get_latest_news
from telegram_bot import send_message
from news_db import (
    init_db,
    is_published,
    mark_as_published,
)

from category_detector import detect_category

CHECK_INTERVAL = 300  # هر ۵ دقیقه


async def check_news():

    news = get_latest_news()

    if not news:
        print("No news found.")
        return

    for item in news:

        if is_published(item["link"]):
            continue

        category = detect_category(
            item.get("source", ""),
            item["title"]
        )

        print(f"Category: {category}")

        message = f"""📰 {item['title']}

🔗 {item['link']}
"""

        await send_message(message)

        mark_as_published(item["link"])

        print("✅ New article published.")

        break


async def main():

    init_db()

    print("🚀 KhabarF24 Started")

    while True:

        try:
            await check_news()

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
