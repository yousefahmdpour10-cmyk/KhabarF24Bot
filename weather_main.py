"""اجرای مستقل گزارش روزانه هواشناسی KhabarF24."""

import asyncio

from app.weather.daily_weather_publisher import publish_daily_weather
from app.utils.logger import logger


async def main():
    try:
        await publish_daily_weather()
    except Exception:
        logger.exception("Daily weather publication failed")
        raise


if __name__ == "__main__":
    asyncio.run(main())
