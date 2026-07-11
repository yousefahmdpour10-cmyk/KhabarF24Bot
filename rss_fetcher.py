import feedparser


def fetch_news(rss_url):

    feed = feedparser.parse(rss_url)

    if feed.bozo:
        print(f"RSS Parse Error: {rss_url}")

    news = []

    for entry in feed.entries:

        source = ""

        if "source" in entry:
            source = entry.source.get("title", "").strip()

        if not source:
            source = feed.feed.get("title", "").strip()

        news.append({

            "title": entry.get("title", "").strip(),

            "link": entry.get("link", "").strip(),

            "summary": entry.get("summary", "").strip(),

            "source": source

        })

    return news
