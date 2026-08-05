"""
KhabarF24 Main Entry Point
"""

import asyncio
import logging
from config.settings import CHECK_INTERVAL
from app.utils.logger import logger

# بعداً سرویس‌ها را اضافه می‌کنیم
async def main():
    logger.info("🚀 KhabarF24 Bot Started")
    
    while True:
        try:
            logger.info("Checking for new news...")
            # اینجا بعداً fetch و pipeline را صدا می‌زنیم
            await asyncio.sleep(CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
