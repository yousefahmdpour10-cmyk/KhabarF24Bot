import feedparser


def fetch_news(source_info):

    rss_url = source_info["url"]
    source_name = source_info["name"]
    category = source_info["category"]

    feed = feedparser.parse(rss_url)

    if feed.bozo:
        print(f"RSS Parse Error: {rss_url}")

    news = []

    for entry in feed.entries:

        news.append({
            "title": entry.get("title", "").strip(),

            "link": entry.get("link", "").strip(),

            "summary": entry.get("summary", "").strip(),

            # اطلاعات منبع برای هوشمندی ربات
            "source": source_name,

            # دسته‌بندی از قبل مشخص شده
            "category": category
        })

    return news
