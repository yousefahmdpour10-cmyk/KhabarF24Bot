"""
KhabarF24 Formatter v6.3

Fixed Telegram Style

Changes:
- 🗞️ Source sticker
- English source names preserved
- Correct source flags
- No "منبع:" text
- Sport hashtag compatibility
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
# Source Flags
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


    "Channel 12 Israel": "🇮🇱",

    "کان اسرائیل": "🇮🇱",


    "ISNA": "🇮🇷",

    "Tasnim": "🇮🇷",

    "Fars": "🇮🇷",

    "Khabar Fori": "🇮🇷",

    "Iran International": "🇬🇧",


    "Digikala": "🇮🇷",

    "Digiato": "🇮🇷",


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
# Sport Hashtag
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
            "🏎️",
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
        text += f"\n⚽ {sport['score']}\n"


    if sport.get("yellow_cards"):
        text += f"\n🟨 {sport['yellow_cards']}\n"


    if sport.get("red_cards"):
        text += f"\n🟥 {sport['red_cards']}\n"


    if sport.get("lineup"):
        text += f"\n👥 {sport['lineup']}\n"


    if sport.get("interview"):
        text += f"\n🎙️ {sport['interview']}\n"


    return text.strip()






def format_game_section(game):

    if not game:
        return ""


    text = ""


    if game.get("details"):
        text += f"\n🎮 {game['details']}\n"


    if game.get("release"):
        text += f"\n📅 {game['release']}\n"


    return text.strip()






# =========================
# Final Message
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


    emoji = style["emoji"]

    name = style["name"]

    hashtag = style["hashtag"]



    if category == "sport":


        emoji, hashtag = get_sport_style(
            sport
        )

        name = hashtag.replace(
            "#",
            ""
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
