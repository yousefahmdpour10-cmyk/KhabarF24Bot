"""
KhabarF24 Telegram Bot v8.2 - Fixed Version
"""

from telegram import Bot
from config import BOT_TOKEN, CHANNEL_ID
import asyncio
import os
import logging

from formatter import format_news
from image_processor import download_image, add_khabarf24_watermark

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)


async def send_to_telegram(processed_news: dict):
    try:
        # فراخوانی مستقیم format_news (رشته برمی‌گرداند)
        caption = format_news(
            title=processed_news.get("title", ""),
            summary=processed_news.get("summary", ""),
            source=processed_news.get("source", "نامشخص"),
            category=processed_news.get("category", "world")
        )

        image_url = processed_news.get("image_url")
        logger.info(f"📤 Sending: {processed_news.get('title', '')[:60]}...")

        final_image_path = None

        if image_url:
            temp_image = download_image(image_url)
            if temp_image and os.path.exists(temp_image):
                final_image_path = add_khabarf24_watermark(temp_image)

        if final_image_path and os.path.exists(final_image_path):
            with open(final_image_path, 'rb') as photo:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=photo,
                    caption=caption,
                    parse_mode='Markdown'
                )
            logger.info("✅ Sent with photo")
            # پاکسازی
            try:
                os.remove(final_image_path)
                if temp_image and os.path.exists(temp_image):
                    os.remove(temp_image)
            except:
                pass
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption,
                parse_mode='Markdown'
            )
            logger.info("✅ Sent as text")

        return True

    except Exception as e:
        logger.error(f"❌ Telegram send error: {e}", exc_info=True)
        return False
