"""
KhabarF24 Sport Formatter v3.0

Features:
- Detect sport type
- Sport emoji
- Sport hashtag
- Team flags
- Remove video-only posts
- Match event detection
"""


import re



SPORTS = {


    "football": {

        "name": "فوتبال",

        "emoji": "⚽",

        "hashtag": "#فوتبال",

        "keywords": [

            "فوتبال",
            "جام جهانی",
            "لیگ قهرمانان",
            "Premier League",
            "La Liga",
            "گل",
            "مسی",
            "رونالدو",
            "بازیکن",
            "مربی",
            "باشگاه",
            "VAR",
            "فینال"

        ]

    },


    "basketball": {

        "name": "بسکتبال",

        "emoji": "🏀",

        "hashtag": "#بسکتبال",

        "keywords": [

            "بسکتبال",
            "NBA",
            "لیکرز",
            "سلتیکس",
            "کری"

        ]

    },


    "volleyball": {

        "name": "والیبال",

        "emoji": "🏐",

        "hashtag": "#والیبال",

        "keywords": [

            "والیبال",
            "لیگ ملت‌ها",
            "FIVB"

        ]

    },


    "tennis": {

        "name": "تنیس",

        "emoji": "🎾",

        "hashtag": "#تنیس",

        "keywords": [

            "تنیس",
            "گرند اسلم",
            "ویمبلدون",
            "رولان گاروس"

        ]

    },


    "wrestling": {

        "name": "کشتی",

        "emoji": "🤼",

        "hashtag": "#کشتی",

        "keywords": [

            "کشتی",
            "آزاد",
            "فرنگی",
            "اتحادیه جهانی کشتی"

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

    },


    "mma": {

        "name": "MMA",

        "emoji": "🥊",

        "hashtag": "#MMA",

        "keywords": [

            "UFC",
            "MMA",
            "مبارزه"

        ]

    }


}







TEAM_FLAGS = {


    "آرژانتین": "🇦🇷",

    "انگلیس": "🏴🇬🇧",

    "اسپانیا": "🇪🇸",

    "فرانسه": "🇫🇷",

    "آلمان": "🇩🇪",

    "ایتالیا": "🇮🇹",

    "پرتغال": "🇵🇹",

    "برزیل": "🇧🇷",

    "هلند": "🇳🇱",

    "ایران": "🇮🇷",

    "آمریکا": "🇺🇸",

    "ژاپن": "🇯🇵"

}







BLOCK_WORDS = [

    "تماشا کنید",

    "watch",

    "watch live",

    "live stream",

    "پخش زنده",

    "هایلایت",

    "highlights",

    "preview",

    "پیش نمایش",

    "ویدیو",

    "video"

]








def detect_sport(title="", summary=""):


    text = f"{title} {summary}".lower()



    scores = {}



    for sport, data in SPORTS.items():


        count = 0


        for word in data["keywords"]:


            if word.lower() in text:

                count += 1



        scores[sport] = count



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



    data = SPORTS[best]



    return {

        "type": best,

        "name": data["name"],

        "emoji": data["emoji"],

        "hashtag": data["hashtag"]

    }









def is_blocked_sport_news(title="", summary=""):


    text = f"{title} {summary}".lower()



    for word in BLOCK_WORDS:


        if word.lower() in text:

            return True



    return False







def add_team_flags(text):


    if not text:

        return ""



    items = sorted(

        TEAM_FLAGS.items(),

        key=lambda x: len(x[0]),

        reverse=True

    )


    for team, flag in items:


        text = text.replace(

            team,

            f"{flag}{team}"

        )



    return text







def format_score(text):


    if not text:

        return ""



    pattern = r"(\D+)\s(\d+)\s*[-–]\s*(\d+)\s(\D+)"



    return re.sub(

        pattern,

        r"\1 \2-\3 \4",

        text

    )









def format_sport_news(title, summary):


    sport = detect_sport(

        title,

        summary

    )



    blocked = is_blocked_sport_news(

        title,

        summary

    )



    if blocked:


        return {

            "blocked": True,

            "sport": sport,

            "title": title,

            "summary": summary

        }






    title = format_score(title)

    summary = format_score(summary)



    title = add_team_flags(title)

    summary = add_team_flags(summary)





    return {


        "blocked": False,


        "sport": sport,


        "title": title,


        "summary": summary

    }
