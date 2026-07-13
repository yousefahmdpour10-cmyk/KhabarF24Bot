from metadata import SOURCE_METADATA


def format_news(title, summary, source):

    data = SOURCE_METADATA.get(source, {
        "country": "🌐",
        "sticker": "📰",
        "hashtag": "#خبر"
    })

    sticker = data["sticker"]
    flag = data["country"]
    hashtag = data["hashtag"]

    return f"""{sticker}

📰 {title}

✍️ {summary}

🗞️ {flag} {source}

━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
"""
