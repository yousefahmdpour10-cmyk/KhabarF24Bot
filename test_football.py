import asyncio
from app.models.raw_news import RawNews
from app.processors.sport.detector import SportDetector
from app.formatter.sports.football import FootballFormatter


async def test_football():
    # یک خبر آزمایشی فوتبال
    news = RawNews(
        title="رئال مادرید با گل رونالدو ۳ بر ۱ بارسلونا را شکست داد",
        summary="در ال کلاسیکو، کریستیانو رونالدو دو گل زد و وینیسیوس هم یک گل به ثمر رساند. بارسلونا هم یک گل زد.",
        source="ورزش۳",
        url="https://example.com",
        content="",
    )

    # مرحله ۱: تشخیص رشته ورزشی
    detector = SportDetector()
    news = await detector.process(news)

    print("=== نتیجه تشخیص رشته ===")
    print(f"Sport: {news.sport}")
    print(f"Sport Name: {news.sport_name}")
    print(f"Emoji: {news.sport_emoji}")
    print(f"Hashtag: {news.sport_hashtag}")
    print()

    # مرحله ۲: فرمت کردن پست (فعلاً بدون جزئیات گل و ...)
    formatter = FootballFormatter()
    post = await formatter.format(news)

    print("=== پست نهایی ===")
    print(post)


if __name__ == "__main__":
    asyncio.run(test_football())
