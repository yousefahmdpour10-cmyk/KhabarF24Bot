"""
KhabarF24 Quality Engine v1.1

بررسی کیفیت خبر قبل از انتشار

بهینه شده برای:
- اخبار کوتاه تلگرام
- ورزش
- فناوری
- منابع RSS
"""


import re



MIN_TITLE_LENGTH = 10
MIN_SUMMARY_LENGTH = 25




BAD_ENGLISH_WORDS = [

    "the",
    "is",
    "are",
    "has",
    "have",
    "with",
    "from",
    "and",
    "this",
    "that",

]





BAD_PHRASES = [

    "مورد حمله قرار داد",

    "به پایان می دهد",

    "می باشد",

    "این متن",

    "یک اندازه",

]





def contains_english(text):

    if not text:

        return False


    words = re.findall(

        r"\b[A-Za-z]{4,}\b",

        text

    )


    count = 0


    for word in words:


        if word.lower() in BAD_ENGLISH_WORDS:

            count += 1



    # فقط وقتی تعداد زیاد باشد مشکل است

    return count >= 2







def check_bad_phrases(text):

    if not text:

        return False


    for phrase in BAD_PHRASES:

        if phrase in text:

            return True


    return False







def calculate_quality(title, summary):


    score = 100



    # تیتر

    if not title:

        score -= 50


    elif len(title) < MIN_TITLE_LENGTH:

        score -= 10






    # خلاصه


    if not summary:

        score -= 25


    elif len(summary) < MIN_SUMMARY_LENGTH:

        score -= 10






    text = f"{title} {summary}"





    # انگلیسی خراب

    if contains_english(text):

        score -= 15





    # ترجمه ماشینی

    if check_bad_phrases(text):

        score -= 15





    # خبر خیلی کوتاه

    if len(text) < 50:

        score -= 20





    if score < 0:

        score = 0



    return score







def is_high_quality(title, summary, minimum=50):


    score = calculate_quality(

        title,

        summary

    )


    print(

        f"🧪 Quality Score: {score}/100"

    )



    return score >= minimum
