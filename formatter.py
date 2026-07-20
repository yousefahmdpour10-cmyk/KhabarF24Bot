"""
KhabarF24 Formatter v8.0
Final Post Formatter for Telegram - Beautiful & Professional
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

print("📰 KhabarF24 Formatter v8.0 Loaded")


# =====================================
# Category Styles + Emojis
# =====================================
CATEGORY_STYLE = {
    "politics": {"name": "سیاست", "emoji": "🔴", "header": "🔴 KhabarF24 | 🔴 سیاست", "hashtag": "#سیاست"},
    "iran":     {"name": "ایران", "emoji": "🇮🇷", "header": "🔴 KhabarF24 | 🇮🇷 ایران", "hashtag": "#ایران"},
    "world":    {"name": "جهان", "emoji": "🌍", "header": "🔴 KhabarF24 | 🌍 جهان", "hashtag": "#جهان"},
    "economy":  {"name": "اقتصاد", "emoji": "💰", "header": "🔴 KhabarF24 | 💰 اقتصاد", "hashtag": "#اقتصاد"},
    "technology": {"name": "تکنولوژی", "emoji": "💻", "header": "🔴 KhabarF24 | 💻 تکنولوژی", "hashtag": "#تکنولوژی"},
    "science":  {"name": "علم", "emoji": "🔬", "header": "🔴 KhabarF24 | 🔬 علم", "hashtag": "#علم"},
    "health":   {"name": "سلامت", "emoji": "🏥", "header": "🔴 KhabarF24 | 🏥 سلامت", "hashtag": "#سلامت"},
    
    # Sports
    "football":    {"name": "فوتبال", "emoji": "⚽", "header": "🔴 KhabarF24 | ⚽ فوتبال", "hashtag": "#فوتبال"},
    "basketball":  {"name": "بسکتبال", "emoji": "🏀", "header": "🔴 KhabarF24 | 🏀 بسکتبال", "hashtag": "#بسکتبال"},
    "volleyball":  {"name": "والیبال", "emoji": "🏐", "header": "🔴 KhabarF24 | 🏐 والیبال", "hashtag": "#والیبال"},
    "tennis":      {"name": "تنیس", "emoji": "🎾", "header": "🔴 KhabarF24 | 🎾 تنیس", "hashtag": "#تنیس"},
    "wrestling":   {"name": "کشتی", "emoji": "🤼", "header": "🔴 KhabarF24 | 🤼 کشتی", "hashtag": "#کشتی"},
    "formula1":    {"name": "فرمول یک", "emoji": "🏎️", "header": "🔴 KhabarF24 | 🏎️ فرمول یک", "hashtag": "#فرمول_یک"},
    
    "gaming":   {"name": "گیم", "emoji": "🎮", "header": "🔴 KhabarF24 | 🎮 گیم", "hashtag": "#گیم"},
    "default":  {"name": "اخبار", "emoji": "📰", "header": "🔴 KhabarF24 | 📰 اخبار", "hashtag": "#اخبار"},
}


def get_category_style(category: str):
    cat = category.lower().strip() if category else "default"
    return CATEGORY_STYLE.get(cat, CATEGORY_STYLE["default"])


# =====================================
# Source Formatter
# =====================================
SOURCE_FLAGS = {
    "ISNA": "🇮🇷", "IRNA": "🇮🇷", "Tasnim": "🇮🇷", "Fars": "🇮🇷",
    "BBC": "🇬🇧", "Reuters": "🌍", "CNN": "🇺🇸", "Al Jazeera": "🇶🇦",
    "Al Arabiya": "🇸🇦", "Iran International": "🇬🇧", "Mehr": "🇮🇷",
}

def get_source_flag(source: str) -> str:
    if not source:
        return "🌐"
    for key, flag in SOURCE_FLAGS.items():
        if key.lower() in source.lower():
            return flag
    return "🌐"


def clean_source_name(source: str) -> str:
    if not source:
        return "منبع نامشخص"
    # حذف کلمات اضافی
    source = source.replace("News", "").replace("Agency", "").strip()
    return source


# =====================================
# Main Formatter
# =====================================
def format_news(processed_news: Dict) -> Dict:
    """
    دریافت خروجی ai_processor و تبدیل به فرمت نهایی تلگرام
    """
    title = processed_news.get("title", "").strip()
    summary = processed_news.get("summary", "").strip()
    source = clean_source_name(processed_news.get("source", ""))
    category = processed_news.get("category", "default")
    image_url = processed_news.get("image_url")
    link = processed_news.get("link", "")

    style = get_category_style(category)

    # ساخت متن نهایی
    post_text = f"""
━━━━━━━━━━━━━━━━
{style['header']}
━━━━━━━━━━━━━━━━
📰 **{title}**

✍️ {summary}

🗞️ {get_source_flag(source)} {source}
"""

    if link:
        post_text += f"\n🔗 [ادامه خبر]({link})"

    post_text += f"""
━━━━━━━━━━━━━━━━
📢 @KhabarF24
{style['hashtag']}
"""

    return {
        "text": post_text.strip(),
        "title": title,
        "summary": summary,
        "category": style['name'],
        "hashtag": style['hashtag'],
        "image_url": image_url,
        "parse_mode": "Markdown"
    }


# Helper function for sport detection (if needed)
def get_sport_emoji(category: str) -> str:
    style = get_category_style(category)
    return style['emoji']
