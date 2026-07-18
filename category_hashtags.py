"""
KhabarF24 Category Hashtag Engine v2.0

وظیفه:
- تعیین هشتگ نهایی خبر
- تشخیص رشته ورزشی
- هماهنگ با Category Engine v7
- خروجی استاندارد برای Formatter
"""


print("🏷️ KhabarF24 Hashtag Engine v2.0 Loaded")



# ==========================
# Hashtags Database
# ==========================


HASHTAGS = {


    "politics": {
        "emoji": "🔴",
        "hashtag": "#سیاست"
    },


    "iran": {
        "emoji": "🇮🇷",
        "hashtag": "#ایران"
    },


    "world": {
        "emoji": "🌍",
        "hashtag": "#جهان"
    },


    "technology": {
        "emoji": "💻",
        "hashtag": "#تکنولوژی"
    },


    "gaming": {
        "emoji": "🎮",
        "hashtag": "#گیم"
    },


    "economy": {
        "emoji": "💰",
        "hashtag": "#اقتصاد"
    },


    "health": {
        "emoji": "🏥",
        "hashtag": "#سلامت"
    },


    "science": {
        "emoji": "🔬",
        "hashtag": "#علم"
    },


    "weather": {
        "emoji": "🌦",
        "hashtag": "#هواشناسی"
    },


    "football": {
        "emoji": "⚽",
        "hashtag": "#فوتبال"
    },


    "basketball": {
        "emoji": "🏀",
        "hashtag": "#بسکتبال"
    },


    "volleyball": {
        "emoji": "🏐",
        "hashtag": "#والیبال"
    },


    "tennis": {
        "emoji": "🎾",
        "hashtag": "#تنیس"
    },


    "wrestling": {
        "emoji": "🤼",
        "hashtag": "#کشتی"
    },


    "formula1": {
        "emoji": "🏎",
        "hashtag": "#فرمول_یک"
    },


    "combat": {
        "emoji": "🥊",
        "hashtag": "#ورزش_رزمی"
    },


    "sport": {
        "emoji": "🏆",
        "hashtag": "#ورزش"
    }

}





# ==========================
# Sport Detection
# ==========================


SPORT_KEYWORDS = {


"football": [

    "فوتبال",
    "football",
    "soccer",

    "توپ فوتبال",
    "کفش فوتبال",
    "استوک",

    "دروازه",
    "تور دروازه",

    "گل",
    "گلزن",
    "پنالتی",

    "var",

    "بازیکن",
    "مهاجم",
    "مدافع",
    "هافبک",

    "منچستر",
    "رئال",
    "بارسلونا",
    "لیورپول",
    "آرسنال",

    "مسی",
    "رونالدو",
    "امباپه",
    "هالند"

],



"basketball": [

    "بسکتبال",
    "basketball",

    "توپ بسکتبال",

    "nba",
    "wnba",

    "دانک",
    "ریباند",

    "سه امتیازی",

    "زمین بسکتبال",

    "لیکرز",
    "واریرز",

    "کری",
    "لبران"

],




"volleyball": [

    "والیبال",
    "volleyball",

    "توپ والیبال",

    "fivb",

    "ست",

    "اسپک",

    "سرویس",

    "تور والیبال"

],




"tennis": [

    "تنیس",
    "tennis",

    "راکت تنیس",

    "atp",
    "wta",

    "گرند اسلم",

    "ویمبلدون",

    "رولان گاروس",

    "جوکوویچ",

    "آلکاراز"

],




"wrestling": [

    "کشتی",

    "کشتی آزاد",

    "کشتی فرنگی",

    "تشک کشتی",

    "uww",

    "مدال",

    "قهرمانی جهان",

    "حسن یزدانی"

],




"formula1": [

    "فرمول یک",

    "formula 1",

    "formula1",

    "f1",

    "گرندپری",

    "ماشین فرمول یک",

    "ورشتپن",

    "ردبول"

],




"combat": [

    "ufc",

    "mma",

    "بوکس",

    "boxing",

    "ناک اوت",

    "کمربند قهرمانی",

    "مبارزه"

]


}







# ==========================
# Main Function
# ==========================


def get_hashtag(category, title="", summary=""):


    text = f"{title} {summary}".lower()



    # اگر دسته ورزشی بود
    if category in [

        "sport",

        "football",

        "basketball",

        "volleyball",

        "tennis",

        "wrestling",

        "formula1",

        "combat"

    ]:



        # اگر دسته دقیق آمده باشد

        if category in SPORT_KEYWORDS:


            return {

                "emoji": HASHTAGS[category]["emoji"],

                "hashtag": HASHTAGS[category]["hashtag"],

                "sport_type": category

            }






        # تشخیص ورزش از متن

        for sport, words in SPORT_KEYWORDS.items():


            for word in words:


                if word.lower() in text:


                    return {

                        "emoji": HASHTAGS[sport]["emoji"],

                        "hashtag": HASHTAGS[sport]["hashtag"],

                        "sport_type": sport

                    }







        return {

            "emoji": HASHTAGS["sport"]["emoji"],

            "hashtag": HASHTAGS["sport"]["hashtag"],

            "sport_type": "general"

        }







    # دسته‌های عمومی


    data = HASHTAGS.get(

        category,

        HASHTAGS["world"]

    )


    return {


        "emoji": data["emoji"],

        "hashtag": data["hashtag"],

        "sport_type": None

    }
