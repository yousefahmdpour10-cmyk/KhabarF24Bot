import feedparser

def fetch_news(rss_url):
    feed = feedparser.parse(rss_url)

    news = []

    for entry in feed.entries:
        news.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", "")
        })

    return news
