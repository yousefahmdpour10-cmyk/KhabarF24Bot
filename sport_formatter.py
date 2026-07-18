"""
KhabarF24 Sport Formatter v5.0

Sport Processing Engine

وظیفه:
- تحلیل خبر ورزشی
- افزودن پرچم تیم‌ها
- تشخیص رویداد بازی
- حذف ویدیوهای بدون ارزش خبری
- آماده سازی برای Formatter اصلی
"""


import re



print("⚽ KhabarF24 Sport Formatter v5.0 Loaded")



# ==================================
# Sports Data
# ==================================


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
            "استوک",
            "کفش فوتبال",
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
            "لیگ قهرمانان",

            "فیفا",
            "یوفا",

            "مسی",
            "رونالدو",
            "امباپه",
            "هالند",
            "یامال",

            "منچستر یونایتد",
            "رئال مادرید",
            "بارسلونا",
            "لیورپول",
            "آرسنال",

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

            "سه امتیازی",

            "ریباند",

            "کوارتر",

            "زمین بسکتبال",

            "لیکرز",

            "واریرز",

            "کری",

            "لبران",

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

    }

}





# ==================================
# Sport Flags
# فقط تیم‌ها
# ==================================


TEAM_FLAGS = {


    "منچستر یونایتد":
        "🔴 منچستر یونایتد",


    "رئال مادرید":
        "🇪🇸 رئال مادرید",


    "بارسلونا":
        "🇪🇸 بارسلونا",


    "لیورپول":
        "🔴 لیورپول",


    "آرسنال":
        "🔴 آرسنال",


    "منچستر سیتی":
        "🔵 منچستر سیتی",


    "بایرن مونیخ":
        "🇩🇪 بایرن مونیخ",


    "پاری سن ژرمن":
        "🇫🇷 پاری سن ژرمن",


    "آرژانتین":
        "🇦🇷 آرژانتین",


    "برزیل":
        "🇧🇷 برزیل",


    "فرانسه":
        "🇫🇷 فرانسه",


}





# ==================================
# Video Filter
# ==================================


VIDEO_WORDS = [


    "هایلایت",

    "highlights",

    "کلیپ",

    "ویدیو",

    "ویدئو",

    "watch video",

]





NEWS_WORDS = [


    "اعلام",

    "قرارداد",

    "نتیجه",

    "مصدومیت",

    "انتقال",

    "ترکیب",

    "گزارش",

]





def contains_any(text, words):


    text = text.lower()


    for word in words:

        if word.lower() in text:

            return True


    return False





# ==================================
# Detect sport
# ==================================


def detect_sport(title="", summary=""):


    text = f"{title} {summary}".lower()


    scores = {}



    for sport, data in SPORTS.items():


        score = 0


        for word in data["keywords"]:


            if word.lower() in text:

                score += 1



        scores[sport] = score




    best = max(

        scores,

        key=scores.get

    )



    if scores[best] == 0:


        return {

            "type":"sport",

            "name":"ورزش",

            "emoji":"🏆",

            "hashtag":"#ورزش"

        }



    return {


        "type":best,

        "name":SPORTS[best]["name"],

        "emoji":SPORTS[best]["emoji"],

        "hashtag":SPORTS[best]["hashtag"]

    }






# ==================================
# Add Team Flags
# ==================================


def add_team_flags(text):


    if not text:

        return ""


    for team, flag in TEAM_FLAGS.items():


        text = text.replace(

            team,

            flag

        )


    return text






# ==================================
# Video Only
# ==================================


def is_video_only(title, summary):


    text = f"{title} {summary}"


    return (

        contains_any(text, VIDEO_WORDS)

        and

        not contains_any(text, NEWS_WORDS)

    )







# ==================================
# Match Result
# ==================================


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







# ==================================
# Main Function
# ==================================


def format_sport_news(title, summary):


    sport = detect_sport(

        title,

        summary

    )



    if is_video_only(title, summary):


        return {


            "blocked":True,

            "sport":sport,

            "title":title,

            "summary":summary

        }




    title = add_team_flags(title)


    summary = add_team_flags(summary)



    events = detect_match_result(

        f"{title} {summary}"

    )




    return {


        "blocked":False,


        "sport":sport,


        "title":title,


        "summary":summary,


        "events":events

    }
