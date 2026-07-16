"""
KhabarF24 Formatter v3.0

Telegram post formatter

Supports:
- World
- Iran
- Technology
- Economy
- Sport sub categories
"""


from metadata import SOURCE_METADATA





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









def get_sport_header(sport):


    if not sport:

        return None



    # خروجی sport_formatter v3


    name = sport.get(

        "name",

        "ورزش"

    )


    emoji = sport.get(

        "emoji",

        "🏅"

    )


    hashtag = sport.get(

        "hashtag",

        "#ورزش"

    )



    return {


        "title":

            f"{emoji} {name}",


        "hashtag":

            hashtag

    }









def format_news(

    title,

    summary,

    source,

    category="world",

    sport=None

):



    data = SOURCE_METADATA.get(

        source,

        {

            "country": "🌐"

        }

    )



    source_flag = data.get(

        "country",

        "🌐"

    )




    # اگر خبر ورزشی بود

    if category == "sport" and sport:


        category_data = get_sport_header(

            sport

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

🗞️ {source_flag} {source}

━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
"""
