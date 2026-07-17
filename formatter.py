"""
KhabarF24 Formatter v6.2

Fixed Telegram Style

Changes:
- Newspaper sticker 🗞️
- Correct source flags
- Keep source names
- Sport hashtag support
"""



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


    "gaming": {
        "name": "گیم",
        "emoji": "🎮",
        "hashtag": "#گیم"
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





# =========================
# Sources
# =========================


SOURCE_FLAGS = {


    "BBC World": "🇬🇧",

    "BBC Sport": "🇬🇧",

    "CNN World": "🇺🇸",

    "Reuters": "🇺🇸",

    "Sky Sports": "🇬🇧",

    "ESPN": "🇺🇸",

    "Al Jazeera": "🇶🇦",

    "العربیه": "🇸🇦",


    "کان اسرائیل": "🇮🇱",

    "Channel 12 Israel": "🇮🇱",


    "ایسنا": "🇮🇷",

    "تسنیم": "🇮🇷",

    "فارس": "🇮🇷",

    "خبر فوری": "🇮🇷",

    "ایران اینترنشنال": "🇬🇧",


    "دیجیاتو": "🇮🇷",

    "ویجیاتو": "🇮🇷",


    "FIFA": "🌐",

    "UEFA": "🇪🇺",

    "Premier League": "🇬🇧",

    "La Liga": "🇪🇸",

    "Bundesliga": "🇩🇪",

    "Serie A": "🇮🇹",

    "Di Marzio": "🇮🇹",

}






def get_source_flag(source):


    if not source:

        return "🌐"



    for name, flag in SOURCE_FLAGS.items():


        if name.lower() in source.lower():

            return flag



    return "🌐"







# =========================
# Sport
# =========================


def get_sport_style(sport):


    if not sport:

        return "⚽", "#ورزش"



    sport_type = sport.get(
        "type",
        ""
    )



    styles = {


        "football": (
            "⚽",
            "#فوتبال"
        ),


        "basketball": (
            "🏀",
            "#بسکتبال"
        ),


        "volleyball": (
            "🏐",
            "#والیبال"
        ),


        "tennis": (
            "🎾",
            "#تنیس"
        ),


        "wrestling": (
            "🤼",
            "#کشتی"
        ),


        "formula1": (
            "🏎",
            "#فرمول_یک"
        ),

    }



    return styles.get(

        sport_type,

        (
            "⚽",
            "#ورزش"
        )

    )








def format_sport_section(sport):


    if not sport:

        return ""



    text = ""



    if sport.get("score"):

        text += f"""

⚽ {sport['score']}
"""



    if sport.get("yellow_cards"):

        text += f"""

🟨 {sport['yellow_cards']}
"""



    if sport.get("red_cards"):

        text += f"""

🟥 {sport['red_cards']}
"""



    if sport.get("lineup"):

        text += f"""

👥 {sport['lineup']}
"""



    if sport.get("interview"):

        text += f"""

🎙️ {sport['interview']}
"""



    return text.strip()







def format_game_section(game):


    if not game:

        return ""



    text = ""



    if game.get("details"):

        text += f"""

🎮 {game['details']}
"""



    if game.get("release"):

        text += f"""

📅 {game['release']}
"""



    return text.strip()







# =========================
# Final Formatter
# =========================


def format_news(

        title,

        summary,

        source,

        category,

        sport=None,

        game=None

):


    style = CATEGORY_STYLE.get(

        category,

        CATEGORY_STYLE["world"]

    )



    hashtag = style["hashtag"]

    emoji = style["emoji"]

    name = style["name"]





    if category == "sport":


        sport_emoji, sport_hash = get_sport_style(

            sport

        )


        emoji = sport_emoji

        name = sport_hash.replace(

            "#",

            ""

        )


        hashtag = sport_hash





    flag = get_source_flag(

        source

    )





    extra = ""



    if category == "sport":

        extra = format_sport_section(

            sport

        )



    if category == "gaming":

        extra = format_game_section(

            game

        )







    message = f"""
━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {emoji} {name}
━━━━━━━━━━━━━━━━

📰 {title}


✍️ {summary}
"""





    if extra:


        message += f"""

{extra}
"""







    message += f"""



🗞️ {flag} {source}



━━━━━━━━━━━━━━━━
📢 @KhabarF24

{hashtag}
"""



    return message.strip()
