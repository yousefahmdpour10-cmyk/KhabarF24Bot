"""
KhabarF24 Daily Weather Publisher
انتشار گزارش روزانه هواشناسی ۳۱ استان ایران در یک پست.
"""

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Bot
from telegram.error import TelegramError

from config import settings
from app.weather.weather_service import WeatherService
from app.utils.logger import logger


IRAN_TZ = ZoneInfo("Asia/Tehran")
MAX_CONCURRENT_REQUESTS = 5

# نام استان، مرکز استان، عرض جغرافیایی، طول جغرافیایی
PROVINCES = [
    ("آذربایجان شرقی", "تبریز", 38.0962, 46.2738),
    ("آذربایجان غربی", "ارومیه", 37.5527, 45.0761),
    ("اردبیل", "اردبیل", 38.2498, 48.2933),
    ("اصفهان", "اصفهان", 32.6546, 51.6680),
    ("البرز", "کرج", 35.8400, 50.9391),
    ("ایلام", "ایلام", 33.6374, 46.4227),
    ("بوشهر", "بوشهر", 28.9234, 50.8203),
    ("تهران", "تهران", 35.6892, 51.3890),
    ("چهارمحال و بختیاری", "شهرکرد", 32.3256, 50.8644),
    ("خراسان جنوبی", "بیرجند", 32.8663, 59.2211),
    ("خراسان رضوی", "مشهد", 36.2972, 59.6067),
    ("خراسان شمالی", "بجنورد", 37.4747, 57.3290),
    ("خوزستان", "اهواز", 31.3183, 48.6706),
    ("زنجان", "زنجان", 36.6736, 48.4787),
    ("سمنان", "سمنان", 35.5769, 53.3921),
    ("سیستان و بلوچستان", "زاهدان", 29.4963, 60.8629),
    ("فارس", "شیراز", 29.5918, 52.5837),
    ("قزوین", "قزوین", 36.2688, 50.0041),
    ("قم", "قم", 34.6416, 50.8746),
    ("کردستان", "سنندج", 35.3149, 46.9988),
    ("کرمان", "کرمان", 30.2839, 57.0834),
    ("کرمانشاه", "کرمانشاه", 34.3142, 47.0650),
    ("کهگیلویه و بویراحمد", "یاسوج", 30.6682, 51.5879),
    ("گلستان", "گرگان", 36.8456, 54.4393),
    ("گیلان", "رشت", 37.2808, 49.5832),
    ("لرستان", "خرم‌آباد", 33.4878, 48.3558),
    ("مازندران", "ساری", 36.5633, 53.0601),
    ("مرکزی", "اراک", 34.0917, 49.6892),
    ("هرمزگان", "بندرعباس", 27.1832, 56.2666),
    ("همدان", "همدان", 34.7992, 48.5146),
    ("یزد", "یزد", 31.8974, 54.3569),
]


def format_temperature(value):
    if value is None:
        return "نامشخص"
    try:
        return f"{round(float(value))}°"
    except (TypeError, ValueError):
        return "نامشخص"


def format_probability(value):
    if value is None:
        return None
    try:
        return f"{round(float(value))}%"
    except (TypeError, ValueError):
        return None


async def fetch_province(service, semaphore, province):
    name, capital, latitude, longitude = province

    async with semaphore:
        try:
            result = await service.get_weather(
                latitude=latitude,
                longitude=longitude,
                forecast_days=1,
            )

            if not result:
                logger.warning("Weather unavailable for %s", name)
                return name, capital, None

            daily = result.get("daily") or []
            today = daily[0] if daily else {}

            return name, capital, {
                "icon": today.get("icon") or "🌡️",
                "description": today.get("description") or "نامشخص",
                "min": today.get("temperature_min"),
                "max": today.get("temperature_max"),
                "rain_probability": today.get(
                    "precipitation_probability"
                ),
            }

        except Exception:
            logger.exception("Weather failed for %s", name)
            return name, capital, None


def build_weather_message(results):
    today = datetime.now(IRAN_TZ)
    persian_date = today.strftime("%Y/%m/%d")

    lines = [
        "🌤️ KhabarF24 | هواشناسی ایران",
        "",
        f"📅 پیش‌بینی روزانه | {persian_date}",
        "🌡️ وضعیت و دمای پیش‌بینی‌شده در مراکز استان‌ها",
        "",
    ]

    valid_results = []

    for province, capital, weather in results:
        if weather is None:
            lines.append(f"▫️ {province}: اطلاعات در دسترس نیست")
            continue

        low = format_temperature(weather["min"])
        high = format_temperature(weather["max"])
        icon = weather["icon"]
        description = weather["description"]
        probability = format_probability(weather["rain_probability"])

        line = (
            f"{icon} {province} ({capital}): "
            f"{low} تا {high} | {description}"
        )

        if probability is not None:
            line += f" | احتمال بارش {probability}"

        lines.append(line)
        valid_results.append(weather)

    if valid_results:
        lines.extend(["", "ℹ️ داده‌ها از Open-Meteo دریافت شده‌اند."])

    lines.extend([
        "",
        "📢 @KhabarF24",
        "",
        "#هواشناسی",
        "#ایران",
    ])

    message = "\n".join(lines)

    # سقف تلگرام برای متن پیام ۴۰۹۶ نویسه است.
    if len(message) > 4000:
        logger.warning(
            "Weather message is too long: %s characters",
            len(message),
        )
        raise ValueError(
            "گزارش هواشناسی از محدودیت طول یک پیام تلگرام بیشتر است."
        )

    return message


async def publish_daily_weather():
    if not settings.BOT_TOKEN:
        raise ValueError("BOT_TOKEN تنظیم نشده است")

    if not settings.CHANNEL_ID:
        raise ValueError("CHANNEL_ID تنظیم نشده است")

    logger.info("Starting daily weather publication")

    service = WeatherService()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    results = await asyncio.gather(
        *[
            fetch_province(service, semaphore, province)
            for province in PROVINCES
        ]
    )

    message = build_weather_message(results)

    async with Bot(token=settings.BOT_TOKEN) as bot:
        await bot.send_message(
            chat_id=settings.CHANNEL_ID,
            text=message,
            disable_web_page_preview=True,
        )

    logger.info(
        "Daily weather report published. "
        "Successful provinces: %s/%s",
        sum(1 for item in results if item[2] is not None),
        len(PROVINCES),
    )
