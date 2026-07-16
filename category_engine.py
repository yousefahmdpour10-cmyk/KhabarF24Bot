"""
KhabarF24 Category Engine v6.0

Smart News Category Detection

Priority:

1- Politics / Security 🔴
2- Iran 🇮🇷
3- World 🌍
4- Sport ⚽
5- Gaming 🎮
6- Technology 💻
7- Economy 💰
8- Health 🏥
9- Science 🔬
10- Weather 🌦
"""


print("🔥 KhabarF24 Category Engine v6.0 Loaded")



CATEGORIES = {



    # 🔴 سیاست و امنیت

    "politics": [

        "جنگ",
        "حمله",
        "حمله هوایی",
        "حمله موشکی",

        "موشک",
        "پهپاد",

        "ارتش",
        "نیروهای مسلح",
        "عملیات نظامی",

        "درگیری",
        "تنش",
        "بحران",

        "تحریم",

        "مذاکرات",
        "دیپلماسی",
        "توافق",
        "آتش بس",

        "انتخابات",

        "رئیس جمهور",
        "رئیس‌جمهور",

        "وزیر",
        "پارلمان",

        "بازداشت",
        "دستگیری",
        "اعدام",

        "ترور",
        "انفجار",

    ],



    # 🇮🇷 ایران

    "iran": [

        "ایران",
        "ایرانی",
        "تهران",

        "مجلس ایران",
        "دولت ایران",

        "وزارت کشور",

        "سپاه",
        "ارتش ایران",

    ],



    # 🌍 جهان

    "world": [

        "آمریکا",
        "بریتانیا",
        "روسیه",
        "اوکراین",
        "چین",
        "فرانسه",
        "آلمان",

        "جهان",

        "بین الملل",
        "بین‌الملل",

    ],




    # ⚽ ورزش

    "sport": [

        "فوتبال",
        "football",
        "soccer",

        "فیفا",
        "fifa",

        "یوفا",
        "uefa",

        "جام جهانی",

        "لیگ قهرمانان",

        "premier league",
        "la liga",
        "serie a",
        "bundesliga",

        "گل",
        "گلزنی",

        "بازیکن",
        "مربی",
        "سرمربی",

        "ترکیب",

        "مسی",
        "رونالدو",
        "امباپه",
        "هالند",
        "یامال",

        "منچستر یونایتد",
        "رئال مادرید",
        "بارسلونا",

        "بسکتبال",
        "nba",

        "والیبال",

        "تنیس",

        "کشتی",

        "فرمول یک",

        "ufc",

    ],




    # 🎮 گیم

    "gaming": [

        "gaming",
        "game",

        "گیم",
        "بازی ویدیویی",
        "بازی رایانه‌ای",

        "پلی استیشن",
        "playstation",

        "ایکس باکس",
        "xbox",

        "نینتندو",
        "nintendo",

        "استیم",
        "steam",

        "یوبی سافت",
        "ubisoft",

        "الکترونیک آرتز",

        "call of duty",
        "warzone",

        "minecraft",

        "fortnite",

        "کنسول",

    ],




    # 💻 فناوری

    "technology": [

        "فناوری",
        "تکنولوژی",
        "technology",

        "هوش مصنوعی",
        "artificial intelligence",
        "ai",

        "openai",
        "chatgpt",

        "گوگل",
        "google",

        "اپل",
        "apple",

        "مایکروسافت",
        "microsoft",

        "متا",
        "meta",

        "انویدیا",
        "nvidia",

        "تسلا",
        "tesla",

        "ربات",

        "تراشه",
        "چیپ",

        "هک",

        "امنیت سایبری",

    ],




    # 💰 اقتصاد

    "economy": [

        "اقتصاد",

        "دلار",

        "ارز",

        "یورو",

        "طلا",

        "نفت",

        "گاز",

        "بورس",

        "سهام",

        "تورم",

        "بانک",

        "نرخ بهره",

        "بیت کوین",

        "bitcoin",

        "کریپتو",

    ],




    # 🏥 سلامت

    "health": [

        "سلامت",

        "بیماری",

        "ویروس",

        "واکسن",

        "پزشکی",

        "بیمارستان",

        "دارو",

    ],




    # 🔬 علم

    "science": [

        "علم",

        "science",

        "تحقیق",

        "فضا",

        "ناسا",

        "nasa",

    ],




    # 🌦 هواشناسی

    "weather": [

        "هواشناسی",

        "weather",

        "طوفان",

        "سیل",

        "زلزله",

        "بارندگی",

        "برف",

        "گرما",

        "سرمای شدید",

    ],


}







CATEGORY_PRIORITY = [

    "politics",

    "iran",

    "world",

    "sport",

    "gaming",

    "technology",

    "economy",

    "health",

    "science",

    "weather",

]







def detect_smart_category(title="", summary="", source=""):


    text = f"""

    {title}

    {summary}

    {source}

    """.lower()



    scores = {}



    for category, keywords in CATEGORIES.items():


        score = 0


        for word in keywords:


            if word.lower() in text:

                score += 1



        scores[category] = score





    for category in CATEGORY_PRIORITY:


        if scores.get(category, 0) > 0:

            return category





    return "world"
