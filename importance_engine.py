"""
KhabarF24 Importance Engine v5.0

News Importance Intelligence

هماهنگ با:
- category_engine v7
- category_hashtags.py
- sport_formatter v5
- quality_engine v2

Features:
- Breaking news detection
- Sport importance
- Football / Basketball / Tennis / Wrestling separation
- Technology priority
- Economy priority
- Weighted scoring
"""


print("🔥 KhabarF24 Importance Engine v5.0 Loaded")



# =========================
# Category Base Weights
# =========================


CATEGORY_WEIGHTS = {


    "politics": 4,

    "iran": 3,

    "world": 2,


    "football": 4,

    "basketball": 3,

    "volleyball": 3,

    "tennis": 3,

    "wrestling": 3,

    "formula1": 3,

    "combat": 3,


    "technology": 3,

    "gaming": 2,

    "economy": 3,

    "health": 2,

    "science": 2,

    "weather": 3,

}






# =========================
# Important Keywords
# =========================


IMPORTANT_WORDS = {


    "politics": [

        "جنگ",

        "حمله",

        "حمله موشکی",

        "حمله هوایی",

        "موشک",

        "پهپاد",

        "ارتش",

        "عملیات نظامی",

        "درگیری",

        "بحران",

        "تحریم",

        "مذاکرات",

        "توافق",

        "آتش بس",

        "دیپلماسی",

        "انتخابات",

        "ترور",

        "انفجار",

    ],



    "iran": [

        "ایران",

        "تهران",

        "دولت",

        "مجلس",

        "وزارت",

        "سپاه",

    ],



    "world": [

        "آمریکا",

        "روسیه",

        "چین",

        "اروپا",

        "اوکراین",

        "سازمان ملل",

    ],




    # =================
    # Sports
    # =================


    "football": [

        "فوتبال",

        "گل",

        "هتریک",

        "قهرمانی",

        "فینال",

        "لیگ قهرمانان",

        "جام جهانی",

        "بازیکن",

        "مربی",

        "مصدومیت",

        "انتقال",

        "قرارداد",

        "VAR",

    ],



    "basketball": [

        "بسکتبال",

        "NBA",

        "WNBA",

        "دانک",

        "ریباند",

        "سه امتیازی",

        "قهرمانی NBA",

    ],



    "volleyball": [

        "والیبال",

        "FIVB",

        "ست",

        "اسپک",

        "سرویس",

    ],



    "tennis": [

        "تنیس",

        "ATP",

        "WTA",

        "گرند اسلم",

        "ویمبلدون",

        "رولان گاروس",

        "جوکوویچ",

    ],



    "wrestling": [

        "کشتی",

        "کشتی آزاد",

        "کشتی فرنگی",

        "UWW",

        "مدال",

        "قهرمانی جهان",

    ],



    "formula1": [

        "فرمول یک",

        "F1",

        "Formula 1",

        "گرندپری",

        "ردبول",

        "فراری",

    ],




    # =================
    # Technology
    # =================


    "technology": [

        "فناوری",

        "تکنولوژی",

        "هوش مصنوعی",

        "AI",

        "OpenAI",

        "ChatGPT",

        "گوگل",

        "اپل",

        "مایکروسافت",

        "انویدیا",

        "تراشه",

        "چیپ",

        "ربات",

        "هک",

        "امنیت سایبری",

    ],




    "economy": [

        "دلار",

        "ارز",

        "طلا",

        "نفت",

        "تورم",

        "بورس",

        "بانک",

        "کریپتو",

        "بیت کوین",

    ],

}






# =========================
# High Impact
# =========================


HIGH_IMPACT_WORDS = [


    "خبر فوری",

    "فوری",

    "لحظاتی قبل",

    "اکنون",

    "کشته",

    "تلفات",

    "فاجعه",

    "وضعیت اضطراری",

    "حمله گسترده",

    "جنگ آغاز شد",

    "رکورد تاریخی",

    "قهرمان شد",

    "قهرمانی جهان",

    "رکورد جهانی",

]






# =========================
# Helpers
# =========================


def contains_any(text, words):


    text = text.lower()


    for word in words:

        if word.lower() in text:

            return True


    return False






# =========================
# Score Engine
# =========================


def calculate_importance(

        title="",

        summary="",

        category="world"

):


    text = f"{title} {summary}".lower()


    score = 1





    # دسته اصلی

    score += CATEGORY_WEIGHTS.get(

        category,

        0

    )







    # کلمات مرتبط

    for cat, words in IMPORTANT_WORDS.items():


        hits = 0


        for word in words:


            if word.lower() in text:

                hits += 1



        if hits:


            score += hits



            # تقویت دسته خودش

            if cat == category:

                score += 2






    # خبر مهم

    for word in HIGH_IMPACT_WORDS:


        if word.lower() in text:

            score += 3






    # محدود کردن

    if score > 10:

        score = 10



    return round(score,1)







# =========================
# Final Check
# =========================


def is_important(

        title="",

        summary="",

        category="world",

        minimum=5

):


    score = calculate_importance(

        title,

        summary,

        category

    )



    print(

        f"🔥 Importance Score: {score}/10"

    )



    return score >= minimum
