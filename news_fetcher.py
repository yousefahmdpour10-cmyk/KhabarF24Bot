"""
KhabarF24 News Fetcher v8.0
Hybrid RSS + Scraper - Optimized for Main Engine
"""

import feedparser
import html
import re
import logging
from typing import List, Dict

from sources import RSS_SOURCES, SCRAPER_SOURCES
from scraper_engine import scrape_source

logger = logging.getLogger(__name__)

print("📰 KhabarF24 News Fetcher v8.0 Loaded")


# =====================================================
# Text Cleaner
# =====================================================
def clean_text(text):
    if not text:
        return ""
    
    if isinstance(text, list):
        text = " ".join(str(t) for t in text)

    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)      # Remove HTML tags
    text = re.sub(r"\s+", " ", text)         # Normalize whitespace
    return text.strip()


def remove_ads(text: str) -> str:
    if not text:
        return ""

    BAD_PHRASES = [
        "برای مشاهده ادامه خبر", "ادامه مطلب", "عضویت در کانال",
        "subscribe", "click here", "read more", "برای خواندن کامل",
        "این خبر ادامه دارد", "جزئیات بیشتر"
    ]
    
    for phrase in BAD_PHRASES:
        text = text.replace(phrase, "")
    return text.strip()


# =====================================================
# RSS Fetch
# =====================================================
def fetch_rss_news(source: Dict) -> List[Dict]:
    url = source.get("url", "")
    name = source.get("name", "Unknown")
    category = source.get("category", "world")

    if not url:
        return []

    try:
        feed = feedparser.parse(url)
        news = []

        for item in feed.entries[:10]:   # افزایش به ۱۰
            title = clean_text(item.get("title", ""))
            if not title:
                continue

            summary = clean_text(item.get("summary", ""))
            content = clean_text(
                item.get("content", [{}])[0].get("value") 
                if isinstance(item.get("content"), list) 
                else item.get("content", summary)
            )

            news.append({
                "title": title,
                "summary": remove_ads(summary),
                "content": remove_ads(content),
                "link": item.get("link", ""),
                "source": name,
                "category": category,
                "image_url": item.get("media_content", [{}])[0].get("url") 
                            if item.get("media_content") else None,
                "published": item.get("published", "")
            })

        if news:
            logger.info(f"✅ RSS: {name} → {len(news)} news")
        return news

    except Exception as e:
        logger.error(f"⚠️ RSS Failed {name}: {e}")
        return []


# =====================================================
# Scraper Fetch
# =====================================================
def fetch_scraper_news(source: Dict) -> List[Dict]:
    name = source.get("name", "Unknown")
    category = source.get("category", "world")

    try:
        result = scrape_source(source)
        news = []

        for item in result[:8]:
            title = clean_text(item.get("title", ""))
            if not title:
                continue

            summary = clean_text(item.get("summary", ""))
            content = clean_text(item.get("content", summary))

            news.append({
                "title": title,
                "summary": remove_ads(summary),
                "content": remove_ads(content),
                "link": item.get("link", ""),
                "source": name,
                "category": category,
                "image_url": item.get("image_url") or item.get("image"),
                "published": item.get("published", "")
            })

        if news:
            logger.info(f"✅ Scraper: {name} → {len(news)} news")
        return news

    except Exception as e:
        logger.error(f"⚠️ Scraper Failed {name}: {e}")
        return []


# =====================================================
# Hybrid + Main Function
# =====================================================
def fetch_hybrid_news(source: Dict) -> List[Dict]:
    """اول RSS امتحان کن، اگر خبر نیاورد Scraper"""
    rss_news = fetch_rss_news(source)
    if rss_news:
        return rss_news

    logger.info(f"🔄 Switching to Scraper for: {source.get('name')}")
    return fetch_scraper_news(source)


def get_latest_news() -> List[Dict]:
    """Main entry point - returns all fresh news"""
    all_news = []

    # RSS Sources (Hybrid)
    for source in RSS_SOURCES:
        all_news.extend(fetch_hybrid_news(source))

    # Pure Scraper Sources
    for source in SCRAPER_SOURCES:
        all_news.extend(fetch_scraper_news(source))

    logger.info(f"📥 Total news fetched: {len(all_news)}")
    return all_news
