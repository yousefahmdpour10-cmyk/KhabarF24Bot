from rss_fetcher import fetch_news
from sources import RSS_SOURCES


def get_latest_news():

    news = []

    for source in RSS_SOURCES:

        try:
            news.extend(fetch_news(source))

        except Exception as e:
            print(f"RSS Error {source.get('name', '')}: {e}")

    return news
