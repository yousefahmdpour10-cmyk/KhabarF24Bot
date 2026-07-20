"""
KhabarF24 Telegram Bot v7.1
- ارسال متن + عکس با واترمارک
- هماهنگ با ai_processor و formatter
"""

from telegram import Bot
from config import BOT_TOKEN, CHANNEL_ID
import asyncio
import os

# Importهای پروژه
from formatter import format_news, format_news_with_image
from image_processor import download_image, add_khabarf24_watermark

bot = Bot(token=BOT_TOKEN)


async def send_to_telegram(news: dict):
    """
    ارسال خبر به کانال تلگرام
    news: خروجی تابع process_news
    """
    try:
        title = news.get("title", "")
        summary = news.get("summary", "")
        source = news.get("source", "Unknown")
        category = news.get("category", "world")
        image_url = news.get("image_url")

        print(f"📤 در حال ارسال خبر: {title[:50]}...")

        # اگر عکس داشت → دانلود + واترمارک
        final_image_path = None
        if image_url:
            temp_image = download_image(image_url)
            if temp_image:
                final_image_path = add_khabarf24_watermark(temp_image)

        # ساخت کپشن
        caption = format_news(title, summary, source, category)

        if final_image_path and os.path.exists(final_image_path):
            # ارسال با عکس
            with open(final_image_path, 'rb') as photo:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=photo,
                    caption=caption,
                    parse_mode='HTML'
                )
            print("✅ خبر با عکس ارسال شد.")
            
            # پاک کردن فایل‌های موقتی
            try:
                os.remove(final_image_path)
                if temp_image and os.path.exists(temp_image):
                    os.remove(temp_image)
            except:
                pass
        else:
            # ارسال فقط متن
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption,
                parse_mode='HTML'
            )
            print("✅ خبر متنی ارسال شد.")

    except Exception as e:
        print(f"❌ خطا در ارسال به تلگرام: {e}")


# تابع کمکی برای تست
async def test_send():
    test_news = {
        "title": "تست عنوان خبر",
        "summary": "این یک خلاصه آزمایشی برای چک کردن فرمت است.",
        "source": "ISNA",
        "category": "politics",
        "image_url": None  # می‌تونی لینک عکس بذاری برای تست
    }
    await send_to_telegram(test_news)


# اگر مستقیم اجرا شود
if __name__ == "__main__":
    asyncio.run(test_send())
