from telegram import Bot
from config import BOT_TOKEN, CHANNEL_ID

bot = Bot(token=BOT_TOKEN)

async def send_message(text):
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text
        )
        print("✅ Message sent successfully.")

    except Exception as e:
        print(f"❌ Telegram Error: {e}")
