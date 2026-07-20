"""
KhabarF24 Category Engine v8.0
Smart Category Detection + Sport Separation
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

print("🔥 KhabarF24 Category Engine v8.0 Loaded")


# ==========================
# Categories Database
# ==========================
CATEGORIES = {
    "politics": {
        "name": "سیاست", "emoji": "🔴", "hashtag": "#سیاست", "priority": 10,
        "keywords": ["جنگ", "حمله", "موشک", "پهپاد", "ارتش", "تحریم", "انتخابات", "ترور", "کودتا", "رئیس‌جمهور"]
    },
    "football": {
        "name": "فوتبال", "emoji": "⚽", "hashtag": "#فوتبال", "priority": 9,
        "keywords": ["فوتبال", "football", "soccer", "مسی", "رونالدو", "امباپه", "لیگ قهرمانان", "VAR"]
    },
    "basketball": {
        "name": "بسکتبال", "emoji": "🏀", "hashtag": "#بسکتبال", "priority": 8,
        "keywords": ["بسکتبال", "basketball", "NBA", "دانک", "ریباند"]
    },
    "volleyball": {
        "name": "والیبال", "emoji": "🏐", "hashtag": "#والیبال", "priority": 8,
        "keywords": ["والیبال", "volleyball", "FIVB", "اسپک"]
    },
    "tennis": {
        "name": "تنیس", "emoji": "🎾", "hashtag": "#تنیس", "priority": 7,
        "keywords": ["تنیس", "tennis", "ATP", "WTA", "گرند اسلم"]
    },
    "wrestling": {
        "name": "کشتی", "emoji": "🤼", "hashtag": "#کشتی", "priority": 7,
        "keywords": ["کشتی", "uww", "کشتی آزاد", "کشتی فرنگی"]
    },
    "formula1": {
        "name": "فرمول یک", "emoji": "🏎️", "hashtag": "#فرمول_یک", "priority": 8,
        "keywords": ["فرمول یک", "formula 1", "f1", "گرندپری"]
    },
    "technology": {
        "name": "تکنولوژی", "emoji": "💻", "hashtag": "#تکنولوژی", "priority": 6,
        "keywords": ["هوش مصنوعی", "AI", "ChatGPT", "انویدیا", "تراشه"]
    },
    "economy": {
        "name": "اقتصاد", "emoji": "💰", "hashtag": "#اقتصاد", "priority": 5,
        "keywords": ["دلار", "تورم", "بورس", "بیت کوین", "کریپتو"]
    },
    "gaming": {
        "name": "گیم", "emoji": "🎮", "hashtag": "#گیم", "priority": 5,
        "keywords": ["گیم", "gaming", "playstation", "xbox"]
    },
    "world": {
        "name": "جهان", "emoji": "🌍", "hashtag": "#جهان", "priority": 3,
        "keywords": ["آمریکا", "روسیه", "چین", "اوکراین"]
    },
    "health": {
        "name": "سلامت", "emoji": "🏥", "hashtag": "#سلامت", "priority": 3,
        "keywords": ["بیماری", "واکسن", "پزشکی"]
    },
    "weather": {
        "name": "آب‌وهوا", "emoji": "🌦", "hashtag": "#آب_وهوا", "priority": 3,
        "keywords": ["هواشناسی", "طوفان", "سیل"]
    },
}


def detect_smart_category(title: str = "", summary: str = "", source: str = "") -> str:
    text = f"{title} {summary} {source}".lower()
    scores = {}

    for category, data in CATEGORIES.items():
        score = sum(data["priority"] for word in data["keywords"] if word.lower() in text)
        scores[category] = score

    # Politics has highest priority
    if scores.get("politics", 0) >= 15:
        return "politics"

    # Sport priority
    sport_cats = ["football", "basketball", "volleyball", "tennis", "wrestling", "formula1"]
    best_sport = max(sport_cats, key=lambda x: scores.get(x, 0))
    
    if scores.get(best_sport, 0) >= 10:
        return best_sport

    # Default to highest score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "world"


def get_category_info(category: str) -> Dict:
    data = CATEGORIES.get(category.lower(), CATEGORIES["world"])
    return {
        "name": data["name"],
        "emoji": data["emoji"],
        "hashtag": data["hashtag"]
    }       CATEGORIES["world"]

    )


    return {


        "category": category,


        "name": data["name"],


        "emoji": data["emoji"],


        "hashtag": data["hashtag"]


    }
