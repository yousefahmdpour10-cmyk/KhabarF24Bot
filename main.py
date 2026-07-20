"""
KhabarF24 Main Engine v8.0
Improved coordination + Multi-platform ready + Better stability
"""

import asyncio
import random
import logging
from datetime import datetime

# Core modules
from news_fetcher import get_latest_news
from ai_processor import process_news
from formatter import format_news
from category_engine import detect_smart_category

# Specialized formatters (if needed)
from sport_formatter import format_sport_news
from game_formatter import format_game_news

# Quality & Filters
from quality_engine import is_high_quality
from importance_engine import is_important

# Database & Publishing
from news_db import init_db, is_published, mark_as_published

# Platforms (فقط تلگرام فعلاً)
from telegram_bot import send_to_telegram

# Config
CHECK_INTERVAL = 300  # 5 دقیقه
MAX_NEWS_PER_CYCLE = 3   # می‌تونی بعداً بیشتر کنی

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_category(category: str) -> str:
    sport_categories = {"football", "basketball", "volleyball", "tennis", 
                       "wrestling", "formula1", "combat", "sport"}
    if category.lower() in sport_categories or any(s in category.lower() for s in sport_categories):
        return "sport"
    return category.lower().strip()


async def process_and_publish(item: dict) -> bool:
    """Process one news item and publish if qualified"""
    link = item.get("link") or item.get("url") or ""
    title = item.get("title", "")

    if not link and not title:
        return False

    # Deduplication
    if is_published(link, title):
        logger.debug(f"Duplicate skipped: {title[:60]}...")
        return False

    try:
        # Category Detection
        raw_category = detect_smart_category(
            title=title,
            summary=item.get("summary", ""),
            source=item.get("source", "")
        )
        category = normalize_category(raw_category)

        logger.info(f"📂 Category: {category} | Title: {title[:70]}...")

        # AI Processing (تیتر + خلاصه)
        processed = process_news({
            "title": title,
            "summary": item.get("summary", ""),
            "content": item.get("content", ""),
            "source": item.get("source", ""),
            "category": category,
            "image_url": item.get("image_url") or item.get("image"),
            "link": link
        })

        # Specialized Formatting
        if category == "sport":
            sport_result = format_sport_news(processed["title"], processed["summary"])
            if sport_result.get("blocked"):
                return False
            processed["title"] = sport_result.get("title", processed["title"])
            processed["summary"] = sport_result.get("summary", processed["summary"])

        elif category == "gaming":
            game_result = format_game_news(processed["title"], processed["summary"])
            if game_result.get("blocked"):
                return False
            processed["title"] = game_result.get("title", processed["title"])
            processed["summary"] = game_result.get("summary", processed["summary"])

        # Final Quality Check
        if not is_high_quality(processed["title"], processed["summary"]):
            logger.info("❌ Low quality skipped")
            return False

        if not is_important(processed["title"], processed["summary"], category):
            logger.info("❌ Low importance skipped")
            return False

        # Format final output
        final_news = format_news(processed)

        # Send to Telegram
        success = await send_to_telegram(final_news)
        
        if success:
            mark_as_published(link, title)
            logger.info(f"✅ Published: {processed['title'][:80]}...")
            return True
        else:
            logger.warning("⚠️ Failed to send to Telegram")
            return False

    except Exception as e:
        logger.error(f"Error processing news '{title[:60]}...': {e}")
        return False


async def check_news():
    """Main news checking cycle"""
    news_list = get_latest_news()
    if not news_list:
        logger.info("No new news found.")
        return

    random.shuffle(news_list)
    published_count = 0

    for item in news_list:
        if published_count >= MAX_NEWS_PER_CYCLE:
            break

        success = await process_and_publish(item)
        if success:
            published_count += 1
            await asyncio.sleep(8)  # فاصله بین پست‌ها برای جلوگیری از اسپم

    logger.info(f"Cycle finished. Published {published_count} news.")


async def main():
    init_db()
    logger.info("🚀 KhabarF24 Main Engine v8.0 Started - Multi-platform Ready")

    while True:
        try:
            await check_news()
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            await asyncio.sleep(60)
        
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
