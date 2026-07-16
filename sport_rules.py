"""
KhabarF24 Sport Rules v2.0

موتور هوشمند ورزش

قابلیت‌ها:
- تشخیص رشته ورزشی
- امتیاز اهمیت خبر ورزشی
- تشخیص بازی‌های بزرگ
- تشخیص ترکیب، نتیجه، گل، کارت، مصاحبه
- حذف خبرهای ناقص ویدیویی
"""


# =========================
# 🏅 رشته های ورزشی
# =========================


SPORT_TYPES = {


    "football": {

        "emoji": "⚽",

        "hashtag": "#فوتبال",

        "keywords": [

            "فوتبال",
            "football",
            "soccer",

            "fifa",
            "uefa",

            "جام جهانی",
            "world cup",

            "لیگ قهرمانان",

            "مسی",
            "رونالدو",
            "امباپه",

            "منچستر",
            "رئال",
            "بارسلونا",

            "گل",
            "گلزن",
            "VAR",

            "کارت قرمز",
            "کارت زرد",

        ]

    },



    "basketball": {

        "emoji": "🏀",

        "hashtag": "#بسکتبال",

        "keywords": [

            "بسکتبال",
            "basketball",

            "nba",
            "wnba",

            "دانک",

            "سه امتیازی",

        ]

    },



    "volleyball": {

        "emoji": "🏐",

        "hashtag": "#والیبال",

        "keywords": [

            "والیبال",
            "volleyball",

            "fivb",

            "ست",

        ]

    },



    "tennis": {

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



    "wrestling": {

        "emoji": "🤼",

        "hashtag": "#کشتی",

        "keywords": [

            "کشتی",

            "کشتی آزاد",

            "کشتی فرنگی",

            "قهرمانی جهان",

        ]

    },



    "formula1": {

        "emoji": "🏎",

        "hashtag": "#فرمول_یک",

        "keywords": [

            "فرمول یک",

            "formula 1",

            "f1",

            "گرندپری",

        ]

    },


}





# =========================
# تیم های بزرگ
# =========================


BIG_TEAMS = [

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

    "بایرن مونیخ",
    "Bayern",

    "پاری سن ژرمن",
    "PSG",

    "آرژانتین",
    "Argentina",

    "انگلیس",
    "England",

    "برزیل",
    "Brazil",

    "فرانسه",
    "France",

]




# =========================
# مسابقات مهم
# =========================


BIG_COMPETITIONS = [

    "جام جهانی",

    "world cup",

    "لیگ قهرمانان",

    "champions league",

    "فینال",

    "نیمه نهایی",

    "semi final",

]




# =========================
# اتفاقات مهم
# =========================


IMPORTANT_EVENTS = [

    "نتیجه",

    "پایان بازی",

    "گل",

    "گلزن",

    "هت تریک",

    "کارت قرمز",

    "کارت زرد",

    "اخراج",

    "VAR",

    "نیمه اول",

    "نیمه دوم",

    "مصاحبه",

    "کنفرانس خبری",

]





# =========================
# ترکیب
# =========================


LINEUP_WORDS = [

    "ترکیب رسمی",

    "ترکیب اولیه",

    "lineup",

    "starting xi",

    "starting eleven",

]






# =========================
# خبرهای ناقص
# =========================


VIDEO_ONLY_WORDS = [

    "هایلایت",

    "highlights",

    "watch video",

    "video",

    "ویدئو",

    "کلیپ",

    "لحظات برتر",

]





# =========================
# ابزارها
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
# تشخیص رشته
# =========================


def detect_sport_type(title="", summary=""):


    text = f"""

    {title}

    {summary}

    """



    for sport, data in SPORT_TYPES.items():


        if contains_any(

            text,

            data["keywords"]

        ):

            return {

                "type": sport,

                "emoji": data["emoji"],

                "hashtag": data["hashtag"]

            }



    return None





# =========================
# حذف خبر ناقص
# =========================


def is_incomplete_sport_news(title="", summary=""):


    text = f"""

    {title}

    {summary}

    """



    has_video = contains_any(

        text,

        VIDEO_ONLY_WORDS

    )



    has_event = contains_any(

        text,

        IMPORTANT_EVENTS

    )



    if has_video and not has_event:

        return True



    return False





# =========================
# بازی بزرگ
# =========================


def is_big_match(title="", summary=""):


    text = f"""

    {title}

    {summary}

    """



    return (

        contains_any(text, BIG_TEAMS)

        or

        contains_any(text, BIG_COMPETITIONS)

    )





# =========================
# امتیاز ورزش
# =========================


def calculate_sport_score(title="", summary=""):


    score = 0



    if is_big_match(title, summary):

        score += 4



    if contains_any(

        summary,

        BIG_COMPETITIONS

    ):

        score += 3




    if contains_any(

        summary,

        IMPORTANT_EVENTS

    ):

        score += 2




    if contains_any(

        title,

        LINEUP_WORDS

    ):


        score += 3





    if is_incomplete_sport_news(

        title,

        summary

    ):

        score = 0




    if score > 10:

        score = 10



    return score
