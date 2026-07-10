from rss_fetcher import fetch_news
from sources import RSS_SOURCES

def get_latest_news():
    news = []

    for url in RSS_SOURCES["world"]:
        try:
            news.extend(fetch_news(url))
        except Exception as e:
            print(f"RSS Error: {e}")

    return news
