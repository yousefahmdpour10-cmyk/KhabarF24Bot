"""
KhabarF24 Category Engine v8.1
بهبود دقت تشخیص دسته‌بندی + اولویت‌بندی
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

print("🔥 KhabarF24 Category Engine v8.1 Loaded")


CATEGORIES = {
    "politics": {
        "name": "سیاست", "emoji": "🔴", "hashtag": "#سیاست", "priority": 12,
        "keywords": ["جنگ", "حمله", "موشک", "پهپاد", "ارتش", "تحریم", "انتخابات", "ترور", "کودتا", "رئیس‌جمهور", "دولت", "مجلس", "نظامی", "اسرائیل", "غزه", "اوکراین"]
    },
    "football": {
        "name": "فوتبال", "emoji": "⚽", "hashtag": "#فوتبال", "priority": 10,
        "keywords": ["فوتبال", "football", "soccer", "مسی", "رونالدو", "امباپه", "لیگ قهرمانان", "پرسپولیس", "استقلال", "تراکتور"]
    },
    "technology": {
        "name": "تکنولوژی", "emoji": "💻", "hashtag": "#تکنولوژی", "priority": 7,
        "keywords": ["هوش مصنوعی", "AI", "ChatGPT", "انویدیا", "تراشه", "اپل", "گوگل", "سامسونگ", "توییتر", "متا"]
    },
    "economy": {
        "name": "اقتصاد", "emoji": "💰", "hashtag": "#اقتصاد", "priority": 6,
        "keywords": ["دلار", "تورم", "بورس", "بیت کوین", "کریپتو", "قیمت", "اقتصادی"]
    },
    # بقیه دسته‌ها...
    "world": {
        "name": "جهان", "emoji": "🌍", "hashtag": "#جهان", "priority": 4,
        "keywords": ["آمریکا", "روسیه", "چین", "اروپا", "بریتانیا"]
    },
}


def detect_smart_category(title: str = "", summary: str = "", source: str = "") -> str:
    if not title and not summary:
        return "world"

    text = f"{title} {summary} {source}".lower()

    scores = {}
    for category, data in CATEGORIES.items():
        score = sum(1 for word in data["keywords"] if word.lower() in text) * data["priority"]
        scores[category] = score

    # اولویت سیاست خیلی بالا
    if scores.get("politics", 0) >= 8:
        return "politics"

    # ورزش
    sport_cats = ["football", "basketball", "volleyball", "tennis", "wrestling", "formula1"]
    best_sport = max((cat for cat in sport_cats if cat in scores), key=lambda x: scores.get(x, 0), default=None)
    
    if best_sport and scores.get(best_sport, 0) >= 10:
        return best_sport

    # بهترین دسته
    best = max(scores, key=scores.get)
    return best if scores[best] > 3 else "world"


def get_category_info(category: str) -> Dict:
    data = CATEGORIES.get(category.lower(), CATEGORIES["world"])
    return {
        "name": data["name"],
        "emoji": data["emoji"],
        "hashtag": data["hashtag"]
    }
