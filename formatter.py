"""
KhabarF24 Formatter v7.1

Final Telegram Formatter
Compatible with ai_processor v7.2 + image_processor
"""

print("📰 KhabarF24 Formatter v7.1 Loaded")


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
    "tennis": {"name": "تنیس", "emoji": "🎾", "hashtag": "#تنیس"},
    "wrestling": {"name": "کشتی", "emoji": "🤼", "hashtag": "#کشتی"},
    "formula1": {"name": "فرمول یک", "emoji": "🏎️", "hashtag": "#فرمول_یک"},
    "combat": {"name": "ورزش رزمی", "emoji": "🥊", "hashtag": "#ورزش_رزمی"},
}


# =====================================
# Source Flags
# =====================================
SOURCE_FLAGS = {
    "BBC": "🇬🇧", "Reuters": "🇬🇧", "CNN": "🇺🇸", "ESPN": "🇺🇸",
    "Sky Sports": "🇬🇧", "Al Jazeera": "🇶🇦", "Tasnim": "🇮🇷",
    "Fars News": "🇮🇷", "ISNA": "🇮🇷", "IRNA": "🇮🇷",
    "Iran International": "🇬🇧", "Al Arabiya": "🇸🇦",
    # می‌تونی بعداً اضافه کنی
}


def get_source_flag(source: str) -> str:
    if not source:
        return "🌐"
    
    source_upper = source.upper()
    for name, flag in SOURCE_FLAGS.items():
        if name.upper() in source_upper:
            return flag
    return "🌐"


def clean_source_name(source: str) -> str:
    if not source:
        return "نامشخص"
    
    replacements = {
        "ایسنا": "ISNA", "ایرنا": "IRNA", "تسنیم": "Tasnim",
        "فارس": "Fars News", "بی‌بی‌سی": "BBC", "رویترز": "Reuters",
        "الجزیره": "Al Jazeera", "العربیه": "Al Arabiya",
    }
    
    for old, new in replacements.items():
        if old in source:
            return new
    return source


# =====================================
# Main Formatter
# =====================================
def format_news(title: str, summary: str, source: str, category: str = "world", image_path: str = None):
    """
    فرمت نهایی پست تلگرام
    image_path: اگر عکس پردازش شده باشد، اینجا ارسال شود
    """
    style = CATEGORY_STYLE.get(category.lower(), CATEGORY_STYLE["world"])
    
    category_name = style["name"]
    category_emoji = style["emoji"]
    hashtag = style["hashtag"]

    source = clean_source_name(source)
    source_flag = get_source_flag(source)

    message = f"""━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {category_emoji} {category_name}
━━━━━━━━━━━━━━━━

📰 {title}

{summary}

• 🗞️ {source_flag} {source}
━━━━━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
"""

    return message.strip()


# تابع کمکی برای وقتی که عکس هم داریم
def format_news_with_image(title, summary, source, category, final_image_path=None):
    caption = format_news(title, summary, source, category)
    return caption, final_image_path
