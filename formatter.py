from metadata import SOURCE_METADATA


def format_news(title, summary, source):

    data = SOURCE_METADATA.get(
        source,
        {
            "country": "🌐",
            "sticker": "📰",
            "hashtag": "#خبر"
        }
    )

    flag = data["country"]
    sticker = data["sticker"]
    hashtag = data["hashtag"]

    category_name = hashtag.replace("#", "")

    title = (title or "").strip()
    summary = (summary or "").strip()

    if not summary:
        summary = "جزئیات بیشتر به‌زودی..."

    return f"""━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {sticker} {category_name}
━━━━━━━━━━━━━━━━

📰 {title}

✍️ {summary}

🗞️ {flag} {source}

━━━━━━━━━━━━
📢 @KhabarF24
{hashtag}
"""
