"""
KhabarF24 Game Rules v1.0

تشخیص اخبار گیم:
- بازی‌ها
- کنسول‌ها
- شرکت‌های بازی‌سازی
- آپدیت‌ها
- انتشار بازی
"""


GAME_KEYWORDS = [

    # Consoles

    "playstation",
    "ps5",
    "ps4",
    "xbox",
    "nintendo",

    "پلی استیشن",
    "ایکس باکس",
    "نینتندو",
    "کنسول",


    # Games

    "call of duty",
    "warzone",
    "minecraft",
    "fortnite",
    "gta",
    "grand theft auto",

    "کال آف دیوتی",
    "وارزون",
    "ماینکرفت",
    "فورتنایت",
    "جی تی ای",


    # Companies

    "ubisoft",
    "electronic arts",
    "ea games",
    "rockstar",
    "valve",
    "steam",

    "یوبی سافت",
    "راک‌استار",
    "استیم",


    # News

    "game",
    "gaming",
    "video game",

    "بازی",
    "گیم",
    "بازی ویدیویی",
    "بازی رایانه‌ای",

]



def detect_game(title, summary=""):

    text = f"{title} {summary}".lower()


    for word in GAME_KEYWORDS:

        if word.lower() in text:

            return True


    return False
