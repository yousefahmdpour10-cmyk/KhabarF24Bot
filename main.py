"""
KhabarF24 Main Engine
"""

import sys
import time
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import asyncio
from config.settings import CHECK_INTERVAL
from config.sources import load_sources
from app.services.fetch_service import FetchService
from app.processors.pipeline import NewsPipeline
from app.utils.logger import logger

# حداکثر مدت هر اجرا، کمی کمتر از سقف ۶ ساعته‌ی GitHub Actions
# تا وقت کافی برای بسته‌شدن تمیز و شروع اجرای بعدی باقی بماند.
MAX_RUNTIME_SECONDS = 5 * 3600 + 50 * 60  # 5h50m


async def main():
    logger.info("KhabarF24 Bot Started Successfully")

    start_time = time.monotonic()

    fetch_service = FetchService()
    pipeline = NewsPipeline()
    sources = load_sources()

    logger.info(f"Loaded {len(sources)} sources")

    while True:
        if time.monotonic() - start_time > MAX_RUNTIME_SECONDS:
            logger.info("Max runtime reached, exiting cleanly for next scheduled run")
            break

        try:
            logger.info("Checking for new news...")
            all_news = await fetch_service.fetch_all(sources)

            if all_news:
                for news in all_news[:3]:  # فعلاً حداکثر ۳ خبر در هر چرخه
                    await pipeline.process(news)
                    await asyncio.sleep(5)

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
