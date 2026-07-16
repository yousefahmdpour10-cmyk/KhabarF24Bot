"""
KhabarF24 Game Rules v1.0

تشخیص خبرهای گیمینگ
"""

GAME_KEYWORDS = [

    # کنسول
    "playstation",
    "ps5",
    "ps4",
    "xbox",
    "nintendo",
    "switch",

    # شرکت‌ها
    "sony",
    "سونی",
    "microsoft",
    "مایکروسافت",
    "ubisoft",
    "یوبی‌سافت",
    "electronic arts",
    "ea sports",
    "valve",
    "steam",

    # بازی‌ها
    "call of duty",
    "warzone",
    "minecraft",
    "fortnite",
    "gta",
    "grand theft auto",
    "elder scrolls",
    "fifa",
    "fc 25",
    "fc 26",

    # فارسی
    "گیم",
    "بازی ویدیویی",
    "بازی رایانه‌ای",
    "کنسول بازی",
    "گیمر",
    "استودیو بازی",
    "سازنده بازی",
    "آپدیت بازی",
    "نسخه جدید بازی",

]


def detect_game(title, summary=""):

    text = f"{title} {summary}".lower()


    for word in GAME_KEYWORDS:

        if word.lower() in text:

            return True


    return False
