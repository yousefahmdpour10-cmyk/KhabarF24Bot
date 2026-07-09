from telegram import Bot
from config import BOT_TOKEN, CHANNEL_ID

bot = Bot(token=BOT_TOKEN)

async def send_message(text):
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=text
    )
