"""
KhabarF24 Formatter v8.2
"""

import logging

logger = logging.getLogger(__name__)

print("📰 KhabarF24 Formatter v8.2 Loaded")

CATEGORY_STYLE = {
    "politics":   {"header": "🔴 KhabarF24 | 🔴 سیاست", "hashtag": "#سیاست"},
    "iran":       {"header": "🔴 KhabarF24 | 🇮🇷 ایران", "hashtag": "#ایران"},
    "world":      {"header": "🔴 KhabarF24 | 🌍 جهان", "hashtag": "#جهان"},
    "economy":    {"header": "🔴 KhabarF24 | 💰 اقتصاد", "hashtag": "#اقتصاد"},
    "technology": {"header": "🔴 KhabarF24 | 💻 فناوری", "hashtag": "#فناوری"},
    "science":    {"header": "🔴 KhabarF24 | 🔬 علم", "hashtag": "#علم"},
    "health":     {"header": "🔴 KhabarF24 | 🏥 سلامت", "hashtag": "#سلامت"},
    "football":   {"header": "🔴 KhabarF24 | ⚽ فوتبال", "hashtag": "#فوتبال"},
    "basketball": {"header": "🔴 KhabarF24 | 🏀 بسکتبال", "hashtag": "#بسکتبال"},
    "volleyball": {"header": "🔴 KhabarF24 | 🏐 والیبال", "hashtag": "#والیبال"},
    "tennis":     {"header": "🔴 KhabarF24 | 🎾 تنیس", "hashtag": "#تنیس"},
    "wrestling":  {"header": "🔴 KhabarF24 | 🤼 کشتی", "hashtag": "#کشتی"},
    "formula1":   {"header": "🔴 KhabarF24 | 🏎️ فرمول یک", "hashtag": "#فرمول_یک"},
    "gaming":     {"header": "🔴 KhabarF24 | 🎮 گیم", "hashtag": "#گیم"},
    "sport":      {"header": "🔴 KhabarF24 | ⚽ ورزش", "hashtag": "#ورزش"},
    "default":    {"header": "🔴 KhabarF24 | 📰 اخبار", "hashtag": "#اخبار"},
}


def get_category_style(category: str):
    category = str(category).lower().strip()
    return CATEGORY_STYLE.get(category, CATEGORY_STYLE["default"])


def clean_source_name(source: str) -> str:
    if not source:
        return "نامشخص"
    return source.strip()


def get_source_flag(source: str) -> str:
    return "📰"


def format_news(title: str, summary: str, source: str, category: str = "world"):

    style = get_category_style(category)

    header = style["header"]
    hashtag = style["hashtag"]

    source = clean_source_name(source)
    source_flag = get_source_flag(source)

    message = f"""━━━━━━━━━━━━━━━━
{header}
━━━━━━━━━━━━━━━━

📰 *{title}*

{summary}

• {source_flag} {source}

━━━━━━━━━━━━━━━━
📢 @KhabarF24

{hashtag}
"""

    return message.strip()
