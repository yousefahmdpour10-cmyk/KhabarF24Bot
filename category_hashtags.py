"""
KhabarF24 Category Hashtag Engine v1.0

وظیفه:
- تعیین هشتک مناسب خبر
- تشخیص رشته ورزشی
- خروجی استاندارد برای Formatter
"""


print("🏷️ KhabarF24 Hashtag Engine Loaded")



HASHTAGS = {


    "politics":
        "#سیاست",


    "iran":
        "#ایران",


    "world":
        "#جهان",


    "technology":
        "#فناوری",


    "gaming":
        "#گیم",


    "economy":
        "#اقتصاد",


    "health":
        "#سلامت",


    "science":
        "#علم",


    "weather":
        "#هواشناسی",


    "football":
        "#فوتبال",


    "basketball":
        "#بسکتبال",


    "tennis":
        "#تنیس",


    "volleyball":
        "#والیبال",


    "wrestling":
        "#کشتی",


    "formula1":
        "#فرمول_یک",


    "combat":
        "#ورزش_رزمی",


    "sport":
        "#ورزش",


}




SPORT_KEYWORDS = {


    "football": [

        "فوتبال",
        "football",
        "soccer",

        "فیفا",
        "fifa",

        "یوفا",
        "uefa",

        "جام جهانی",

        "لیگ قهرمانان",

        "premier league",
        "la liga",
        "serie a",
        "bundesliga",

        "گل",
        "پنالتی",
        "var",

        "منچستر",
        "رئال",
        "بارسلونا",
        "لیورپول",

        "مسی",
        "رونالدو",
        "امباپه",
        "هالند",

    ],



    "basketball": [

        "بسکتبال",
        "basketball",

        "nba",
        "wnba",

        "دانک",
        "ریباند",

        "سه امتیازی",

        "لیکرز",
        "بوستون",

        "استفن کری",

    ],



    "tennis": [

        "تنیس",
        "tennis",

        "atp",
        "wta",

        "گرند اسلم",

        "ویمبلدون",

        "رولان گاروس",

        "جوکوویچ",

        "آلکاراز",

    ],



    "volleyball": [

        "والیبال",
        "volleyball",

        "fivb",

        "لیگ ملت‌ها",

        "اسپک",

        "سرویس",

    ],



    "wrestling": [

        "کشتی",

        "کشتی آزاد",

        "کشتی فرنگی",

        "uww",

        "قهرمانی جهان",

        "مدال",

        "حسن یزدانی",

    ],



    "formula1": [

        "فرمول یک",

        "formula 1",

        "formula1",

        "f1",

        "گرندپری",

        "ورشتپن",

        "ردبول",

    ],



    "combat": [

        "ufc",

        "mma",

        "بوکس",

        "boxing",

        "ناک اوت",

        "کمربند قهرمانی",

    ],

}





def get_hashtag(category, title="", summary=""):


    text = f"{title} {summary}".lower()



    # اول ورزش‌های تخصصی

    if category == "sport":


        for sport, words in SPORT_KEYWORDS.items():


            for word in words:


                if word.lower() in text:


                    return {


                        "category": "sport",


                        "sport_type": sport,


                        "hashtag": HASHTAGS[sport]


                    }



        return {


            "category": "sport",

            "sport_type": "general",

            "hashtag": HASHTAGS["sport"]

        }





    # دسته‌های عمومی


    return {


        "category": category,


        "sport_type": None,


        "hashtag": HASHTAGS.get(

            category,

            "#خبر"

        )

    }
