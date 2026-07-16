"""
KhabarF24 Formatter v6.0

Final Telegram Post Formatter

Features:
- Fixed KhabarF24 style
- Category header
- Summary sticker ✍️
- Source newspaper 🗞️
- Source flag
- Sport events
- Gaming details
- Channel footer
- Hashtags
"""



CATEGORY_STYLE = {


    "politics": {

        "title": "🔴 سیاست و امنیت",

        "emoji": "🔴",

        "hashtag": "#سیاست"

    },


    "iran": {

        "title": "🇮🇷 ایران",

        "emoji": "🇮🇷",

        "hashtag": "#ایران"

    },


    "world": {

        "title": "🌍 جهان",

        "emoji": "🌍",

        "hashtag": "#جهان"

    },


    "sport": {

        "title": "⚽ ورزش",

        "emoji": "⚽",

        "hashtag": "#ورزش"

    },


    "gaming": {

        "title": "🎮 گیم",

        "emoji": "🎮",

        "hashtag": "#گیم"

    },


    "technology": {

        "title": "💻 فناوری",

        "emoji": "💻",

        "hashtag": "#فناوری"

    },


    "economy": {

        "title": "💰 اقتصاد",

        "emoji": "💰",

        "hashtag": "#اقتصاد"

    },


    "health": {

        "title": "🏥 سلامت",

        "emoji": "🏥",

        "hashtag": "#سلامت"

    },


    "science": {

        "title": "🔬 علم",

        "emoji": "🔬",

        "hashtag": "#علم"

    },


    "weather": {

        "title": "🌦 هواشناسی",

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

    "Al Jazeera": "🇶🇦",

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

⚽ نتیجه:
{sport.get("score")}

"""



    if sport.get("yellow_cards"):


        text += f"""

🟨 کارت زرد:
{sport.get("yellow_cards")}

"""



    if sport.get("red_cards"):


        text += f"""

🟥 کارت قرمز:
{sport.get("red_cards")}

"""



    if sport.get("lineup"):


        text += f"""

👥 ترکیب:
{sport.get("lineup")}

"""



    if sport.get("interview"):


        text += f"""

🎙️ مصاحبه:
{sport.get("interview")}

"""



    return text.strip()







def format_game_section(game):


    if not game:

        return ""



    text = ""



    if game.get("details"):


        text += f"""

🎮 جزئیات بازی:
{game.get("details")}

"""



    if game.get("release"):


        text += f"""

📅 انتشار:
{game.get("release")}

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

🔴 KhabarF24 | {style['title']}



📰 {title}



✍️ {summary}

"""



    if extra:


        message += f"""



{extra}

"""



    message += f"""



🗞️ {source} {flag}



━━━━━━━━━━━━

📢 @KhabarF24

{style['hashtag']}

"""



    return message.strip()
