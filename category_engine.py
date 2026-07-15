"""
KhabarF24 Category Engine v4.0

تشخیص هوشمند دسته خبر

اولویت:
1- ورزش
2- فناوری
3- اقتصاد
4- سلامت
5- علم
6- هواشناسی
7- ایران
8- جهان
"""


CATEGORIES = {


    # ⚽ ورزش

    "sport": [

        # فوتبال

        "فوتبال",
        "football",
        "soccer",
        "fifa",
        "uefa",
        "جام جهانی",
        "world cup",

        "لیگ قهرمانان",
        "champions league",

        "فینال",
        "نیمه نهایی",
        "نیمه‌نهایی",

        "انگلیس",
        "آرژانتین",
        "برزیل",
        "فرانسه",
        "اسپانیا",

        "منچستر",
        "لیورپول",
        "آرسنال",
        "چلسی",
        "رئال مادرید",
        "بارسلونا",

        "مسی",
        "رونالدو",
        "امباپه",
        "یامال",

        # مسابقه

        "مسابقه",
        "بازی",
        "دقیقه",
        "گل",
        "گلزنی",
        "نتیجه",
        "امتیاز",
        "آمار",

        "بازیکن",
        "مربی",
        "داور",

        "کارت زرد",
        "کارت قرمز",

        # نقل و انتقالات

        "انتقال",
        "نقل و انتقالات",
        "قرارداد",
        "اخراج مربی",

        # سایر ورزش‌ها

        "nba",
        "بسکتبال",
        "تنیس",
        "والیبال",
        "کشتی",
        "المپیک",

    ],





    # 💻 فناوری

    "technology": [

        "فناوری",
        "technology",
        "تکنولوژی",

        "هوش مصنوعی",
        "artificial intelligence",
        "ai",

        "ربات",
        "تراشه",
        "چیپ",

        "اپل",
        "گوگل",
        "مایکروسافت",
        "openai",

        "هک",
        "امنیت سایبری",

    ],





    # 💰 اقتصاد

    "economy": [

        "اقتصاد",
        "economy",

        "دلار",
        "ارز",
        "یورو",
        "طلا",

        "بیت کوین",
        "bitcoin",
        "کریپتو",

        "بورس",
        "سهام",

        "تورم",
        "بانک",
        "نفت",

        "بازار",

    ],





    # 🏥 سلامت

    "health": [

        "سلامت",
        "health",
        "بیماری",
        "ویروس",
        "واکسن",
        "پزشکی",
        "بیمارستان",

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





    # 🌧 هواشناسی

    "weather": [

        "هواشناسی",
        "weather",
        "طوفان",
        "سیل",
        "زلزله",
        "باران",
        "برف",
        "موج گرما",

    ],





    # 🇮🇷 ایران

    "iran": [

        "ایران",
        "تهران",
        "اصفهان",
        "شیراز",

    ],

}





CATEGORY_PRIORITY = [

    "sport",

    "technology",

    "economy",

    "health",

    "science",

    "weather",

    "iran",

    "world",

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






    # اولویت دسته‌ها

    for category in CATEGORY_PRIORITY:


        if scores.get(category,0) > 0:

            return category





    return "world"
