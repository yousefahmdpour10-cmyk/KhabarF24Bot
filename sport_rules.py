"""
KhabarF24 Sport Rules v4.0

Sport Intelligence Engine

Features:
- Detect sport type
- Sport emoji
- Sport hashtag
- Big match detection
- Match events
- Goals
- Cards
- Lineups
- Coach interviews
- Video-only filtering
- Importance score
"""


# =========================
# 🏅 Sport Types
# =========================


SPORT_TYPES = {

    "football": {

        "title": "فوتبال",
        "emoji": "⚽",
        "hashtag": "#فوتبال",

        "keywords": [

            "فوتبال",
            "football",
            "soccer",

            "فیفا",
            "fifa",

            "یوفا",
            "uefa",

            "جام جهانی",
            "world cup",

            "لیگ قهرمانان",
            "champions league",

            "مسی",
            "رونالدو",
            "امباپه",
            "هالند",
            "یامال",

            "منچستر یونایتد",
            "Manchester United",

            "رئال مادرید",
            "Real Madrid",

            "بارسلونا",
            "Barcelona",

            "لیورپول",
            "Liverpool",

            "آرسنال",
            "Arsenal",

        ]
    },


    "basketball": {

        "title": "بسکتبال",
        "emoji": "🏀",
        "hashtag": "#بسکتبال",

        "keywords": [

            "بسکتبال",
            "basketball",

            "nba",
            "wnba",

            "دانک",

            "سه امتیازی",

            "لیگ NBA",

        ]
    },


    "volleyball": {

        "title": "والیبال",
        "emoji": "🏐",
        "hashtag": "#والیبال",

        "keywords": [

            "والیبال",
            "volleyball",

            "fivb",

            "ست",

        ]
    },


    "wrestling": {

        "title": "کشتی",
        "emoji": "🤼",
        "hashtag": "#کشتی",

        "keywords": [

            "کشتی",
            "کشتی آزاد",
            "کشتی فرنگی",

            "قهرمانی جهان",

        ]
    },


    "tennis": {

        "title": "تنیس",
        "emoji": "🎾",
        "hashtag": "#تنیس",

        "keywords": [

            "تنیس",
            "tennis",

            "ATP",
            "WTA",

            "گرند اسلم",

            "ویمبلدون",

        ]
    },


    "formula1": {

        "title": "فرمول یک",
        "emoji": "🏎",
        "hashtag": "#فرمول_یک",

        "keywords": [

            "فرمول یک",
            "formula 1",
            "formula1",
            "f1",

            "گرندپری",

        ]
    },

}



# =========================
# Events
# =========================


SPORT_EVENTS = {


    "score": [

        "نتیجه",
        "پایان بازی",
        "برنده",
        "پیروز شد",
        "باخت",
        "مساوی",

    ],


    "goal": [

        "گل",
        "گلزن",
        "گلزنی",
        "هت تریک",

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
        "اظهارات مربی",
        "صحبت‌های سرمربی",

    ]

}



# =========================
# Big Teams
# =========================


BIG_TEAMS = [

    "منچستر یونایتد",
    "Manchester United",

    "منچستر سیتی",
    "Manchester City",

    "رئال مادرید",
    "Real Madrid",

    "بارسلونا",
    "Barcelona",

    "لیورپول",
    "Liverpool",

    "بایرن مونیخ",
    "Bayern",

    "پاری سن ژرمن",
    "PSG",

    "آرژانتین",
    "Argentina",

    "برزیل",
    "Brazil",

    "فرانسه",
    "France",

]



BIG_COMPETITIONS = [

    "جام جهانی",

    "world cup",

    "لیگ قهرمانان",

    "champions league",

    "فینال",

    "نیمه نهایی",

]



VIDEO_ONLY = [

    "هایلایت",

    "highlights",

    "watch video",

    "ویدیو",

    "ویدئو",

    "کلیپ",

    "لحظات برتر",

]



# =========================
# Helpers
# =========================


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



# =========================
# Detect Sport
# =========================


def detect_sport_type(title="", summary=""):


    text = f"{title} {summary}"


    for sport, data in SPORT_TYPES.items():


        if contains_any(

            text,

            data["keywords"]

        ):

            return {


                "type": sport,


                "title": data["title"],


                "emoji": data["emoji"],


                "hashtag": data["hashtag"]


            }



    return {


        "type": "sport",


        "title": "ورزش",


        "emoji": "🏆",


        "hashtag": "#ورزش"

    }



# =========================
# Events
# =========================


def detect_events(title="", summary=""):


    text = f"{title} {summary}"


    result = []



    for event, words in SPORT_EVENTS.items():


        if contains_any(text, words):

            result.append(event)



    return result



# =========================
# Big Match
# =========================


def is_big_match(title="", summary=""):


    text = f"{title} {summary}"


    return (

        contains_any(text, BIG_TEAMS)

        or

        contains_any(text, BIG_COMPETITIONS)

    )



# =========================
# Video Filter
# =========================


def is_video_only(title="", summary=""):


    text = f"{title} {summary}"


    return (

        contains_any(text, VIDEO_ONLY)

        and

        not detect_events(title, summary)

    )



# =========================
# Full Sport Analysis
# =========================


def analyze_sport(title="", summary=""):


    sport = detect_sport_type(

        title,

        summary

    )


    return {


        **sport,


        "events": detect_events(

            title,

            summary

        ),


        "big_match": is_big_match(

            title,

            summary

        ),


        "video_only": is_video_only(

            title,

            summary

        )


    }



# =========================
# Importance Score
# =========================


def calculate_sport_score(title="", summary=""):


    score = 1


    data = analyze_sport(

        title,

        summary

    )


    if data["big_match"]:

        score += 4



    if "score" in data["events"]:

        score += 3



    if "goal" in data["events"]:

        score += 2



    if "cards" in data["events"]:

        score += 2



    if "lineup" in data["events"]:

        score += 3



    if "interview" in data["events"]:

        score += 2



    if data["video_only"]:

        return 0



    if score > 10:

        score = 10



    return score
