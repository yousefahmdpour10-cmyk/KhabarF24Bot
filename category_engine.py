"""
KhabarF24 Category Engine v7.0

Smart Category + Hashtag Engine

Features:

- Weighted keywords
- Priority detection
- Emoji
- Hashtag
- Sport separation
- Politics protection
"""

print("🔥 KhabarF24 Category Engine v7.0 Loaded")



# ==========================
# Categories Database
# ==========================


CATEGORIES = {


    "football": {

        "name": "فوتبال",
        "emoji": "⚽",
        "hashtag": "#فوتبال",
        "weight": 5,

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

            "ترکیب",
            "lineup",

            "کارت زرد",
            "کارت قرمز",

            "var",

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

            "منچستر سیتی",

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


        "name": "بسکتبال",
        "emoji": "🏀",
        "hashtag": "#بسکتبال",
        "weight": 5,


        "keywords": [

            "بسکتبال",
            "basketball",

            "nba",
            "wnba",

            "توپ بسکتبال",

            "دانک",

            "سه امتیازی",

            "ریباند",

            "کوآرتر",

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
        "weight": 5,


        "keywords": [

            "والیبال",
            "volleyball",

            "fivb",

            "ست",

            "تور والیبال",

            "توپ والیبال",

        ]

    },





    "politics": {


        "name": "سیاست",
        "emoji": "🔴",
        "hashtag": "#سیاست",
        "weight": 5,


        "keywords": [

            "جنگ",

            "حمله",

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






    "iran": {


        "name": "ایران",
        "emoji": "🇮🇷",
        "hashtag": "#ایران",
        "weight": 4,


        "keywords": [

            "ایران",

            "ایرانی",

            "تهران",

            "دولت ایران",

            "مجلس ایران",

            "سپاه",

            "وزارت کشور",

        ]

    },




    "world": {


        "name": "جهان",
        "emoji": "🌍",
        "hashtag": "#جهان",
        "weight": 3,


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

            "بین الملل",

            "بین‌الملل",

        ]

    },
        "technology": {


        "name": "تکنولوژی",
        "emoji": "💻",
        "hashtag": "#تکنولوژی",
        "weight": 4,


        "keywords": [

            "فناوری",

            "تکنولوژی",

            "technology",

            "هوش مصنوعی",

            "ai",

            "artificial intelligence",

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





    "gaming": {


        "name": "گیم",
        "emoji": "🎮",
        "hashtag": "#گیم",
        "weight": 3,


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

            "استیم",

            "کنسول",

            "minecraft",

            "fortnite",

            "call of duty",

        ]

    },





    "economy": {


        "name": "اقتصاد",
        "emoji": "💰",
        "hashtag": "#اقتصاد",
        "weight": 4,


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





    "health": {


        "name": "سلامت",
        "emoji": "🏥",
        "hashtag": "#سلامت",
        "weight": 3,


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





    "science": {


        "name": "علم",
        "emoji": "🔬",
        "hashtag": "#علم",
        "weight": 2,


        "keywords": [

            "علم",

            "science",

            "تحقیق",

            "آزمایش",

            "فضا",

            "ناسا",

            "nasa",

        ]

    },





    "weather": {


        "name": "آب‌وهوا",
        "emoji": "🌦",
        "hashtag": "#آب_وهوا",
        "weight": 3,


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


def detect_smart_category(

        title="",

        summary="",

        source=""

):


    text = f"{title} {summary}".lower()



    scores = {}



    for category, data in CATEGORIES.items():


        score = 0



        for word in data["keywords"]:


            if word.lower() in text:

                score += data["weight"]



        scores[category] = score





    # ==========================
    # حفاظت فوتبال و ورزش
    # ==========================


    if scores.get("football",0) >= 5:

        result = "football"



    elif scores.get("basketball",0) >= 5:

        result = "basketball"



    elif scores.get("volleyball",0) >= 5:

        result = "volleyball"




    # ==========================
    # سیاست همیشه بالاتر از جهان
    # ==========================


    elif scores.get("politics",0) >= 5:

        result = "politics"




    elif scores.get("iran",0) > 0:

        result = "iran"




    elif scores.get("world",0) > 0:

        result = "world"



    else:


        result = max(

            scores,

            key=scores.get

        )



        if scores[result] == 0:

            result = "world"





    return result





# ==========================
# Category Info
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
