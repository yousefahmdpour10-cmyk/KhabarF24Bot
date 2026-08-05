"""
KhabarF24 Main Engine - Final Working Version
"""

import asyncio
import logging
from config.settings import CHECK_INTERVAL, MAX_POSTS_PER_HOUR, MIN_POST_DELAY
from config.sources import load_sources

from app.services.fetch_service import FetchService
from app.processors.pipeline import NewsPipeline
from app.utils.logger import logger


async def main():
    logger.info("🚀 KhabarF24 Bot Started Successfully")

    fetch_service = FetchService()
    pipeline = NewsPipeline()

    sources = load_sources()
    logger.info(f"Loaded {len(sources)} news sources")

    posts_this_hour = 0

    while True:
        try:
            logger.info("🔄 Checking for new news...")

            # دریافت خبرها
            all_news = await fetch_service.fetch_all(sources)

            if not all_news:
                logger.info("No new news found.")
            else:
                logger.info(f"Fetched {len(all_news)} news items")

                for news in all_news:
                    # محدودیت تعداد پست
                    if posts_this_hour >= MAX_POSTS_PER_HOUR:
                        logger.info("Reached max posts per hour limit")
                        break

                    # پردازش کامل (ترجمه + دسته‌بندی + خلاصه + ارسال به تلگرام)
                    processed = await pipeline.process(news)

                    posts_this_hour += 1
                    logger.info(f"✅ News processed & published: {processed.title[:60]}...")

                    # فاصله بین پست‌ها
                    await asyncio.sleep(MIN_POST_DELAY)

            # صبر تا چرخه بعدی
            await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"❌ Critical error in main loop: {e}", exc_info=True)
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
