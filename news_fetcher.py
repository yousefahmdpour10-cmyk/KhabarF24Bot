from rss_fetcher import fetch_news
from sources import RSS_SOURCES


def get_latest_news():

    news = []

    for category in RSS_SOURCES.values():

        for url in category:

            try:
                news.extend(fetch_news(url))

            except Exception as e:
                print(f"RSS Error: {e}")

    return news
