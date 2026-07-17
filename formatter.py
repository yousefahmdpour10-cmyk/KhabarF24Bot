"""
KhabarF24 Formatter v6.1

Fixed Telegram Style
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



SOURCE_FLAGS = {

    "BBC": "🇬🇧",
    "CNN": "🇺🇸",
    "Reuters": "🇺🇸",
    "Sky Sports": "🇬🇧",
    "ESPN": "🇺🇸",
    "العربیه": "🇸🇦",
    "کان اسرائیل": "🇮🇱",
    "کان 12": "🇮🇱",

    "ایسنا": "🇮🇷",
    "تسنیم": "🇮🇷",
    "فارس": "🇮🇷",
    "خبر فوری": "🇮🇷",

    "دیجیاتو": "🇮🇷",
    "ویجیاتو": "🇮🇷",

}




def get_source_flag(source):

    if not source:
        return "🌐"


    for name, flag in SOURCE_FLAGS.items():

        if name.lower() in source.lower():

            return flag


    return "🌐"






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


    flag = get_source_flag(source)



    extra = ""



    if category == "sport":

        extra = format_sport_section(sport)



    if category == "gaming":

        extra = format_game_section(game)




    message = f"""
━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {style['emoji']} {style['name']}
━━━━━━━━━━━━━━━━

📰 {title}


✍️ {summary}
"""



    if extra:

        message += f"""

{extra}
"""



    message += f"""

📰 {source} {flag}.

━━━━━━━━━━━━━━━━
📢 @KhabarF24

{style['hashtag']}
"""


    return message.strip()
