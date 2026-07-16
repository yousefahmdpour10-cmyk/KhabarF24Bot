"""
KhabarF24 Importance Engine v4.0

Priority:

1 Politics / Security 🔴
2 Iran 🇮🇷
3 World 🌍
4 Sport ⚽
5 Technology 💻
6 Gaming 🎮
7 Others
"""


from sport_rules import calculate_sport_score




CATEGORY_WEIGHTS = {


    "politics": 4,

    "iran": 3,

    "world": 2,

    "sport": 0,

    "technology": 1,

    "gaming": 1,

    "economy": 2,

    "weather": 3,

    "health": 2,

}





IMPORTANT_WORDS = {


    "politics": [

        "جنگ",

        "حمله",

        "موشک",

        "پهپاد",

        "عملیات نظامی",

        "درگیری",

        "بحران",

        "تحریم",

        "مذاکرات",

        "توافق",

        "آتش بس",

        "هسته‌ای",

        "هسته ای",

        "ترور",

        "انفجار",

        "کودتا",

        "انتخابات",

        "رئیس جمهور",

        "وزیر دفاع",

        "وزیر خارجه",

    ],



    "iran": [

        "ایران",

        "تهران",

        "دولت ایران",

        "مجلس",

        "سپاه",

    ],



    "world": [

        "آمریکا",

        "روسیه",

        "چین",

        "اوکراین",

        "اروپا",

        "بین‌الملل",

    ],



    "economy": [

        "دلار",

        "ارز",

        "طلا",

        "نفت",

        "بورس",

        "تورم",

        "بانک",

        "بیت کوین",

        "کریپتو",

    ],



    "technology": [

        "هوش مصنوعی",

        "openai",

        "chatgpt",

        "گوگل",

        "اپل",

        "مایکروسافت",

        "تراشه",

        "چیپ",

        "هک",

        "امنیت سایبری",

    ],



    "gaming": [

        "گیم",

        "بازی",

        "playstation",

        "xbox",

        "steam",

        "کنسول",

        "بازی ویدیویی",

    ],



    "weather": [

        "سیل",

        "زلزله",

        "طوفان",

        "سونامی",

        "هشدار قرمز",

        "فاجعه طبیعی",

    ],



    "health": [

        "ویروس",

        "بیماری",

        "واکسن",

        "همه گیری",

    ],


}





HIGH_IMPACT_WORDS = [


    "صدها کشته",

    "هزاران کشته",

    "تلفات سنگین",

    "فاجعه انسانی",

    "وضعیت اضطراری",

    "حمله گسترده",

    "جنگ آغاز شد",

    "حمله هسته‌ای",

    "زلزله شدید",

    "سیل مرگبار",

]





def calculate_importance(

        title="",

        summary="",

        category=""

):


    text = f"{title} {summary}".lower()



    score = 1





    # ورزش اختصاصی


    if category == "sport":


        return calculate_sport_score(

            title,

            summary

        )







    # دسته


    score += CATEGORY_WEIGHTS.get(

        category,

        0

    )






    # کلمات مهم


    for cat, words in IMPORTANT_WORDS.items():


        hits = 0


        for word in words:


            if word.lower() in text:

                hits += 1




        if hits:


            score += hits



            score += CATEGORY_WEIGHTS.get(

                cat,

                0

            )







    # خبرهای بحرانی


    for word in HIGH_IMPACT_WORDS:


        if word.lower() in text:


            score += 3







    if score > 10:


        score = 10



    return round(

        score,

        1

    )







def is_important(

        title="",

        summary="",

        category="",

        minimum=6

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
