"""
test_football_builder_smoke.py

اسکریپت تست دستی (نه pytest) — این فایل رو کنار main.py (ریشه‌ی پروژه)
بذار و اجرا کن:

    python test_football_builder_smoke.py

هدف: بررسی اینکه FootballBuilder با داده‌ی ناقص کرش نمی‌کند و خروجی
معقول تولید می‌کند، نه اینکه خروجی "درست" یا "کامل" است — آن را با
چشم بررسی کن.
"""

from datetime import datetime

from app.models.raw_news import RawNews
from app.formatter.sports.football.builder import FootballBuilder


def make_news(**overrides) -> RawNews:
    base = dict(
        title="پیش‌بینی از انتقال ستاره منچستریونایتد",
        content="یک خبر ساده درباره‌ی نقل‌وانتقالات، بدون اطلاعات بازی زنده.",
        summary="خلاصه‌ی خبر نقل‌وانتقال.",
        source="bbc",
        category="sports",
        sport="football",
        fetched_at=datetime.utcnow(),
    )
    base.update(overrides)
    return RawNews(**base)


def run_case(title: str, news: RawNews):
    print(f"\n{'=' * 50}\nCASE: {title}\n{'=' * 50}")
    try:
        builder = FootballBuilder()
        text = builder.build(news)
        print(text if text.strip() else "(خروجی خالی — بررسی کن که این درست است یا نه)")
    except Exception as e:
        print(f"❌ CRASH: {type(e).__name__}: {e}")


if __name__ == "__main__":
    # حالت ۱: خبر نقل‌وانتقال ساده، بدون هیچ داده‌ی مسابقه‌ای
    run_case("خبر نقل‌وانتقال (بدون match_info/lineup)", make_news())

    # حالت ۲: یک گزارش کامل بازی با تیم‌های خانه/میهمان مشخص
    run_case(
        "گزارش کامل بازی (match_info کامل)",
        make_news(
            home_team="Manchester United",
            away_team="Manchester City",
            match_date="1404/05/19",
            match_time="20:00",
            stage="هفته ۲۴",
        ),
    )

    # حالت ۳: فقط نتیجه‌ی بازی، بدون لاین‌آپ
    run_case(
        "فقط نتیجه (بدون lineup/referee/stadium)",
        make_news(
            home_team="Manchester United",
            away_team="Manchester City",
            home_score=2,
            away_score=1,
            result_status="finished",
        ),
    )
