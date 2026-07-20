"""
KhabarF24 Telegram Bot v8.1
Fully coordinated with formatter v8 + image processor
"""

from telegram import Bot
from config import BOT_TOKEN, CHANNEL_ID
import asyncio
import os
import logging

# Core imports
from formatter import format_news
from image_processor import download_image, add_khabarf24_watermark

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)


async def send_to_telegram(processed_news: dict):
    """
    ارسال نهایی خبر به کانال تلگرام
    processed_news: خروجی تابع process_news از ai_processor
    """
    try:
        # استفاده از formatter v8
        formatted = format_news(processed_news)
        
        caption = formatted["text"]
        image_url = processed_news.get("image_url")

        logger.info(f"📤 Sending news: {processed_news.get('title', '')[:60]}...")

        final_image_path = None

        # اگر عکس داشت → دانلود + واترمارک
        if image_url:
            temp_image = download_image(image_url)
            if temp_image and os.path.exists(temp_image):
                final_image_path = add_khabarf24_watermark(temp_image)

        if final_image_path and os.path.exists(final_image_path):
            # ارسال با عکس
            with open(final_image_path, 'rb') as photo:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=photo,
                    caption=caption,
                    parse_mode='Markdown'
                )
            logger.info("✅ News sent with photo")

            # پاکسازی فایل‌های موقتی
            try:
                os.remove(final_image_path)
                if temp_image and os.path.exists(temp_image):
                    os.remove(temp_image)
            except Exception as e:
                logger.warning(f"Cleanup warning: {e}")
        else:
            # ارسال فقط متن
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption,
                parse_mode='Markdown'
            )
            logger.info("✅ News sent as text")

        return True

    except Exception as e:
        logger.error(f"❌ Error sending to Telegram: {e}")
        return False


# تست سریع
async def test_send():
    test_news = {
        "title": "تست ارسال خبر",
        "summary": "این یک خبر آزمایشی برای بررسی فرمت نهایی است. امیدواریم خوب نمایش داده شود.",
        "source": "CITNA",
        "category": "politics",
        "image_url": None
    }
    success = await send_to_telegram(test_news)
    print("Test successful" if success else "Test failed")


if __name__ == "__main__":
    asyncio.run(test_send())
