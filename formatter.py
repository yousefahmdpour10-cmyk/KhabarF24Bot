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
def format_news(title: str, summary: str, source: str, category: str = "world"):
    style = get_category_style(category)

header = style["header"]
hashtag = style["hashtag"]

    source = clean_source_name(source)
    source_flag = get_source_flag(source)

    # تیتر بولد (در تلگرام با ** قوی نمایش داده می‌شود)
    message = f"""━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {category_emoji} {category_name}
━━━━━━━━━━━━━━━━

📰 **{title}**

{summary}

• 🗞️ {source_flag} {source}
━━━━━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
"""

    return message.strip()
