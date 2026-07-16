"""
KhabarF24 Formatter v5.0

Telegram post formatter

Rules:
- Persian category names
- Source before divider
- Channel id and hashtag only after divider
- Sport categories supported
- Game and weather ready
"""


from metadata import SOURCE_METADATA


from sport_formatter import detect_sport






CATEGORY_NAMES = {


    "world": {
        "title": "🌍 جهان",
        "hashtag": "#جهان"
    },


    "iran": {
        "title": "🇮🇷 ایران",
        "hashtag": "#ایران"
    },


    "technology": {
        "title": "💻 فناوری",
        "hashtag": "#تکنولوژی"
    },


    "economy": {
        "title": "💰 اقتصاد",
        "hashtag": "#اقتصاد"
    },


    "health": {
        "title": "❤️ سلامت",
        "hashtag": "#سلامت"
    },


    "science": {
        "title": "🔬 علم",
        "hashtag": "#علم"
    },


    "weather": {
        "title": "🌦️ هواشناسی",
        "hashtag": "#هواشناسی"
    },


    "game": {
        "title": "🎮 گیم",
        "hashtag": "#گیم"
    },


    "sport": {
        "title": "🏅 ورزش",
        "hashtag": "#ورزش"
    }

}






def get_category_data(category):


    return CATEGORY_NAMES.get(

        category,

        CATEGORY_NAMES["world"]

    )








def get_sport_data(title, summary):


    sport = detect_sport(

        title,

        summary

    )



    if not sport:


        return {

            "title": "🏅 ورزش",

            "hashtag": "#ورزش"

        }




    return {


        "title":

            f"{sport['emoji']} {sport['name']}",



        "hashtag":

            sport["hashtag"]

    }









def format_news(

    title,

    summary,

    source,

    category="world",

    sport=None

):


    source_data = SOURCE_METADATA.get(

        source,

        {

            "country": "🌐"

        }

    )



    source_flag = source_data.get(

        "country",

        "🌐"

    )






    if category == "sport":


        category_data = get_sport_data(

            title,

            summary

        )


    else:


        category_data = get_category_data(

            category

        )





    header = category_data["title"]

    hashtag = category_data["hashtag"]






    return f"""━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {header}
━━━━━━━━━━━━━━━━

📰 {title}

✍️ {summary}

🗞️ • {source_flag} {source}

━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
"""
