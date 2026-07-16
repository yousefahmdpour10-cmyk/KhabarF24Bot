"""
KhabarF24 Sport Formatter v4.0

Features:
- Detect sport type
- Sport emoji
- Sport hashtag
- Team flags
- Match result
- Goals
- Yellow cards
- Red cards
- Lineups
- Coach/player interviews
- Remove video-only posts
"""


import re



# ==========================
# ورزش‌ها
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

            "لیگ قهرمانان",
            "champions league",

            "premier league",
            "لیگ برتر",

            "la liga",
            "لالیگا",

            "serie a",
            "سری آ",

            "bundesliga",
            "بوندسلیگا",

            "گل",
            "گلزنی",

            "مسی",
            "رونالدو",

            "مربی",
            "سرمربی",

            "VAR",

            "کارت زرد",
            "کارت قرمز"

        ]

    },


    "basketball": {

        "name": "بسکتبال",
        "emoji": "🏀",
        "hashtag": "#بسکتبال",

        "keywords": [

            "بسکتبال",
            "NBA",
            "WNBA"

        ]

    },


    "tennis": {

        "name": "تنیس",
        "emoji": "🎾",
        "hashtag": "#تنیس",

        "keywords": [

            "تنیس",
            "گرند اسلم",
            "ویمبلدون"

        ]

    },


    "volleyball": {

        "name": "والیبال",
        "emoji": "🏐",
        "hashtag": "#والیبال",

        "keywords": [

            "والیبال",
            "FIVB"

        ]

    },


    "wrestling": {

        "name": "کشتی",
        "emoji": "🤼",
        "hashtag": "#کشتی",

        "keywords": [

            "کشتی",
            "آزاد",
            "فرنگی"

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
# پرچم تیم‌ها
# ==========================


TEAM_FLAGS = {


    "منچستر یونایتد": "🏴",
    "منچستر سیتی": "🏴",

    "رئال مادرید": "🇪🇸",
    "بارسلونا": "🇪🇸",

    "لیورپول": "🏴",
    "آرسنال": "🏴",

    "بایرن مونیخ": "🇩🇪",

    "پاری‌سن‌ژرمن": "🇫🇷",

    "اینتر": "🇮🇹",

    "میلان": "🇮🇹",

    "یوونتوس": "🇮🇹",

    "آرژانتین": "🇦🇷",

    "برزیل": "🇧🇷",

    "فرانسه": "🇫🇷",

    "انگلیس": "🏴"

}





# ==========================
# حذف خبرهای فقط ویدیو
# ==========================


VIDEO_ONLY_WORDS = [

    "تماشا کنید",

    "watch",

    "watch live",

    "live stream",

    "پخش زنده",

    "هایلایت",

    "highlights",

]





# ==========================
# تشخیص نوع ورزش
# ==========================


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







# ==========================
# بررسی ویدیویی
# ==========================


def is_blocked_sport_news(title="", summary=""):


    text = f"{title} {summary}".lower()


    for word in VIDEO_ONLY_WORDS:


        if word.lower() in text:

            return True



    return False







# ==========================
# پرچم اضافه کردن
# ==========================


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

            f"{flag} {team}"

        )



    return text







# ==========================
# نتیجه بازی
# ==========================


def detect_match_events(text):


    result = {


        "score": "",

        "goals": "",

        "yellow": "",

        "red": "",

        "lineup": "",

        "interview": ""

    }




    # نتیجه 2-1

    score = re.search(

        r"(\d+)\s*[-–]\s*(\d+)",

        text

    )



    if score:


        result["score"] = (

            f"⚽ نتیجه: {score.group(0)}"

        )





    # کارت زرد

    if "کارت زرد" in text:


        result["yellow"] = (

            "🟨 کارت زرد: اعلام شده"

        )





    # کارت قرمز

    if "کارت قرمز" in text:


        result["red"] = (

            "🟥 کارت قرمز: اعلام شده"

        )





    # ترکیب

    if "ترکیب" in text:


        result["lineup"] = (

            "👥 ترکیب: منتشر شد"

        )





    # مصاحبه

    interview_words = [

        "مصاحبه",

        "گفت",

        "اظهارات",

        "صحبت‌های",

        "صحبت های"

    ]


    for word in interview_words:


        if word in text:


            result["interview"] = (

                "🎤 مصاحبه: خلاصه صحبت‌های مربی یا بازیکن"

            )

            break



    return result







# ==========================
# خروجی نهایی ورزش
# ==========================


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
