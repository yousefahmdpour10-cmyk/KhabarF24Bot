"""
KhabarF24 Game Rules v1.0

وظیفه:
- تشخیص نوع خبرهای گیم
- تشخیص زیر دسته بازی
- آماده سازی برای Formatter

Categories:
🎮 گیم
"""



print("🎮 KhabarF24 Game Rules v1.0 Loaded")





GAME_TYPES = {


    "console": {

        "emoji": "🎮",

        "type": "کنسول",

        "hashtag": "#گیم"

    },


    "game_release": {

        "emoji": "🕹️",

        "type": "معرفی بازی",

        "hashtag": "#گیم"

    },


    "online_game": {

        "emoji": "🌐",

        "type": "بازی آنلاین",

        "hashtag": "#گیم"

    },


    "studio": {

        "emoji": "🏢",

        "type": "استودیو بازی",

        "hashtag": "#گیم"

    },


    "esport": {

        "emoji": "🏆",

        "type": "ورزش الکترونیک",

        "hashtag": "#گیم"

    }


}





GAME_KEYWORDS = {


    "console": [

        "playstation",

        "ps5",

        "ps4",

        "xbox",

        "nintendo",

        "کنسول",

        "پلی استیشن",

        "ایکس باکس",

        "نینتندو",

    ],



    "game_release": [

        "new game",

        "game release",

        "release date",

        "trailer",

        "gameplay",

        "معرفی بازی",

        "عرضه بازی",

        "تاریخ انتشار",

        "تریلر",

        "گیم پلی",

    ],




    "online_game": [

        "online game",

        "server",

        "update",

        "season",

        "آپدیت",

        "سرور",

        "فصل جدید",

        "بازی آنلاین",

    ],




    "studio": [

        "ubisoft",

        "electronic arts",

        "ea games",

        "rockstar",

        "valve",

        "استودیو",

        "شرکت بازی سازی",

        "شرکت بازی‌سازی",

    ],




    "esport": [

        "esports",

        "e sports",

        "مسابقات بازی",

        "ورزش الکترونیک",

        "قهرمانی بازی",

    ]

}







def contains_any(text, words):


    text = text.lower()


    for word in words:


        if word.lower() in text:

            return True


    return False







def detect_game_type(title="", summary=""):


    text = f"{title} {summary}"



    for game_type, keywords in GAME_KEYWORDS.items():


        if contains_any(text, keywords):


            return GAME_TYPES[game_type]



    return {


        "emoji": "🎮",

        "type": "گیم",

        "hashtag": "#گیم"

    }







def calculate_game_score(title="", summary=""):


    text = f"{title} {summary}".lower()


    score = 0



    important = [

        "هک",

        "تعطیلی سرور",

        "خرید شرکت",

        "عرضه رسمی",

        "نسخه جدید",

        "کنسول جدید",

        "جایزه",

        "آپدیت بزرگ",

    ]



    for word in important:


        if word in text:

            score += 2



    if score > 10:

        score = 10



    return score
