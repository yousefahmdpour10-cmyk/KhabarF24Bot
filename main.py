import asyncio
from telegram_bot import send_message

async def main():
    await send_message("🤖 KhabarF24Bot Online")

asyncio.run(main())
