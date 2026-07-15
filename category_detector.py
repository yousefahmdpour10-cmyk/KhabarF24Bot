"""
KhabarF24 Category Detector v2

تشخیص:
- جهان
- ایران
- ورزش
- فناوری
- اقتصاد
- سلامت
"""


def detect_category(source, title, summary=""):

    text = f"{source} {title} {summary}".lower()


    # ======================
    # 🏅 ورزش
    # ======================

    sport_words = [

        "fifa",
        "uefa",
        "football",
        "soccer",
        "premier league",
        "laliga",
        "serie a",
        "bundesliga",
        "champions league",
        "nba",
        "wnba",
        "tennis",
        "wrestling",
        "ufc",

        "منچستر",
        "رئال",
        "بارسلونا",
        "لیورپول",
        "آرسنال",
        "فوتبال",
        "بسکتبال",
        "جام جهانی",
        "لیگ",

    ]



    # ======================
    # 💻 فناوری
    # ======================

    tech_words = [

        "tech",
        "technology",
        "ai",
        "artificial intelligence",
        "openai",
        "apple",
        "google",
        "microsoft",
        "tesla",
        "nvidia",
        "iphone",
        "android",

        "هوش مصنوعی",
        "فناوری",
        "ربات",
        "تکنولوژی",

    ]



    # ======================
    # 💰 اقتصاد
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
        "ارز",
        "دلار",
        "طلا",

    ]



    # ======================
    # ❤️ سلامت
    # ======================

    health_words = [

        "health",
        "medicine",
        "hospital",
        "virus",
        "disease",

        "سلامت",
        "پزشکی",
        "بیماری",
        "واکسن",

    ]



    # ======================
    # 🇮🇷 ایران
    # ======================

    iran_words = [

        "iran",
        "iranian",
        "tehran",

        "ایران",
        "تهران",
        "ایرانی",

    ]



    # ======================
    # 🌍 جهان / سیاسی
    # ======================

    world_words = [

        "war",
        "attack",
        "missile",
        "strike",
        "trump",
        "biden",
        "israel",
        "ukraine",
        "russia",
        "china",
        "america",
        "united states",

        "جنگ",
        "حمله",
        "موشک",
        "ترامپ",
        "آمریکا",
        "اسرائیل",
        "روسیه",
        "چین",
        "تحریم",
        "سپاه",

    ]



    # ======================
    # اولویت بندی
    # ======================

    # ورزش و فناوری اگر واضح باشند
    for word in sport_words:
        if word in text:
            return "sport"


    for word in tech_words:
        if word in text:
            return "technology"



    for word in economy_words:
        if word in text:
            return "economy"



    for word in health_words:
        if word in text:
            return "health"



    # خبرهای سیاسی و جنگی همیشه جهان
    for word in world_words:
        if word in text:
            return "world"



    # ایران اگر سیاسی نبود
    for word in iran_words:
        if word in text:
            return "iran"



    return "world"
