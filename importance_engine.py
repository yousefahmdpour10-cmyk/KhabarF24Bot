"""
KhabarF24 Importance Engine v3.1

Smart importance scoring

Features:
- Category based weights
- Sport dedicated engine
- Disaster detection
- Mass casualty detection
- Crisis detection
"""


from sport_rules import calculate_sport_score





IMPORTANCE_WORDS = {


    # 🔴 Politics / Security

    "politics": [

        "جنگ",
        "حمله",
        "حمله هوایی",
        "حمله موشکی",
        "موشک",
        "پهپاد",

        "هسته‌ای",
        "هسته ای",
        "اتمی",

        "تحریم",
        "مذاکرات",
        "توافق",
        "آتش بس",

        "بحران",
        "درگیری",
        "عملیات نظامی",

        "اعدام",
        "بازداشت",
        "دستگیری",
        "زندانی",

        "اخراج",
        "برکناری",
        "استعفا",
        "کناره گیری",

        "انتخابات",

        "رئیس جمهور",
        "رئیس‌جمهور",

        "وزیر دفاع",
        "وزیر خارجه",

        "پارلمان",

        "ترور",
        "انفجار",

    ],



    # 💰 Economy

    "economy": [

        "بیت کوین",
        "bitcoin",
        "کریپتو",

        "دلار",
        "ارز",
        "یورو",

        "طلا",

        "نفت",
        "گاز",

        "بورس",
        "سهام",

        "تورم",
        "اقتصاد",

        "بانک",

        "ورشکستگی",

        "سرمایه گذاری",

        "نرخ بهره",

        "رکود",

    ],




    # 💻 Technology

    "technology": [

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

        "تسلا",

        "ربات",

        "تراشه",
        "چیپ",

        "هک",
        "امنیت سایبری",

    ],





    # 🌧 Weather / Disaster

    "weather": [

        "طوفان",
        "سیل",
        "زلزله",

        "سونامی",

        "هشدار قرمز",
        "هشدار نارنجی",

        "موج گرما",
        "سرمای شدید",

        "بارش شدید",
        "برف سنگین",

        "گرد و غبار",

        "فاجعه طبیعی",

    ],




    # 🏥 Health

    "health": [

        "ویروس",
        "بیماری",
        "واکسن",

        "همه گیری",

        "سلامت",

        "پزشکی",

        "بیمارستان",

    ],


}





# خبرهای خیلی مهم

HIGH_IMPACT_WORDS = [


    "صدها کشته",

    "هزاران کشته",

    "بیش از 100 کشته",

    "بیش از 500 کشته",

    "کشته برجای گذاشت",

    "تلفات سنگین",

    "فاجعه انسانی",

    "فاجعه مرگبار",

    "غرق شدن",

    "واژگونی قایق",

    "مفقود شدن",

    "بحران انسانی",

    "وضعیت اضطراری",

]






def calculate_importance(
        title="",
        summary="",
        category=""
):


    text = f"{title} {summary}".lower()



    score = 2





    # ورزش جدا

    if category == "sport":


        return calculate_sport_score(

            title,

            summary

        )





    # موارد فوق مهم

    for word in HIGH_IMPACT_WORDS:


        if word.lower() in text:


            score += 5







    for cat, words in IMPORTANCE_WORDS.items():


        hits = 0


        for word in words:


            if word.lower() in text:

                hits += 1




        if hits:


            score += hits



            if cat == "politics":

                score += 2



            if cat in [

                "economy",

                "technology"

            ]:

                score += 1



            if cat == "weather":

                score += 2





    if score > 10:

        score = 10



    return round(score,1)








def is_important(
        title="",
        summary="",
        category="",
        minimum=7
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
