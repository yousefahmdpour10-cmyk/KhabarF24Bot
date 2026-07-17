"""
KhabarF24 Sport Formatter v4.1

Sport Intelligence Engine

Features:
- Detect sport type
- Sport emoji
- Sport hashtag
- National team flags
- Match events
- Video filtering
"""


import re



# ==========================
# Sports Database
# ==========================


SPORTS = {


    "football": {

        "name": "فوتبال",
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

            "premier league",
            "لیگ برتر انگلیس",

            "la liga",
            "لالیگا",

            "serie a",
            "سری آ",

            "bundesliga",
            "بوندسلیگا",

            "مسی",
            "رونالدو",
            "امباپه",
            "هالند",

            "گلزنی",
            "گلزن",

            "VAR",

            "کارت زرد",
            "کارت قرمز",

        ]

    },



    "basketball": {

        "name": "بسکتبال",
        "emoji": "🏀",
        "hashtag": "#بسکتبال",

        "keywords": [

            "بسکتبال",
            "basketball",
            "NBA",
            "WNBA"

        ]

    },



    "volleyball": {

        "name": "والیبال",
        "emoji": "🏐",
        "hashtag": "#والیبال",

        "keywords": [

            "والیبال",
            "volleyball",
            "FIVB"

        ]

    },



    "tennis": {

        "name": "تنیس",
        "emoji": "🎾",
        "hashtag": "#تنیس",

        "keywords": [

            "تنیس",
            "tennis",
            "گرند اسلم",
            "ویمبلدون"

        ]

    },



    "wrestling": {

        "name": "کشتی",
        "emoji": "🤼",
        "hashtag": "#کشتی",

        "keywords": [

            "کشتی",
            "کشتی آزاد",
            "کشتی فرنگی",
            "UWW"

        ]

    },



    "formula1": {

        "name": "فرمول یک",
        "emoji": "🏎️",
        "hashtag": "#فرمول_یک",

        "keywords": [

            "فرمول یک",
            "Formula 1",
            "F1"

        ]

    }


}





# ==========================
# National Flags Only
# ==========================


NATIONAL_FLAGS = {


    "آرژانتین": "🇦🇷",

    "برزیل": "🇧🇷",

    "فرانسه": "🇫🇷",

    "انگلیس": "🇬🇧",

    "آلمان": "🇩🇪",

    "اسپانیا": "🇪🇸",

    "ایتالیا": "🇮🇹",

    "پرتغال": "🇵🇹",

    "هلند": "🇳🇱",

    "بلژیک": "🇧🇪",

    "آمریکا": "🇺🇸",

}





# ==========================
# Video Filter
# ==========================


VIDEO_ONLY_WORDS = [

    "تماشا کنید",

    "watch video",

    "watch live",

    "live stream",

    "پخش زنده",

    "هایلایت",

    "highlights",

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







# ==========================
# Detect Sport
# ==========================


def detect_sport(title="", summary=""):


    text = f"{title} {summary}"



    scores = {}



    for sport, data in SPORTS.items():


        score = 0


        for word in data["keywords"]:


            if word.lower() in text.lower():

                score += 1


        scores[sport] = score





    best = max(

        scores,

        key=scores.get

    )





    if scores[best] == 0:


        return {

            "type": "sport",

            "name": "ورزش",

            "emoji": "🏅",

            "hashtag": "#ورزش"

        }





    return {


        "type": best,

        "name": SPORTS[best]["name"],

        "emoji": SPORTS[best]["emoji"],

        "hashtag": SPORTS[best]["hashtag"]

    }









# ==========================
# Add National Flags
# ==========================


def add_team_flags(text):


    if not text:

        return ""



    for team, flag in NATIONAL_FLAGS.items():

        text = text.replace(

            team,

            f"{flag} {team}"

        )



    return text







# ==========================
# Video Detection
# ==========================


def is_blocked_sport_news(title="", summary=""):


    text = f"{title} {summary}"



    has_video_word = contains_any(

        text,

        VIDEO_ONLY_WORDS

    )



    has_news_word = contains_any(

        text,

        [

            "اعلام کرد",

            "گزارش",

            "نتیجه",

            "قرارداد",

            "مصدومیت",

            "ترکیب",

        ]

    )



    return has_video_word and not has_news_word







# ==========================
# Match Events
# ==========================


def detect_match_events(text):


    result = {}



    score = re.search(

        r"\d+\s*[-–]\s*\d+",

        text

    )



    if score:

        result["score"] = f"⚽ نتیجه: {score.group()}"



    return result







# ==========================
# Final Formatter
# ==========================


def format_sport_news(title, summary):


    sport = detect_sport(

        title,

        summary

    )



    if is_blocked_sport_news(

        title,

        summary

    ):


        return {

            "blocked": True,

            "sport": sport,

            "title": title,

            "summary": summary

        }




    title = add_team_flags(title)

    summary = add_team_flags(summary)



    events = detect_match_events(

        f"{title} {summary}"

    )



    return {


        "blocked": False,

        "sport": sport,

        "title": title,

        "summary": summary,

        "events": events

    }
