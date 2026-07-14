from metadata import SOURCE_METADATA


def format_news(title, summary, source, category="world"):


    data = SOURCE_METADATA.get(source, {

        "country": "🌐",

        "hashtag": f"#{category}"

    })


    flag = data.get(
        "country",
        "🌐"
    )


    hashtag = data.get(
        "hashtag",
        f"#{category}"
    )



    category_names = {

        "world": "🌍 جهان",

        "iran": "🇮🇷 ایران",

        "sport": "🏅 ورزش",

        "technology": "💻 فناوری",

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
