import asyncio

from news_fetcher import get_latest_news
from telegram_bot import send_message

from news_db import (
    init_db,
    is_published,
    mark_as_published,
)

from category_engine import detect_smart_category
from formatter import format_news
from ai_processor import process_news


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



        # =========================
        # 🧠 تشخیص هوشمند دسته خبر
        # =========================

        category = detect_smart_category(
            title=item.get("title", ""),
            summary=item.get("summary", ""),
            source=item.get("source", "")
        )


        print(f"Source: {item.get('source')}")
        print(f"Smart Category: {category}")



        # =========================
        # 🤖 پردازش فارسی خبر
        # =========================

        processed = process_news(
            item.get("title", ""),
            item.get("summary", "")
        )



        title = processed.get(
            "title",
            item.get("title", "")
        )


        summary = processed.get(
            "summary",
            item.get("summary", "")
        )



        # =========================
        # 📰 ساخت پست نهایی
        # =========================

        message = format_news(
            title=title,
            summary=summary,
            source=item.get("source", ""),
            category=category
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
