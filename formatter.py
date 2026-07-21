"""
KhabarF24 Formatter v8.1
فرمت نهایی پست تلگرام - بسیار قوی و زیبا
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

print("📰 KhabarF24 Formatter v8.1 Loaded")


# =====================================
# Category Styles
# =====================================
CATEGORY_STYLE = {
    "politics":    {"header": "🔴 KhabarF24 | 🔴 سیاست", "hashtag": "#سیاست"},
    "iran":        {"header": "🔴 KhabarF24 | 🇮🇷 ایران", "hashtag": "#ایران"},
    "world":       {"header": "🔴 KhabarF24 | 🌍 جهان", "hashtag": "#جهان"},
    "economy":     {"header": "🔴 KhabarF24 | 💰 اقتصاد", "hashtag": "#اقتصاد"},
    "technology":  {"header": "🔴 KhabarF24 | 💻 تکنولوژی", "hashtag": "#تکنولوژی"},
    "science":     {"header": "🔴 KhabarF24 | 🔬 علم", "hashtag": "#علم"},
    "health":      {"header": "🔴 KhabarF24 | 🏥 سلامت", "hashtag": "#سلامت"},
    "football":    {"header": "🔴 KhabarF24 | ⚽ فوتبال", "hashtag": "#فوتبال"},
    "basketball":  {"header": "🔴 KhabarF24 | 🏀 بسکتبال", "hashtag": "#بسکتبال"},
    "volleyball":  {"header": "🔴 KhabarF24 | 🏐 والیبال", "hashtag": "#والیبال"},
    "tennis":      {"header": "🔴 KhabarF24 | 🎾 تنیس", "hashtag": "#تنیس"},
    "wrestling":   {"header": "🔴 KhabarF24 | 🤼 کشتی", "hashtag": "#کشتی"},
    "formula1":    {"header": "🔴 KhabarF24 | 🏎️ فرمول یک", "hashtag": "#فرمول_یک"},
    "gaming":      {"header": "🔴 KhabarF24 | 🎮 گیم", "hashtag": "#گیم"},
    "default":     {"header": "🔴 KhabarF24 | 📰 اخبار", "hashtag": "#اخبار"},
}


def get_category_style(category: str):
    cat = str(category).lower().strip()
    return CATEGORY_STYLE.get(cat, CATEGORY_STYLE["default"])


# =====================================
# Main Formatter
# =====================================
def format_news(processed: Dict) -> Dict:
    title = processed.get("title", "").strip()
    summary = processed.get("summary", "").strip()
    source = processed.get("source", "نامشخص")
    category = processed.get("category", "default")
    image_url = processed.get("image_url")
    link = processed.get("link", "")

    style = get_category_style(category)

    caption = f"""
━━━━━━━━━━━━━━━━
{style['header']}
━━━━━━━━━━━━━━━━
📰 **{title}**

✍️ {summary}

🗞️ 🌐 {source}
"""

    if link:
        caption += f"\n🔗 [ادامه خبر]({link})"

    caption += f"""
━━━━━━━━━━━━━━━━
📢 @KhabarF24
{style['hashtag']}
"""

    return {
        "text": caption.strip(),
        "title": title,
        "summary": summary,
        "category": category,
        "hashtag": style['hashtag'],
        "image_url": image_url,
        "parse_mode": "Markdown"
    }
