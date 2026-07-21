"""
KhabarF24 Sport Formatter v8.0
فرمت هوشمند اخبار ورزشی + تشخیص رشته + ایموجی + هشتگ
"""

import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)

print("⚽ KhabarF24 Sport Formatter v8.0 Loaded")


# =====================================
# Sports Database
# =====================================
SPORTS = {
    "football": {
        "name": "فوتبال",
        "emoji": "⚽",
        "hashtag": "#فوتبال",
        "keywords": ["فوتبال", "football", "soccer", "گل", "VAR", "لیگ قهرمانان", "مسی", "رونالدو", "امباپه"]
    },
    "basketball": {
        "name": "بسکتبال",
        "emoji": "🏀",
        "hashtag": "#بسکتبال",
        "keywords": ["بسکتبال", "basketball", "NBA", "دانک", "ریباند", "لبران", "کری"]
    },
    "volleyball": {
        "name": "والیبال",
        "emoji": "🏐",
        "hashtag": "#والیبال",
        "keywords": ["والیبال", "volleyball", "FIVB", "اسپک", "ست"]
    },
    "tennis": {
        "name": "تنیس",
        "emoji": "🎾",
        "hashtag": "#تنیس",
        "keywords": ["تنیس", "tennis", "ATP", "WTA", "گرند اسلم", "جوکوویچ"]
    },
    "wrestling": {
        "name": "کشتی",
        "emoji": "🤼",
        "hashtag": "#کشتی",
        "keywords": ["کشتی", "uww", "کشتی آزاد", "مدال"]
    },
    "formula1": {
        "name": "فرمول یک",
        "emoji": "🏎️",
        "hashtag": "#فرمول_یک",
        "keywords": ["فرمول یک", "formula 1", "f1", "گرندپری"]
    },
    "combat": {
        "name": "ورزش رزمی",
        "emoji": "🥊",
        "hashtag": "#ورزش_رزمی",
        "keywords": ["UFC", "MMA", "بوکس", "ناک اوت"]
    },
}


# =====================================
# Team Flags / Nicknames
# =====================================
TEAM_FLAGS = {
    "منچستر یونایتد": "🔴 منچستر یونایتد",
    "Manchester United": "🔴 Manchester United",
    "منچستر سیتی": "🔵 منچستر سیتی",
    "Manchester City": "🔵 Manchester City",
    "رئال مادرید": "🇪🇸 رئال مادرید",
    "Real Madrid": "🇪🇸 Real Madrid",
    "بارسلونا": "🇪🇸 بارسلونا",
    "Barcelona": "🇪🇸 Barcelona",
    "لیورپول": "🔴 لیورپول",
    "Liverpool": "🔴 Liverpool",
    "آرسنال": "🔴 آرسنال",
    "Arsenal": "🔴 Arsenal",
    "بایرن مونیخ": "🇩🇪 بایرن مونیخ",
    "Bayern Munich": "🇩🇪 Bayern Munich",
}


# =====================================
# Filters
# =====================================
VIDEO_WORDS = ["هایلایت", "highlights", "کلیپ", "ویدیو", "ویدئو", "watch video", "live stream"]
NEWS_WORDS = ["اعلام", "گزارش", "نتیجه", "قرارداد", "انتقال", "مصدومیت", "ترکیب"]


# =====================================
# Main Functions
# =====================================
def detect_sport(title: str = "", summary: str = "") -> Dict:
    text = f"{title} {summary}".lower()
    scores = {sport: sum(1 for kw in data["keywords"] if kw.lower() in text) 
              for sport, data in SPORTS.items()}

    best = max(scores, key=scores.get)
    return SPORTS[best] if scores[best] > 0 else {
        "name": "ورزش", "emoji": "🏆", "hashtag": "#ورزش"
    }


def add_team_flags(text: str) -> str:
    if not text:
        return ""
    for team, flagged in TEAM_FLAGS.items():
        text = text.replace(team, flagged)
    return text


def is_video_only(title: str = "", summary: str = "") -> bool:
    text = f"{title} {summary}".lower()
    has_video = any(word in text for word in VIDEO_WORDS)
    has_news = any(word in text for word in NEWS_WORDS)
    return has_video and not has_news


def detect_match_result(text: str) -> Dict:
    score = re.search(r"\d+\s*[-–]\s*\d+", text)
    return {"score": f"⚽ نتیجه: {score.group()}"} if score else {}


# =====================================
# Final Formatter
# =====================================
def format_sport_news(title: str = "", summary: str = "") -> Dict:
    if is_video_only(title, summary):
        return {"blocked": True, "title": title, "summary": summary}

    sport_info = detect_sport(title, summary)

    title = add_team_flags(title)
    summary = add_team_flags(summary)

    events = detect_match_result(f"{title} {summary}")

    return {
        "blocked": False,
        "sport": sport_info,
        "title": title,
        "summary": summary,
        "events": events
    }
