"""
KhabarF24 Category Engine v6.2

Smart Category Detection

Priority:

1- Sport ⚽
2- Politics / Security 🔴
3- Iran 🇮🇷
4- World 🌍
5- Technology 💻
6- Gaming 🎮
7- Economy 💰
8- Health 🏥
9- Science 🔬
10- Weather 🌦
"""


print("🔥 KhabarF24 Category Engine v6.2 Loaded")



CATEGORIES = {


    "politics": [

        "جنگ",
        "حمله",
        "حمله هوایی",
        "حمله موشکی",

        "موشک",
        "پهپاد",

        "ارتش",
        "نظامی",
        "عملیات نظامی",

        "درگیری",
        "تنش",
        "بحران",

        "تحریم",

        "مذاکرات",
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



    "iran": [

        "ایران",
        "ایرانی",

        "تهران",

        "دولت ایران",

        "مجلس ایران",

        "سپاه",

        "رئیس جمهور ایران",

    ],




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




    "sport": [

        # فوتبال

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

        "نتیجه",

        "ترکیب",

        "کارت زرد",
        "کارت قرمز",

        "مصدومیت",

        "بازیکن",

        "مربی",
        "سرمربی",


        # بازیکنان معروف

        "مسی",
        "رونالدو",
        "امباپه",
        "هالند",
        "یامال",


        # تیم ها

        "منچستر یونایتد",
        "رئال مادرید",
        "بارسلونا",
        "لیورپول",
        "آرسنال",


        # رشته ها

        "nba",

        "بسکتبال",
        "basketball",

        "والیبال",
        "volleyball",

        "تنیس",
        "tennis",

        "کشتی",

        "فرمول یک",
        "formula 1",
        "f1",

    ],





    "technology": [

        "فناوری",

        "تکنولوژی",

        "technology",

        "هوش مصنوعی",

        "artificial intelligence",

        "openai",

        "chatgpt",

        "گوگل",

        "google",

        "اپل",

        "apple",

        "مایکروسافت",

        "microsoft",

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





    "gaming": [

        "گیم",

        "gaming",

        "game",

        "بازی ویدیویی",

        "پلی استیشن",

        "playstation",

        "ایکس باکس",

        "xbox",

        "نینتندو",

        "nintendo",

        "steam",

        "استیم",

        "ubisoft",

        "call of duty",

        "minecraft",

        "fortnite",

        "کنسول",

    ],





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

        "بیت کوین",

        "bitcoin",

        "کریپتو",

    ],




    "health": [

        "سلامت",

        "بیماری",

        "ویروس",

        "واکسن",

        "پزشکی",

        "بیمارستان",

        "دارو",

    ],




    "science": [

        "علم",

        "science",

        "تحقیق",

        "فضا",

        "ناسا",

        "nasa",

    ],





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

    "sport",

    "politics",

    "iran",

    "world",

    "technology",

    "gaming",

    "economy",

    "health",

    "science",

    "weather",

]







def detect_smart_category(

        title="",

        summary="",

        source=""

):


    # فقط تیتر و خلاصه
    # منبع حذف شد

    text = f"""

    {title}

    {summary}

    """.lower()






    scores = {}



    for category, keywords in CATEGORIES.items():


        score = 0


        for word in keywords:


            if word.lower() in text:

                score += 1


        scores[category] = score






    # =========================
    # ورزش قوی
    # =========================


    if scores["sport"] >= 2:

        return "sport"







    # =========================
    # سیاست قوی
    # =========================


    if scores["politics"] >= 1:

        return "politics"







    # =========================
    # بقیه دسته ها
    # =========================


    for category in CATEGORY_PRIORITY:


        if scores.get(category,0) > 0:

            return category





    return "world"
