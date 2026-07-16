"""
KhabarF24 Category Engine v6.1

Smart Category Detection

Priority:

1- Politics / Security 🔴
2- Iran 🇮🇷
3- World 🌍
4- Sport ⚽
5- Technology 💻
6- Gaming 🎮
7- Economy 💰
8- Health 🏥
9- Science 🔬
10- Weather 🌦
"""


print("🔥 KhabarF24 Category Engine v6.1 Loaded")



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

        "مسی",
        "رونالدو",
        "امباپه",
        "هالند",
        "یامال",

        "منچستر یونایتد",
        "رئال مادرید",
        "بارسلونا",

        "nba",
        "بسکتبال",
        "والیبال",
        "تنیس",
        "کشتی",
        "فرمول یک",

    ],



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
        "بازی رایانه‌ای",

        "playstation",
        "پلی استیشن",

        "xbox",
        "ایکس باکس",

        "nintendo",
        "نینتندو",

        "steam",
        "استیم",

        "ubisoft",

        "call of duty",

        "warzone",

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

    "politics",

    "iran",

    "world",

    "sport",

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
