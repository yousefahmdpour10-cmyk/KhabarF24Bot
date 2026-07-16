"""
KhabarF24 Formatter v2.0

ویژگی‌ها:
- اتصال موتور اختصاصی ورزش
- هشتگ بر اساس دسته خبر
- حفظ فرمت کانال
"""


from metadata import SOURCE_METADATA


from sport_formatter import format_sport_news





def format_news(title, summary, source, category="world"):



    # =====================
    # Sport Engine
    # =====================

    sport_type = ""


    if category == "sport":


        sport_data = format_sport_news(

            title,

            summary

        )


        title = sport_data.get(

            "title",

            title

        )


        summary = sport_data.get(

            "summary",

            summary

        )


        sport_type = sport_data.get(

            "sport_type",

            ""

        )







    # =====================
    # Source Metadata
    # =====================


    data = SOURCE_METADATA.get(source, {

        "country": "🌐"

    })



    flag = data.get(

        "country",

        "🌐"

    )






    # =====================
    # Category
    # =====================


    category_names = {


        "world":

        "🌍 جهان",


        "iran":

        "🇮🇷 ایران",


        "sport":

        "🏅 ورزش",


        "technology":

        "💻 فناوری",


        "economy":

        "💰 اقتصاد",


        "health":

        "❤️ سلامت",


        "science":

        "🔬 علم",


        "weather":

        "🌦️ هواشناسی",

    }



    header = category_names.get(

        category,

        "🌍 جهان"

    )







    # =====================
    # Hashtag Engine
    # =====================


    hashtags = {


        "world":

        "#جهان",


        "iran":

        "#ایران",


        "sport":

        "#ورزش",


        "technology":

        "#تکنولوژی",


        "economy":

        "#اقتصاد",


        "health":

        "#سلامت",


        "science":

        "#علم",


        "weather":

        "#هواشناسی",

    }



    hashtag = hashtags.get(

        category,

        "#جهان"

    )







    sport_line = ""

    if sport_type:


        sport_line = (

            f"\n{sport_type}\n"

        )








    return f"""━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {header}
━━━━━━━━━━━━━━━━
{sport_line}
📰 {title}

✍️ {summary}

🗞️ {flag} {source}

━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
"""        "technology": "💻 فناوری",

        "economy": "💰 اقتصاد",

        "health": "❤️ سلامت",

        "science": "🔬 علم",

        "weather": "🌦️ هواشناسی",

    }



    header = category_names.get(
        category,
        "🌍 جهان"
    )



    return f"""━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {header}
━━━━━━━━━━━━━━━━

📰 {title}

✍️ {summary}

🗞️ {flag} {source}

━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
"""
