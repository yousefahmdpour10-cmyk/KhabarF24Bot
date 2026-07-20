"""
KhabarF24 Quality Engine v8.0
News Quality Control & Filtering
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

print("🧪 KhabarF24 Quality Engine v8.0 Loaded")


# =========================
# Limits
# =========================
MIN_TITLE_LENGTH = 10
MIN_SUMMARY_LENGTH = 25


# =========================
# Allowed English Terms
# =========================
ALLOWED_ENGLISH = [
    # Tech
    "OpenAI", "ChatGPT", "Google", "Apple", "Microsoft", "Tesla", 
    "NVIDIA", "AMD", "Intel", "AI", "iPhone", "iOS", "Android",
    # Sport
    "Manchester United", "Real Madrid", "Barcelona", "Liverpool", 
    "NBA", "FIFA", "UEFA", "Formula 1", "F1", "WTA", "ATP",
]


# =========================
# Bad Phrases
# =========================
BAD_PHRASES = [
    "این متن", "می باشد", "به پایان می دهد", "در این مقاله",
    "برای اطلاعات بیشتر", "ادامه در لینک", "کلیک کنید",
    "این خبر ادامه دارد", "مورد حمله قرار داد"
]


ADVERTISEMENT_WORDS = [
    "خرید", "فروش", "تخفیف", "ثبت نام", "اسپانسر", "تبلیغات",
    "رایگان", "کد تخفیف", "تماس بگیرید", "عضویت", "لینک دانلود"
]


def normalize(text: str) -> str:
    return text.lower() if text else ""


def contains_bad_english(text: str) -> bool:
    if not text:
        return False
    clean = text
    for word in ALLOWED_ENGLISH:
        clean = clean.replace(word, "")
    
    english_words = re.findall(r"[A-Za-z]{4,}", clean)
    return len(english_words) >= 3


def contains_bad_phrase(text: str) -> bool:
    text_lower = normalize(text)
    return any(phrase in text_lower for phrase in BAD_PHRASES)


def is_advertisement(text: str) -> bool:
    text_lower = normalize(text)
    count = sum(1 for word in ADVERTISEMENT_WORDS if word in text_lower)
    return count >= 2


def calculate_quality(title: str = "", summary: str = "", category: str = "world") -> int:
    score = 100
    text = f"{title} {summary}"

    # Title Check
    if not title or len(title.strip()) < MIN_TITLE_LENGTH:
        score -= 40
    elif len(title) > 120:          # خیلی طولانی
        score -= 10

    # Summary Check
    if not summary or len(summary.strip()) < MIN_SUMMARY_LENGTH:
        if category not in ["politics", "sport"]:
            score -= 20

    # Advertisement
    if is_advertisement(text):
        score -= 50

    # Bad Translation / AI Artifacts
    if contains_bad_phrase(text):
        score -= 20

    # Too much unwanted English
    if contains_bad_english(text):
        score -= 15

    # Too short overall
    if len(text.strip()) < 50:
        score -= 25

    return max(0, score)


def is_high_quality(title: str = "", summary: str = "", category: str = "world", minimum: int = 55) -> bool:
    score = calculate_quality(title, summary, category)
    
    logger.info(f"🧪 Quality Score: {score}/100 | Category: {category}")
    
    if score < minimum:
        logger.info("❌ News rejected due to low quality")
        return False
    
    return True
