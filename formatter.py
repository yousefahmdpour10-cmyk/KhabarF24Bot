"""
KhabarF24 Formatter v7.2
- همه منابع به انگلیسی نمایش داده می‌شوند
- پرچم منبع
- آماده اتصال به image_processor
"""

print("📰 KhabarF24 Formatter v7.2 Loaded")


# =====================================
# Category Style
# =====================================
CATEGORY_STYLE = {
    "politics": {"name": "سیاست", "emoji": "🔴", "hashtag": "#سیاست"},
    "iran": {"name": "ایران", "emoji": "🇮🇷", "hashtag": "#ایران"},
    "world": {"name": "جهان", "emoji": "🌍", "hashtag": "#جهان"},
    "technology": {"name": "تکنولوژی", "emoji": "💻", "hashtag": "#تکنولوژی"},
    "gaming": {"name": "گیم", "emoji": "🎮", "hashtag": "#گیم"},
    "economy": {"name": "اقتصاد", "emoji": "💰", "hashtag": "#اقتصاد"},
    "health": {"name": "سلامت", "emoji": "🏥", "hashtag": "#سلامت"},
    "science": {"name": "علم", "emoji": "🔬", "hashtag": "#علم"},
    "weather": {"name": "آب‌وهوا", "emoji": "🌦", "hashtag": "#آب_وهوا"},
    
    # Sports
    "football": {"name": "فوتبال", "emoji": "⚽", "hashtag": "#فوتبال"},
    "basketball": {"name": "بسکتبال", "emoji": "🏀", "hashtag": "#بسکتبال"},
    "volleyball": {"name": "والیبال", "emoji": "🏐", "hashtag": "#والیبال"},
}


# =====================================
# Source Dictionary - همه به انگلیسی
# =====================================
SOURCE_FLAGS = {
    "ISNA": "🇮🇷", "IRNA": "🇮🇷", "Tasnim": "🇮🇷", "Fars News": "🇮🇷",
    "BBC": "🇬🇧", "Reuters": "🇬🇧", "CNN": "🇺🇸", "Al Jazeera": "🇶🇦",
    "Al Arabiya": "🇸🇦", "Iran International": "🇬🇧",
    # بعداً اضافه کن
}


def get_source_flag(source: str) -> str:
    if not source:
        return "🌐"
    for name, flag in SOURCE_FLAGS.items():
        if name.lower() in source.lower():
            return flag
    return "🌐"


def clean_source_name(source: str) ->
