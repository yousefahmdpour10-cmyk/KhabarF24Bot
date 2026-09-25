"""
دسته‌های اصلی اخبار
"""

from enum import Enum


class Category(str, Enum):
    """
    دسته‌های اصلی اخبار KhabarF24
    """

    BREAKING = "breaking"          # خبر فوری
    WORLD = "world"                # جهان
    IRAN = "iran"                  # ایران
    POLITICS = "politics"          # سیاست
    ECONOMY = "economy"            # اقتصاد
    TECHNOLOGY = "technology"      # فناوری
    SPORTS = "sports"              # ورزش
    HEALTH = "health"              # سلامت
    SCIENCE = "science"            # علم
    WEATHER = "weather"            # هواشناسی
    CULTURE = "culture"            # فرهنگ
    ART = "art"                    # هنر
    CINEMA = "cinema"              # سینما
    MUSIC = "music"                # موسیقی
    GAMING = "gaming"              # بازی
    EDUCATION = "education"        # آموزش
    ENVIRONMENT = "environment"    # محیط زیست
    CRIME = "crime"                # حوادث
    MILITARY = "military"          # نظامی
    SPACE = "space"                # فضا
    OTHER = "other"                # سایر
