"""
KhabarF24 Quality Engine v1.0

بررسی کیفیت خبر قبل از انتشار:

- متن ناقص نباشد
- انگلیسی باقی نمانده باشد
- تیتر معتبر باشد
- خلاصه کافی باشد
- امتیاز کیفیت بدهد
"""


import re



# حداقل طول‌ها

MIN_TITLE_LENGTH = 15
MIN_SUMMARY_LENGTH = 40



# کلمات انگلیسی که اگر در متن فارسی باقی بمانند مشکل هستند

BAD_ENGLISH_WORDS = [

    "the",
    "is",
    "are",
    "has",
    "have",
    "with",
    "from",
    "and",
    "to",
    "of",
    "in",

]



# عبارت‌های خراب ترجمه ماشینی

BAD_PHRASES = [

    "مورد حمله قرار داد",

    "به پایان می دهد",

    "می باشد",

    "این متن",

    "یک اندازه",

    "شرط خود را",

]





def contains_english(text):

    if not text:
        return False


    words = re.findall(
        r"[A-Za-z]{3,}",
        text
    )


    for word in words:

        if word.lower() in BAD_ENGLISH_WORDS:

            return True


    return False





def check_bad_phrases(text):

    if not text:
        return False


    for phrase in BAD_PHRASES:

        if phrase in text:

            return True


    return False





def calculate_quality(title, summary):

    score = 100



    # =====================
    # تیتر
    # =====================

    if not title:

        score -= 40


    elif len(title) < MIN_TITLE_LENGTH:

        score -= 20



    # =====================
    # خلاصه
    # =====================

    if not summary:

        score -= 40


    elif len(summary) < MIN_SUMMARY_LENGTH:

        score -= 20



    text = f"{title} {summary}"



    # =====================
    # انگلیسی باقی مانده
    # =====================

    if contains_english(text):

        score -= 20



    # =====================
    # ترجمه بد
    # =====================

    if check_bad_phrases(text):

        score -= 15



    # محدود کردن امتیاز

    if score < 0:

        score = 0


    return score





def is_high_quality(title, summary, minimum=75):

    score = calculate_quality(
        title,
        summary
    )


    print(
        f"🧪 Quality Score: {score}/100"
    )


    return score >= minimum
