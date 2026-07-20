"""
KhabarF24 Main Engine v7.1
Fully coordinated with ai_processor + formatter + telegram_bot
"""

import asyncio
import random

from news_fetcher import get_latest_news
from telegram_bot import send_to_telegram          # تابع جدید
from news_db import init_db, is_published, mark_as_published

from category_engine import detect_smart_category
from ai_processor import process_news
from sport_formatter import format_sport_news
from game_formatter import format_game_news
from quality_engine import is_high_quality
from importance_engine import is_important
from formatter import format_news   # نسخه جدید formatter

CHECK_INTERVAL = 300  # 5 دقیقه


SPORT_CATEGORIES = {
    "football", "basketball", "volleyball", "tennis",
    "wrestling", "formula1", "combat"
}


def normalize_category(category: str) -> str:
    return "sport" if category in SPORT_CATEGORIES else category


async def check_news():
    news_list = get_latest_news()
    if not news_list:
        print("No new news found.")
        return

    random.shuffle(news_list)

    for item in news_list:
        link = item.get("link") or (item.get("title", "") + item.get("source", ""))

        if is_published(link):
            continue

        # Category Detection
        detected_category = detect_smart_category(
            title=item.get("title", ""),
            summary=item.get("summary", ""),
            source=item.get("source", "")
        )

        category = normalize_category(detected_category)

        print(f"📂 Category: {category} | Original: {detected_category}")

        # AI Processing
        processed = process_news({
            "title": item.get("title", ""),
            "summary": item.get("summary", ""),
            "content": item.get("content", ""),
            "source": item.get("source", ""),
            "category": category,
            "image_url": item.get("image_url") or item.get("image")   # مهم!
        })

        # Sport / Game Processing
        sport_data = None
        game_data = None

        if category == "sport":
            sport_result = format_sport_news(processed["title"], processed["summary"])
            if sport_result.get("blocked"):
                continue
            processed["title"] = sport_result.get("title", processed["title"])
            processed["summary"] = sport_result.get("summary", processed["summary"])
            sport_data = sport_result.get("sport")

        elif category == "gaming":
            game_result = format_game_news(processed["title"], processed["summary"])
            if game_result.get("blocked"):
                continue
            processed["title"] = game_result.get("title", processed["title"])
            processed["summary"] = game_result.get("summary", processed["summary"])
            game_data = game_result.get("game")

        # Quality & Importance Check
        if not is_high_quality(processed["title"], processed["summary"]):
            print("❌ Low quality skipped")
            continue

        if not is_important(processed["title"], processed["summary"], category):
            print("❌ Low importance skipped")
            continue

        # ارسال نهایی به تلگرام
        await send_to_telegram(processed)

        mark_as_published(link)
        print("✅ News published successfully")
        break   # فقط یک خبر در هر چرخه


async def main():
    init_db()
    print("🚀 KhabarF24 Main Engine v7.1 Started")

    while True:
        try:
            await check_news()
        except Exception as e:
            print(f"⚠️ Error in main loop: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
