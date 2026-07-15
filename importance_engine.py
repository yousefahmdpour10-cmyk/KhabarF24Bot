"""
KhabarF24 Importance Engine v1.0

هدف:
- تشخیص اهمیت خبر
- جلوگیری از انتشار خبرهای کم‌ارزش
- امتیازدهی از 1 تا 10

بدون نیاز به API
"""


import re





# =====================
# کلیدواژه‌های مهم
# =====================


HIGH_IMPORTANCE = [

    # جنگ و امنیت

    "war",
    "attack",
    "missile",
    "drone",
    "invasion",
    "military",
    "strike",
    "nuclear",
    "terror",
    "conflict",


    # سیاست

    "president",
    "prime minister",
    "election",
    "government",
    "parliament",
    "sanction",
    "treaty",
    "agreement",


    # اقتصاد

    "crash",
    "market",
    "inflation",
    "bank",
    "oil",
    "energy",


    # حوادث بزرگ

    "earthquake",
    "flood",
    "storm",
    "disaster",


    # فناوری مهم

    "artificial intelligence",
    "ai",
    "chip",
    "cyber attack",

]





MEDIUM_IMPORTANCE = [

    "company",

    "business",

    "research",

    "technology",

    "sports",

    "match",

]





LOW_IMPORTANCE = [

    "celebrity",

    "movie",

    "entertainment",

    "fashion",

    "lifestyle",

]







def calculate_importance(title="", summary=""):


    text = f"""
    {title}
    {summary}
    """.lower()



    score = 5



    # =====================
    # موارد مهم
    # =====================


    for word in HIGH_IMPORTANCE:


        if word in text:

            score += 1





    # =====================
    # موارد متوسط
    # =====================


    for word in MEDIUM_IMPORTANCE:


        if word in text:

            score += 0.3





    # =====================
    # موارد کم اهمیت
    # =====================


    for word in LOW_IMPORTANCE:


        if word in text:

            score -= 1





    # محدود کردن

    if score > 10:

        score = 10


    if score < 1:

        score = 1



    return round(score,1)







def is_important(title="", summary="", minimum=7):


    score = calculate_importance(

        title,

        summary

    )


    print(

        f"🔥 Importance Score: {score}/10"

    )


    return score >= minimum
