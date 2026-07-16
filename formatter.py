"""
KhabarF24 Formatter v2.1

Features:
- Sport formatter connection
- Correct hashtags by category
- Telegram post format
"""


from metadata import SOURCE_METADATA


from sport_formatter import format_sport_news





CATEGORY_NAMES = {

    "world": "🌍 جهان",

    "iran": "🇮🇷 ایران",

    "sport": "🏅 ورزش",

    "technology": "💻 فناوری",

    "economy": "💰 اقتصاد",

    "health": "❤️ سلامت",

    "science": "🔬 علم",

    "weather": "🌦️ هواشناسی",

}





CATEGORY_HASHTAGS = {

    "world": "#جهان",

    "iran": "#ایران",

    "sport": "#ورزش",

    "technology": "#تکنولوژی",

    "economy": "#اقتصاد",

    "health": "#سلامت",

    "science": "#علم",

    "weather": "#هواشناسی",

}





def format_news(title, summary, source, category="world"):



    sport_type = ""



    # =====================
    # Sport Formatter
    # =====================

    if category == "sport":


        sport_result = format_sport_news(

            title,

            summary

        )


        title = sport_result.get(

            "title",

            title

        )


        summary = sport_result.get(

            "summary",

            summary

        )


        sport_type = sport_result.get(

            "sport_type",

            ""

        )







    # =====================
    # Source
    # =====================


    source_data = SOURCE_METADATA.get(

        source,

        {}

    )



    source_flag = source_data.get(

        "country",

        "🌐"

    )







    header = CATEGORY_NAMES.get(

        category,

        "🌍 جهان"

    )



    hashtag = CATEGORY_HASHTAGS.get(

        category,

        "#جهان"

    )







    extra = ""


    if sport_type:


        extra = f"\n{sport_type}\n"








    message = f"""━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {header}
━━━━━━━━━━━━━━━━
{extra}
📰 {title}

✍️ {summary}

🗞️ {source_flag} {source}

━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
"""



    return message
