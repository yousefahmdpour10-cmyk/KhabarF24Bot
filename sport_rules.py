"""
KhabarF24 Sport Rules v3.0

Sport Intelligence Engine

Features:
- Sport importance score
- Big match detection
- Match events
- Goals
- Cards
- Lineups
- Coach interviews
- Video-only filtering
"""





SPORT_EVENTS = {


    "score": [

        "نتیجه",

        "پایان بازی",

        "برنده",

        "پیروز شد",

        "باخت",

        "مساوی",

        "۰-",

        "1-",

        "2-",

    ],



    "goal": [

        "گل",

        "گلزن",

        "گلزنی",

        "هت تریک",

        "دقیقه",

    ],



    "cards": [

        "کارت زرد",

        "کارت قرمز",

        "اخراج",

    ],



    "lineup": [

        "ترکیب رسمی",

        "ترکیب اولیه",

        "lineup",

        "starting xi",

        "starting eleven",

    ],



    "interview": [

        "مصاحبه",

        "کنفرانس خبری",

        "صحبت‌های مربی",

        "اظهارات سرمربی",

    ],

}






BIG_TEAMS = [


    "منچستر یونایتد",

    "منچستر سیتی",

    "لیورپول",

    "آرسنال",

    "چلسی",

    "رئال مادرید",

    "بارسلونا",

    "بایرن مونیخ",

    "پاری سن ژرمن",

    "اینتر",

    "میلان",

    "یوونتوس",

    "آرژانتین",

    "برزیل",

    "فرانسه",

    "انگلیس",

]





BIG_COMPETITIONS = [


    "جام جهانی",

    "لیگ قهرمانان",

    "لیگ اروپا",

    "فینال",

    "دربی",

    "نیمه نهایی",

    "یک چهارم نهایی",

]






VIDEO_ONLY = [


    "هایلایت",

    "highlights",

    "watch video",

    "ویدیو",

    "کلیپ",

    "لحظات برتر",

]






def normalize(text):


    if not text:

        return ""


    return text.lower()






def contains_any(text, words):


    text = normalize(text)


    for word in words:


        if word.lower() in text:

            return True



    return False






def detect_events(title="", summary=""):


    text = f"{title} {summary}"



    result = []



    for event, words in SPORT_EVENTS.items():


        if contains_any(text, words):

            result.append(event)



    return result







def is_big_match(title="", summary=""):


    text = f"{title} {summary}"



    return (

        contains_any(text, BIG_TEAMS)

        or

        contains_any(text, BIG_COMPETITIONS)

    )








def is_video_only(title="", summary=""):


    text = f"{title} {summary}"



    return (

        contains_any(text, VIDEO_ONLY)

        and

        not detect_events(title, summary)

    )








def calculate_sport_score(title="", summary=""):


    score = 1



    events = detect_events(

        title,

        summary

    )




    if is_big_match(title, summary):

        score += 4





    if "score" in events:

        score += 3



    if "goal" in events:

        score += 2



    if "cards" in events:

        score += 2



    if "lineup" in events:

        score += 3



    if "interview" in events:

        score += 2





    if is_video_only(title, summary):


        return 0





    if score > 10:

        score = 10



    return score
