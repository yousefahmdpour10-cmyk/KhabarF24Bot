"""
KhabarF24 Formatter v6.0

Final Post Format

Header
Title
Summary
Source
Divider
Channel ID
Hashtag
"""


from metadata import get_source_flag
from sport_rules import detect_sport_type





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


    "gaming": {

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






def get_sport_category(title, summary):


    sport = detect_sport_type(

        title,

        summary

    )


    if sport:


        return {


            "title":
                f"{sport['emoji']} {sport['type']}",


            "hashtag":
                sport["hashtag"]

        }



    return {


        "title":
            "🏅 ورزش",


        "hashtag":
            "#ورزش"

    }







def format_news(

        title,

        summary,

        source,

        category="world",

        sport=None

):



    # دسته‌بندی


    if category == "sport":


        category_data = get_sport_category(

            title,

            summary

        )


    else:


        category_data = get_category_data(

            category

        )




    header = category_data["title"]


    hashtag = category_data["hashtag"]




    # منبع


    flag = get_source_flag(

        source

    )


    source_line = (

        f"🗞️ {flag} {source}."

    )





    return f"""
━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {header}
━━━━━━━━━━━━━━━━

📰 {title}

✍️ {summary}

{source_line}

━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
""".strip()
