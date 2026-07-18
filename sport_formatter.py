"""
KhabarF24 Sport Formatter v5.1

Sport Intelligence Formatter

Features:
- Multi sport detection
- Correct sport emoji
- Correct sport hashtag
- Team flags
- Club nickname support
- Match score detection
- Video filtering
- Formatter ready output
"""


import re


print("⚽ KhabarF24 Sport Formatter v5.1 Loaded")



# =====================================
# Sports Database
# =====================================


SPORTS = {


    "football": {

        "name": "فوتبال",
        "emoji": "⚽",
        "hashtag": "#فوتبال",

        "keywords": [

            "فوتبال",
            "football",
            "soccer",

            "توپ فوتبال",
            "کفش فوتبال",
            "استوک",
            "دروازه",

            "گل",
            "گلزنی",
            "گلزن",

            "بازیکن",
            "مهاجم",
            "مدافع",
            "هافبک",

            "مربی",
            "سرمربی",

            "var",

            "کارت زرد",
            "کارت قرمز",

            "جام جهانی",
            "world cup",

            "لیگ قهرمانان",
            "champions league",

            "fifa",
            "uefa",

            "مسی",
            "رونالدو",
            "امباپه",
            "هالند",
            "یامال",

            "premier league",
            "لیگ برتر انگلیس",

            "la liga",
            "لالیگا",

            "serie a",
            "سری آ",

            "bundesliga",
            "بوندسلیگا",

        ]
    },



    "basketball": {


        "name": "بسکتبال",
        "emoji": "🏀",
        "hashtag": "#بسکتبال",


        "keywords": [

            "بسکتبال",
            "basketball",

            "nba",
            "wnba",

            "توپ بسکتبال",

            "دانک",
            "ریباند",

            "سه امتیازی",

            "کوارتر",

            "زمین بسکتبال",

            "لیکرز",
            "واریرز",

            "لبران",
            "کری",

        ]

    },



    "volleyball": {


        "name": "والیبال",
        "emoji": "🏐",
        "hashtag": "#والیبال",


        "keywords": [

            "والیبال",
            "volleyball",

            "توپ والیبال",

            "fivb",

            "ست",

            "سرویس",

            "اسپک",

            "دفاع روی تور",

        ]

    },



    "tennis": {


        "name": "تنیس",
        "emoji": "🎾",
        "hashtag": "#تنیس",


        "keywords": [

            "تنیس",
            "tennis",

            "راکت",
            "زمین تنیس",

            "atp",
            "wta",

            "گرند اسلم",

            "ویمبلدون",

            "رولان گاروس",

            "جوکوویچ",

            "آلکاراز",

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

            "تشک",

            "uww",

            "قهرمانی جهان",

            "مدال",

            "حسن یزدانی",

        ]

    },



    "formula1": {


        "name": "فرمول یک",
        "emoji": "🏎️",
        "hashtag": "#فرمول_یک",


        "keywords": [

            "فرمول یک",

            "formula 1",
            "formula1",
            "f1",

            "گرندپری",

            "پیست",

            "ردبول",

            "فراری",

            "ورشتپن",

        ]

    },



    "combat": {


        "name": "ورزش رزمی",
        "emoji": "🥊",
        "hashtag": "#ورزش_رزمی",


        "keywords": [

            "ufc",

            "mma",

            "بوکس",

            "boxing",

            "ناک اوت",

            "کمربند قهرمانی",

        ]

    },


}



# =====================================
# Team Flags
# فقط تیم‌ها و باشگاه‌ها
# =====================================


TEAM_FLAGS = {


    # England 🇬🇧

    "منچستر یونایتد":
        "🔴 منچستر یونایتد",

    "Manchester United":
        "🔴 Manchester United",


    "منچستر سیتی":
        "🔵 منچستر سیتی",

    "Manchester City":
        "🔵 Manchester City",


    "لیورپول":
        "🔴 لیورپول",

    "Liverpool":
        "🔴 Liverpool",


    "آرسنال":
        "🔴 آرسنال",

    "Arsenal":
        "🔴 Arsenal",



    # Spain 🇪🇸

    "رئال مادرید":
        "🇪🇸 رئال مادرید",

    "Real Madrid":
        "🇪🇸 Real Madrid",


    "بارسلونا":
        "🇪🇸 بارسلونا",

    "Barcelona":
        "🇪🇸 Barcelona",



    # Germany 🇩🇪

    "بایرن مونیخ":
        "🇩🇪 بایرن مونیخ",

    "Bayern Munich":
        "🇩🇪 Bayern Munich",



    # France 🇫🇷

    "پاری سن ژرمن":
        "🇫🇷 پاری سن ژرمن",

    "Paris Saint-Germain":
        "🇫🇷 Paris Saint-Germain",



    # Italy 🇮🇹

    "یوونتوس":
        "🇮🇹 یوونتوس",

    "Juventus":
        "🇮🇹 Juventus",


}
# =====================================
# Video Filter
# =====================================


VIDEO_WORDS = [

    "هایلایت",

    "highlights",

    "کلیپ",

    "ویدیو",

    "ویدئو",

    "watch video",

    "watch live",

    "live stream",

    "پخش زنده",

]




NEWS_WORDS = [

    "اعلام",

    "گزارش",

    "نتیجه",

    "قرارداد",

    "انتقال",

    "مصدومیت",

    "ترکیب",

    "شروع بازی",

    "پایان بازی",

]





# =====================================
# Helpers
# =====================================


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






# =====================================
# Detect Sport
# =====================================


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

            "emoji": "🏆",

            "hashtag": "#ورزش"

        }





    return {


        "type": best,

        "name": SPORTS[best]["name"],

        "emoji": SPORTS[best]["emoji"],

        "hashtag": SPORTS[best]["hashtag"]

    }







# =====================================
# Team Flags
# =====================================


def add_team_flags(text):


    if not text:

        return ""



    for team, flag_name in TEAM_FLAGS.items():


        text = text.replace(

            team,

            flag_name

        )



    return text







# =====================================
# Video Only Filter
# =====================================


def is_video_only(title="", summary=""):


    text = f"{title} {summary}"



    has_video = contains_any(

        text,

        VIDEO_WORDS

    )


    has_news = contains_any(

        text,

        NEWS_WORDS

    )


    return (

        has_video

        and

        not has_news

    )







# =====================================
# Match Result Detection
# =====================================


def detect_match_result(text):


    result = {}



    score = re.search(

        r"\d+\s*[-–]\s*\d+",

        text

    )



    if score:


        result["score"] = (

            f"⚽ نتیجه: {score.group()}"

        )



    return result








# =====================================
# Final Sport Formatter
# =====================================


def format_sport_news(title="", summary=""):


    sport = detect_sport(

        title,

        summary

    )



    # حذف ویدیوهای بدون ارزش خبری

    if is_video_only(

        title,

        summary

    ):


        return {


            "blocked": True,


            "sport": sport,


            "title": title,


            "summary": summary,


            "events": {}

        }






    # اضافه کردن نشان تیم‌ها

    title = add_team_flags(

        title

    )


    summary = add_team_flags(

        summary

    )





    events = detect_match_result(

        f"{title} {summary}"

    )





    return {


        "blocked": False,


        "sport": sport,


        "title": title,


        "summary": summary,


        "events": events


    }
