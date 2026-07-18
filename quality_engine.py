"""
KhabarF24 Quality Engine v2.0

News Quality Control

هماهنگ با:
- category_engine v7
- category_hashtags.py
- ai_processor v7
- sport_formatter v5

Features:
- Quality score
- Advertisement filtering
- Brand English protection
- Sport news support
- Breaking news support
- AI summary support
"""


import re



print("🧪 KhabarF24 Quality Engine v2.0 Loaded")



# =========================
# Limits
# =========================


MIN_TITLE_LENGTH = 8

MIN_SUMMARY_LENGTH = 20




# =========================
# Allowed English
# =========================


ALLOWED_ENGLISH = [

    # Technology

    "OpenAI",
    "ChatGPT",
    "Google",
    "Apple",
    "Microsoft",
    "Tesla",
    "NVIDIA",
    "AI",


    # Sport

    "Manchester United",
    "Manchester City",
    "Real Madrid",
    "Barcelona",
    "Liverpool",
    "Arsenal",

    "FIFA",
    "UEFA",
    "NBA",
    "Formula 1",

    "BBC Sport",

]






# =========================
# Bad Translation
# =========================


BAD_PHRASES = [

    "این متن",

    "یک اندازه",

    "می باشد",

    "به پایان می دهد",

    "مورد حمله قرار داد",

    "در این مقاله",

    "برای اطلاعات بیشتر",

]





# =========================
# Advertisement
# =========================


ADVERTISEMENT_WORDS = [

    "خرید",

    "فروش",

    "تخفیف",

    "جایزه",

    "ثبت نام",

    "اسپانسر",

    "تبلیغات",

    "رایگان",

    "کد تخفیف",

    "همین حالا",

    "تماس بگیرید",

    "عضویت",

]







# =========================
# Helpers
# =========================


def normalize(text):

    if not text:

        return ""

    return text.lower()






def remove_allowed_english(text):


    for word in ALLOWED_ENGLISH:

        text = text.replace(

            word,

            ""

        )


    return text






def contains_bad_english(text):


    if not text:

        return False



    clean = remove_allowed_english(

        text

    )



    english_words = re.findall(

        r"[A-Za-z]{4,}",

        clean

    )



    return len(english_words) >= 3







def contains_bad_phrase(text):


    text = normalize(text)


    for phrase in BAD_PHRASES:

        if phrase in text:

            return True


    return False







def is_advertisement(text):


    text = normalize(text)


    count = 0



    for word in ADVERTISEMENT_WORDS:


        if word in text:

            count += 1



    return count >= 2







# =========================
# Quality Score
# =========================


def calculate_quality(

        title,

        summary,

        category="world"

):


    score = 100



    text = f"{title} {summary}"





    # ---------------------
    # Title
    # ---------------------


    if not title:


        score -= 40



    elif len(title) < MIN_TITLE_LENGTH:


        score -= 10







    # ---------------------
    # Summary
    # ---------------------


    if not summary:


        # خبر فوری می‌تواند خلاصه نداشته باشد

        if category != "politics":

            score -= 15



    elif len(summary) < MIN_SUMMARY_LENGTH:


        score -= 5






    # ---------------------
    # Advertisement
    # ---------------------


    if is_advertisement(text):

        score -= 40






    # ---------------------
    # Bad AI Translation
    # ---------------------


    if contains_bad_phrase(text):

        score -= 15






    # ---------------------
    # Broken English
    # ---------------------


    if contains_bad_english(text):

        score -= 10







    # ---------------------
    # Too Short
    # ---------------------


    if len(text) < 40:


        if category not in [

            "sport",

            "politics"

        ]:

            score -= 15





    # limit

    if score < 0:

        score = 0



    return score







# =========================
# Final Check
# =========================


def is_high_quality(

        title,

        summary,

        category="world",

        minimum=50

):


    score = calculate_quality(

        title,

        summary,

        category

    )



    print(

        f"🧪 Quality Score: {score}/100"

    )



    return score >= minimum
