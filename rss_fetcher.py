import feedparser


def fetch_news(rss_url):
    feed = feedparser.parse(rss_url)

    if feed.bozo:
        print(f"RSS Parse Error: {rss_url}")

    news = []

    for entry in feed.entries:
        news.append({
            "title": entry.get("title", "").strip(),
            "link": entry.get("link", "").strip(),
            "summary": entry.get("summary", "").strip()
        })

    return news
