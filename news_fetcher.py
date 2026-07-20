"""
KhabarF24 News Fetcher v7.2
Hybrid (RSS + Scraper) - Ready for AI Processor
"""

import feedparser
import html
import re

from sources import RSS_SOURCES, SCRAPER_SOURCES
from scraper_engine import scrape_source

print("📰 KhabarF24 News Fetcher v7.2 Hybrid Loaded")


# =====================================================
# Text Cleaner
# =====================================================
def clean_text(text):
    if not text:
        return ""

    if isinstance(text, list):
        text = " ".join(text)

    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_ads(text):
    if not text:
        return ""

    BAD_TEXTS = [
        "برای مشاهده ادامه خبر", "ادامه مطلب", "عضویت در کانال",
        "subscribe", "click here", "read more", "برای خواندن کامل"
    ]
    
    for bad in BAD_TEXTS:
        text = text.replace(bad, "")
    return text.strip()


# =====================================================
# RSS Fetch
# =====================================================
def fetch_rss_news(source):
    url = source.get("url", "")
    name = source.get("name", "Unknown")
    category = source.get("category", "world")

    if not url:
        return []

    news = []
    try:
        feed = feedparser.parse(url)
        
        for item in feed.entries[:8]:   # محدود به ۸ خبر
            title = clean_text(item.get("title", ""))
            summary = clean_text(item.get("summary", ""))
            content = clean_text(item.get("content", [{}])[0].get("value", summary) if isinstance(item.get("content"), list) else item.get("content", summary))
            link = item.get("link", "")

            if not title:
                continue

            news.append({
                "title": title,
                "summary": remove_ads(summary),
                "content": remove_ads(content),
                "link": link,
                "source": name,
                "category": category,
                "image_url": item.get("media_content", [{}])[0].get("url") if item.get("media_content") else None
            })

        if news:
            print(f"✅ RSS OK: {name} ({len(news)} news)")

    except Exception as e:
        print(f"⚠️ RSS Failed {name}: {e}")

    return news


# =====================================================
# Scraper Fetch
# =====================================================
def fetch_scraper_news(source):
    name = source.get("name", "Unknown")
    category = source.get("category", "world")

    try:
        result = scrape_source(source)
        news = []

        for item in result[:8]:
            title = clean_text(item.get("title", ""))
            summary = clean_text(item.get("summary", ""))
            content = clean_text(item.get("content", summary))
            link = item.get("link", "")

            if not title:
                continue

            news.append({
                "title": title,
                "summary": remove_ads(summary),
                "content": remove_ads(content),
                "link": link,
                "source": name,
                "category": category,
                "image_url": item.get("image_url") or item.get("image")
            })

        if news:
            print(f"✅ Scraper OK: {name} ({len(news)} news)")

        return news

    except Exception as e:
        print(f"⚠️ Scraper Failed {name}: {e}")
        return []


# =====================================================
# Hybrid Fetch
# =====================================================
def fetch_hybrid_news(source):
    """اول RSS، اگر خالی بود Scraper"""
    rss_news = fetch_rss_news(source)
    if rss_news:
        return rss_news

    print(f"🔄 Trying Scraper for: {source.get('name','Unknown')}")
    return fetch_scraper_news(source)


# =====================================================
# Main Function
# =====================================================
def get_latest_news():
    all_news = []

    # RSS Sources (Hybrid)
    for source in RSS_SOURCES:
        all_news.extend(fetch_hybrid_news(source))

    # Pure Scraper Sources
    for source in SCRAPER_SOURCES:
        all_news.extend(fetch_scraper_news(source))

    print(f"📥 Total news fetched: {len(all_news)}")
    return all_news
