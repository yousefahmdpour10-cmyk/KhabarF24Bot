"""
KhabarF24 Importance Engine v8.0
News Importance Scoring - Coordinated with all modules
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

print("🔥 KhabarF24 Importance Engine v8.0 Loaded")


# =========================
# Category Base Weights
# =========================
CATEGORY_WEIGHTS = {
    "politics": 5,
    "iran": 4,
    "world": 2,
    "football": 4,
    "basketball": 3,
    "volleyball": 3,
    "tennis": 3,
    "wrestling": 3,
    "formula1": 4,
    "combat": 3,
    "technology": 4,
    "economy": 4,
    "gaming": 2,
    "health": 2,
    "science": 2,
    "weather": 2,
    "default": 1,
}


# =========================
# Important Keywords per Category
# =========================
IMPORTANT_WORDS = {
    "politics": ["جنگ", "حمله", "موشک", "پهپاد", "درگیری", "بحران", "تحریم", "توافق", "آتش‌بس", "ترور", "انتخابات", "دیپلماسی"],
    "iran": ["ایران", "تهران", "سپاه", "مجلس", "دولت رئیسی", "ابراهیم رئیسی"],
    "world": ["آمریکا", "روسیه", "چین", "اوکراین", "اسرائیل", "غزه", "سازمان ملل"],
    
    "football": ["فوتبال", "گل", "هتریک", "لیگ قهرمانان", "فینال", "انتقال", "قرارداد", "VAR"],
    "basketball": ["NBA", "بسکتبال", "دانک", "قهرمانی NBA"],
    "volleyball": ["والیبال", "FIVB", "اسپک"],
    "tennis": ["تنیس", "گرند اسلم", "جوکوویچ", "ATP", "WTA"],
    "wrestling": ["کشتی", "کشتی آزاد", "کشتی فرنگی", "مدال"],
    "formula1": ["فرمول یک", "F1", "گرندپری"],

    "technology": ["هوش مصنوعی", "AI", "ChatGPT", "انویدیا", "تراشه", "هک", "امنیت سایبری"],
    "economy": ["دلار", "تورم", "بورس", "بیت‌کوین", "کریپتو", "طلا", "نفت"],
}


HIGH_IMPACT_WORDS = [
    "خبر فوری", "فوری", "لحظاتی قبل", "اکنون", "کشته", "تلفات", "حمله گسترده",
    "رکورد تاریخی", "قهرمان شد", "قهرمانی جهان", "فاجعه", "جنگ آغاز شد"
]


def contains_any(text: str, words: list) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    return any(word.lower() in text_lower for word in words)


def calculate_importance(title: str = "", summary: str = "", category: str = "world") -> float:
    text = f"{title} {summary}".lower()
    score = 1.0

    # Base category weight
    norm_category = category.lower()
    score += CATEGORY_WEIGHTS.get(norm_category, CATEGORY_WEIGHTS["default"])

    # Keyword hits
    for cat, words in IMPORTANT_WORDS.items():
        hits = sum(1 for word in words if word.lower() in text)
        if hits:
            score += hits
            if cat == norm_category:
                score += 2.5  # Bonus for matching category

    # High impact words
    for word in HIGH_IMPACT_WORDS:
        if word.lower() in text:
            score += 3.5

    return round(min(score, 12), 1)


def is_important(title: str = "", summary: str = "", category: str = "world", minimum: float = 5.0) -> bool:
    score = calculate_importance(title, summary, category)
    
    logger.info(f"🔥 Importance Score: {score}/12 | Category: {category}")
    
    return score >= minimum
