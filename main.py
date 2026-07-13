import asyncio

from news_fetcher import get_latest_news
from telegram_bot import send_message
from news_db import (
    init_db,
    is_published,
    mark_as_published,
)

from category_detector import detect_category
from formatter import format_news

CHECK_INTERVAL = 300  # هر ۵ دقیقه


async def check_news():

    news = get_latest_news()

    if not news:
        print("No news found.")
        return

    for item in news:

        link = item.get("link")

        if not link:
            continue

        if is_published(link):
            continue

        # اولویت با دسته‌ای که منبع مشخص کرده
        category = item.get("category")

        # اگر دسته نبود، تشخیص هوشمند
        if not category:
            category = detect_category(
                item.get("source", ""),
                item.get("title", "")
            )

        print(f"Source: {item.get('source')}")
        print(f"Category: {category}")

        message = format_news(
            title=item.get("title", ""),
            summary=item.get("summary", ""),
            source=item.get("source", "")
        )

        await send_message(message)

        mark_as_published(link)

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
