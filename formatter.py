def format_news(news):

    category = news.get("category", "🌍 جهان")
    source = news.get("source", "منبع نامشخص")

    message = f"""{category}

📰 {news["title"]}

🗞 {source}

📢 @KhabarF24

━━━━━━━━━━━━

#خبر
"""

    return message
