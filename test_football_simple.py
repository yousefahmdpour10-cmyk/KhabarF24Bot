import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional, List


# ==================== مدل ساده ====================
@dataclass
class RawNews:
    title: str
    summary: str
    source: str
    url: str = ""
    content: str = ""
    sport: Optional[str] = None
    sport_name: Optional[str] = None
    sport_emoji: Optional[str] = None
    sport_hashtag: Optional[str] = None
    goals: List[str] = field(default_factory=list)


# ==================== کلمات کلیدی ====================
SPORTS = {
    "football": {
        "name": "فوتبال",
        "emoji": "⚽",
        "hashtag": "#فوتبال",
        "keywords": [
            "football", "soccer", "fifa", "uefa", "goal", "penalty",
            "premier league", "la liga", "serie a", "bundesliga",
            "champions league", "فوتبال", "گل", "پنالتی", "لیگ برتر",
            "جام جهانی", "یوفا", "فیفا", "رئال", "بارسلونا", "رونالدو"
        ]
    },
    "basketball": {
        "name": "بسکتبال",
        "emoji": "🏀",
        "hashtag": "#بسکتبال",
        "keywords": ["basketball", "nba", "بسکتبال", "ان بی ای"]
    }
}


# ==================== تشخیص رشته ====================
class SportDetector:
    async def process(self, news: RawNews) -> RawNews:
        text = f"{news.title} {news.summary}".lower()
        scores = defaultdict(int)

        for sport_id, sport in SPORTS.items():
            for keyword in sport["keywords"]:
                if keyword.lower() in text:
                    scores[sport_id] += 1

        if scores:
            best = max(scores, key=scores.get)
            news.sport = best
            news.sport_name = SPORTS[best]["name"]
            news.sport_emoji = SPORTS[best]["emoji"]
            news.sport_hashtag = SPORTS[best]["hashtag"]
            print(f"✅ Sport detected: {news.sport_name}")
        else:
            print("❌ Sport not detected")

        return news


# ==================== فرمت‌کننده ساده فوتبال ====================
class FootballFormatter:
    async def format(self, news: RawNews) -> str:
        text = ""
        text += "━━━━━━━━━━━━━━━━\n"
        text += f"🔴 KhabarF24 | {news.sport_emoji or '⚽'} {news.sport_name or 'فوتبال'}\n"
        text += "━━━━━━━━━━━━━━━━\n\n"
        text += f"📰 {news.title}\n\n"
        text += f"📌 منبع: {news.source}\n"
        text += "\n━━━━━━━━━━━━━━━━\n"
        if news.sport_hashtag:
            text += f"\n{news.sport_hashtag}"
        return text


# ==================== اجرای تست ====================
async def main():
    news = RawNews(
        title="رئال مادرید با گل رونالدو ۳ بر ۱ بارسلونا را شکست داد",
        summary="در ال کلاسیکو، کریستیانو رونالدو دو گل زد و وینیسیوس هم یک گل به ثمر رساند.",
        source="ورزش۳"
    )

    print("=== شروع تست ===\n")

    detector = SportDetector()
    news = await detector.process(news)

    print("\n=== نتیجه تشخیص ===")
    print(f"Sport ID     : {news.sport}")
    print(f"Sport Name   : {news.sport_name}")
    print(f"Emoji        : {news.sport_emoji}")
    print(f"Hashtag      : {news.sport_hashtag}")

    formatter = FootballFormatter()
    post = await formatter.format(news)

    print("\n=== پست نهایی ===")
    print(post)


if __name__ == "__main__":
    asyncio.run(main())
