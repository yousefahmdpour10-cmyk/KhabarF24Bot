"""
KhabarF24 Formatter v5.0

Final Telegram Post Format

Features:
- Fixed KhabarF24 header
- Category emoji
- Newspaper title sticker
- Pen summary sticker
- Source + flag
- Channel ID
- Hashtag
- Sport events support
"""


# ==========================
# دسته‌ها
# ==========================


CATEGORY_STYLE = {


    "politics": {
        "name": "سیاست و امنیت",
        "emoji": "🔴",
        "hashtag": "#سیاست"
    },


    "iran": {
        "name": "ایران",
        "emoji": "🇮🇷",
        "hashtag": "#ایران"
    },


    "world": {
        "name": "جهان",
        "emoji": "🌍",
        "hashtag": "#جهان"
    },


    "sport": {
        "name": "ورزش",
        "emoji": "⚽",
        "hashtag": "#ورزش"
    },


    "technology": {
        "name": "فناوری",
        "emoji": "💻",
        "hashtag": "#فناوری"
    },


    "economy": {
        "name": "اقتصاد",
        "emoji": "💰",
        "hashtag": "#اقتصاد"
    },


    "gaming": {
        "name": "گیم",
        "emoji": "🎮",
        "hashtag": "#گیم"
    },


    "health": {
        "name": "سلامت",
        "emoji": "🏥",
        "hashtag": "#سلامت"
    },


    "science": {
        "name": "علم",
        "emoji": "🔬",
        "hashtag": "#علم"
    },


    "weather": {
        "name": "هواشناسی",
        "emoji": "🌦",
        "hashtag": "#هواشناسی"
    },


}



# ==========================
# پرچم منابع
# ==========================


SOURCE_FLAGS = {


    "BBC": "🇬🇧",

    "CNN": "🇺🇸",

    "Reuters": "🇺🇸",

    "ESPN": "🇺🇸",

    "Sky Sports": "🇬🇧",

    "Al Jazeera": "🇶🇦",

    "العربیه": "🇸🇦",

    "ایسنا": "🇮🇷",

    "تسنیم": "🇮🇷",

    "فارس": "🇮🇷",

    "خبر فوری": "🇮🇷",

    "ایران اینترنشنال": "🇬🇧",

}





def get_source_flag(source):


    if not source:

        return "🌐"



    for name, flag in SOURCE_FLAGS.items():


        if name.lower() in source.lower():

            return flag



    return "🌐"







# ==========================
# پاکسازی
# ==========================


def clean_text(text):


    if not text:

        return ""



    return text.strip()







# ==========================
# اطلاعات ورزش
# ==========================


def format_sport_events(sport):


    if not sport:

        return ""



    events = sport.get(
        "events",
        {}
    )



    output = ""



    if events.get("score"):

        output += (
            "\n\n"
            + events["score"]
        )



    if events.get("goals"):

        output += (
            "\n"
            + events["goals"]
        )



    if events.get("yellow"):

        output += (
            "\n"
            + events["yellow"]
        )



    if events.get("red"):

        output += (
            "\n"
            + events["red"]
        )



    if events.get("lineup"):

        output += (
            "\n"
            + events["lineup"]
        )



    if events.get("interview"):

        output += (
            "\n"
            + events["interview"]
        )



    return output







# ==========================
# ساخت پست
# ==========================


def format_news(
        title,
        summary,
        source,
        category,
        sport=None
):


    style = CATEGORY_STYLE.get(

        category,

        CATEGORY_STYLE["world"]

    )



    title = clean_text(title)

    summary = clean_text(summary)



    header = (

        f"{style['emoji']} KhabarF24 | "
        f"{style['emoji']} {style['name']}"

    )



    message = (

        header

        + "\n━━━━━━━━━━━━━━━━\n\n"

        + "📰 "

        + title

        + "\n\n"

        + "✍️ "

        + summary

    )





    # ورزش

    if category == "sport" and sport:


        message += format_sport_events(

            sport

        )





    # منبع

    flag = get_source_flag(

        source

    )



    message += (

        "\n\n"

        + "🗞️ منبع: "

        + source

        + " "

        + flag

    )





    # پایین پست


    message += (

        "\n\n━━━━━━━━━━━━\n"

        "📢 @KhabarF24\n"

        + style["hashtag"]

    )



    return message
