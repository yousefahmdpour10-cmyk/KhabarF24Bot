"""
KhabarF24 Importance Engine v4.1

بهینه شده برای:
- خبر فوری
- ورزش
- فناوری
- تلگرام

"""

from sport_rules import calculate_sport_score



CATEGORY_WEIGHTS = {

    "politics": 4,

    "iran": 3,

    "world": 2,

    "sport": 3,

    "technology": 2,

    "gaming": 2,

    "economy": 3,

    "weather": 3,

    "health": 2,

    "science": 2,

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
        "ترور",
        "انفجار",
        "انتخابات",

    ],


    "iran": [

        "ایران",
        "تهران",
        "دولت",
        "مجلس",
        "سپاه",

    ],


    "world": [

        "آمریکا",
        "روسیه",
        "چین",
        "اوکراین",
        "اروپا",

    ],


    "sport": [

        "برد",
        "باخت",
        "پیروزی",
        "قهرمانی",
        "رکورد",
        "گل",
        "مصدومیت",
        "انتقال",
        "قرارداد",
        "بازیکن",
        "مربی",
        "لیگ",
        "فینال",
        "جام",

    ],


    "technology": [

        "هوش مصنوعی",
        "openai",
        "chatgpt",
        "گوگل",
        "اپل",
        "مایکروسافت",
        "تراشه",
        "هک",

    ],


    "gaming": [

        "گیم",
        "بازی",
        "پلی استیشن",
        "xbox",
        "کنسول",

    ],


    "economy": [

        "دلار",
        "ارز",
        "طلا",
        "نفت",
        "تورم",
        "بورس",

    ],


}





HIGH_IMPACT_WORDS = [

    "کشته",

    "تلفات",

    "فاجعه",

    "وضعیت اضطراری",

    "حمله گسترده",

    "جنگ آغاز شد",

    "رکورد تاریخی",

    "قهرمان شد",

]






def calculate_importance(title="", summary="", category=""):


    text = f"{title} {summary}".lower()


    score = 1



    # ورزش

    if category == "sport":


        sport_score = calculate_sport_score(

            title,

            summary

        )


        # حداقل ارزش برای ورزش

        return max(

            sport_score,

            6

        )





    # امتیاز دسته

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







    # تاثیر بالا

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
