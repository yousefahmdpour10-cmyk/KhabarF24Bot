"""
KhabarF24 Category Detector v3.0

Smart Category Detection

Priority:

1- Sport
2- Gaming
3- Technology
4- Economy
5- Health
6- Science
7- Weather
8- Iran
9- World
"""


def contains_any(text, words):

    text = text.lower()


    for word in words:

        if word.lower() in text:

            return True


    return False





def detect_category(source, title, summary=""):


    text = f"""
    {source}
    {title}
    {summary}
    """.lower()





    # ======================
    # ⚽ SPORT
    # ======================


    sport_words = [

        "fifa",
        "uefa",
        "football",
        "soccer",

        "champions league",

        "premier league",

        "la liga",

        "serie a",

        "bundesliga",

        "nba",
        "wnba",

        "tennis",

        "ufc",

        "فوتبال",
        "بسکتبال",
        "تنیس",
        "کشتی",

        "مسی",
        "رونالدو",

        "منچستر یونایتد",
        "رئال مادرید",
        "بارسلونا",

        "جام جهانی",

        "گلزنی",
        "بازیکن",
        "مربی",

    ]



    if contains_any(text, sport_words):

        return "sport"






    # ======================
    # 🎮 GAMING
    # ======================


    gaming_words = [

        "playstation",

        "xbox",

        "nintendo",

        "steam",

        "ubisoft",

        "call of duty",

        "warzone",

        "minecraft",

        "fortnite",

        "بازی ویدیویی",

        "گیم",

        "بازی رایانه‌ای",

        "کنسول",

    ]



    if contains_any(text, gaming_words):

        return "gaming"







    # ======================
    # 💻 TECHNOLOGY
    # ======================


    tech_words = [

        "technology",

        "tech",

        "artificial intelligence",

        "openai",

        "chatgpt",

        "google",

        "apple",

        "microsoft",

        "nvidia",

        "tesla",

        "robot",

        "chip",

        "software",

        "هوش مصنوعی",

        "فناوری",

        "تکنولوژی",

        "ربات",

        "تراشه",

        "نرم افزار",

        "امنیت سایبری",

    ]



    if contains_any(text, tech_words):

        return "technology"







    # ======================
    # 💰 ECONOMY
    # ======================


    economy_words = [

        "economy",

        "market",

        "stock",

        "bitcoin",

        "crypto",

        "inflation",

        "oil",

        "اقتصاد",

        "بورس",

        "سهام",

        "دلار",

        "ارز",

        "طلا",

        "نفت",

        "تورم",

    ]



    if contains_any(text, economy_words):

        return "economy"







    # ======================
    # ❤️ HEALTH
    # ======================


    health_words = [

        "health",

        "medicine",

        "hospital",

        "virus",

        "vaccine",

        "سلامت",

        "پزشکی",

        "بیماری",

        "واکسن",

        "بیمارستان",

    ]



    if contains_any(text, health_words):

        return "health"







    # ======================
    # 🔬 SCIENCE
    # ======================


    science_words = [

        "science",

        "nasa",

        "space",

        "research",

        "علم",

        "فضا",

        "ناسا",

        "تحقیق",

    ]



    if contains_any(text, science_words):

        return "science"







    # ======================
    # 🌦 WEATHER
    # ======================


    weather_words = [

        "weather",

        "storm",

        "flood",

        "earthquake",

        "هواشناسی",

        "طوفان",

        "سیل",

        "زلزله",

        "باران",

        "برف",

        "گرما",

    ]



    if contains_any(text, weather_words):

        return "weather"







    # ======================
    # 🇮🇷 IRAN
    # ======================


    iran_words = [

        "iran",

        "iranian",

        "tehran",

        "ایران",

        "ایرانی",

        "تهران",

        "مجلس ایران",

        "دولت ایران",

    ]



    if contains_any(text, iran_words):

        return "iran"







    # ======================
    # 🌍 WORLD
    # ======================


    return "world"
