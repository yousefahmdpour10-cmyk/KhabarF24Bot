"""
KhabarF24 Category Engine v7.1

Smart Category + Hashtag Engine

Features:

- Weighted keywords
- Sport separation
- Equipment detection
- Politics priority
- Emoji
- Hashtag
- Formatter ready
"""


print("🔥 KhabarF24 Category Engine v7.1 Loaded")



# ==========================
# Categories Database
# ==========================


CATEGORIES = {



    # ==========================
    # 🔴 Politics
    # ==========================

    "politics": {

        "name": "سیاست",

        "emoji": "🔴",

        "hashtag": "#سیاست",

        "priority": 10,


        "keywords": [


            "جنگ",

            "حمله نظامی",

            "حمله موشکی",

            "حمله هوایی",

            "موشک",

            "پهپاد",

            "ارتش",

            "نیروی نظامی",

            "عملیات نظامی",

            "درگیری",

            "تنش",

            "بحران",

            "تحریم",

            "مذاکرات",

            "توافق",

            "آتش بس",

            "دیپلماسی",

            "انتخابات",

            "رئیس جمهور",

            "رئیس‌جمهور",

            "وزیر خارجه",

            "وزیر دفاع",

            "پارلمان",

            "کاخ سفید",

            "ناتو",

            "ترور",

            "انفجار",

            "بازداشت",

            "کودتا",


        ]

    },





    # ==========================
    # ⚽ Football
    # ==========================


    "football": {


        "name": "فوتبال",

        "emoji": "⚽",

        "hashtag": "#فوتبال",

        "priority": 8,


        "keywords": [


            "فوتبال",

            "football",

            "soccer",


            "توپ فوتبال",

            "کفش فوتبال",

            "استوک",

            "دروازه فوتبال",

            "زمین فوتبال",


            "بازیکن فوتبال",

            "مهاجم",

            "مدافع",

            "هافبک",

            "دروازه‌بان",


            "سرمربی",

            "مربی فوتبال",


            "ترکیب رسمی",

            "lineup",

            "starting xi",


            "var",

            "داور فوتبال",


            "نقل و انتقالات",

            "قرارداد بازیکن",


            "جام جهانی",

            "لیگ قهرمانان",

            "چمپیونزلیگ",

            "فیفا",

            "یوفا",


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





    # ==========================
    # 🏀 Basketball
    # ==========================


    "basketball": {


        "name": "بسکتبال",

        "emoji": "🏀",

        "hashtag": "#بسکتبال",

        "priority": 8,


        "keywords": [


            "بسکتبال",

            "basketball",

            "nba",

            "wnba",


            "توپ بسکتبال",

            "سبد بسکتبال",

            "زمین بسکتبال",

            "دانک",

            "ریباند",

            "سه امتیازی",

            "کوآرتر",

            "لیکرز",

            "واریرز",

            "لبران",

            "کری",


        ]

    },





    # ==========================
    # 🏐 Volleyball
    # ==========================


    "volleyball": {


        "name": "والیبال",

        "emoji": "🏐",

        "hashtag": "#والیبال",

        "priority": 8,


        "keywords": [


            "والیبال",

            "volleyball",

            "fivb",

            "توپ والیبال",

            "تور والیبال",

            "زمین والیبال",

            "ست",

            "اسپک",

            "لیبرو",


        ]

    },
        # ==========================
    # 🎾 Tennis
    # ==========================


    "tennis": {


        "name": "تنیس",

        "emoji": "🎾",

        "hashtag": "#تنیس",

        "priority": 7,


        "keywords": [

            "تنیس",

            "tennis",

            "ATP",

            "WTA",

            "گرند اسلم",

            "ویمبلدون",

            "رولان گاروس",

            "اوپن آمریکا",

            "اوپن استرالیا",

            "راکت تنیس",

            "توپ تنیس",

            "زمین تنیس",

            "سرویس",

            "ست تنیس",

        ]

    },





    # ==========================
    # 🤼 Wrestling
    # ==========================


    "wrestling": {


        "name": "کشتی",

        "emoji": "🤼",

        "hashtag": "#کشتی",

        "priority": 7,


        "keywords": [

            "کشتی",

            "کشتی آزاد",

            "کشتی فرنگی",

            "اتحادیه جهانی کشتی",

            "uww",

            "قهرمانی جهان",

            "تشک کشتی",

            "وزن‌کشی",

            "مدال طلا",

            "فن کشتی",

        ]

    },





    # ==========================
    # 🏎 Formula 1
    # ==========================


    "formula1": {


        "name": "فرمول یک",

        "emoji": "🏎",

        "hashtag": "#فرمول_یک",

        "priority": 7,


        "keywords": [

            "فرمول یک",

            "formula 1",

            "formula1",

            "f1",

            "گرندپری",

            "راننده فرمول یک",

            "ماشین مسابقه",

            "پیست",

            "مرسدس",

            "فراری",

            "ردبول",

        ]

    },





    # ==========================
    # 💻 Technology
    # ==========================


    "technology": {


        "name": "تکنولوژی",

        "emoji": "💻",

        "hashtag": "#تکنولوژی",

        "priority": 6,


        "keywords": [

            "فناوری",

            "تکنولوژی",

            "technology",

            "هوش مصنوعی",

            "artificial intelligence",

            "ai",

            "openai",

            "chatgpt",

            "گوگل",

            "google",

            "اپل",

            "apple",

            "مایکروسافت",

            "microsoft",

            "انویدیا",

            "nvidia",

            "تسلا",

            "tesla",

            "ربات",

            "تراشه",

            "چیپ",

            "پردازنده",

            "امنیت سایبری",

            "هک",

        ]

    },





    # ==========================
    # 🎮 Gaming
    # ==========================


    "gaming": {


        "name": "گیم",

        "emoji": "🎮",

        "hashtag": "#گیم",

        "priority": 5,


        "keywords": [

            "گیم",

            "gaming",

            "game",

            "بازی ویدیویی",

            "پلی استیشن",

            "playstation",

            "xbox",

            "ایکس باکس",

            "نینتندو",

            "nintendo",

            "steam",

            "کنسول",

            "minecraft",

            "fortnite",

            "call of duty",

        ]

    },





    # ==========================
    # 💰 Economy
    # ==========================


    "economy": {


        "name": "اقتصاد",

        "emoji": "💰",

        "hashtag": "#اقتصاد",

        "priority": 5,


        "keywords": [

            "اقتصاد",

            "دلار",

            "ارز",

            "یورو",

            "طلا",

            "نفت",

            "گاز",

            "بورس",

            "سهام",

            "تورم",

            "بانک",

            "بیت کوین",

            "bitcoin",

            "کریپتو",

        ]

    },





    # ==========================
    # 🌍 World
    # ==========================


    "world": {


        "name": "جهان",

        "emoji": "🌍",

        "hashtag": "#جهان",

        "priority": 3,


        "keywords": [

            "آمریکا",

            "روسیه",

            "چین",

            "اروپا",

            "اوکراین",

            "بریتانیا",

            "فرانسه",

            "آلمان",

            "سازمان ملل",

            "بین‌الملل",

            "بین الملل",

        ]

    },





    # ==========================
    # 🏥 Health
    # ==========================


    "health": {


        "name": "سلامت",

        "emoji": "🏥",

        "hashtag": "#سلامت",

        "priority": 3,


        "keywords": [

            "سلامت",

            "بیماری",

            "ویروس",

            "واکسن",

            "پزشکی",

            "دارو",

            "بیمارستان",

        ]

    },





    # ==========================
    # 🌦 Weather
    # ==========================


    "weather": {


        "name": "آب‌وهوا",

        "emoji": "🌦",

        "hashtag": "#آب_وهوا",

        "priority": 3,


        "keywords": [

            "هواشناسی",

            "weather",

            "طوفان",

            "سیل",

            "زلزله",

            "بارندگی",

            "برف",

            "گرمای شدید",

            "سرمای شدید",

        ]

    },

}






# ==========================
# Detection Engine
# ==========================


def detect_smart_category(title="", summary="", source=""):


    text = f"{title} {summary}".lower()


    scores = {}



    for category, data in CATEGORIES.items():


        score = 0


        for word in data["keywords"]:


            if word.lower() in text:

                score += data["priority"]


        scores[category] = score



    # اول امنیت و جنگ

    if scores.get("politics", 0) >= 10:

        return "politics"



    # بعد ورزش‌ها

    sport_categories = [

        "football",

        "basketball",

        "volleyball",

        "tennis",

        "wrestling",

        "formula1"

    ]


    best_sport = max(

        sport_categories,

        key=lambda x: scores.get(x,0)

    )


    if scores.get(best_sport,0) >= 7:

        return best_sport



    # بقیه دسته‌ها

    result = max(

        scores,

        key=scores.get

    )


    if scores[result] == 0:

        return "world"


    return result






# ==========================
# Formatter Info
# ==========================


def get_category_info(category):


    data = CATEGORIES.get(

        category,

        CATEGORIES["world"]

    )


    return {


        "category": category,


        "name": data["name"],


        "emoji": data["emoji"],


        "hashtag": data["hashtag"]


    }
