"""
KhabarF24 Scraper Engine v8.0
Smart Scraping with Retry + Anti-Block
"""

import requests
from bs4 import BeautifulSoup
import html
import re
import time
import logging
import random
from typing import List, Dict

logger = logging.getLogger(__name__)

print("🌐 KhabarF24 Scraper Engine v8.0 Loaded")


# =====================================================
# HTTP Session
# =====================================================
SESSION = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
    "Referer": "https://www.google.com/",
}

SESSION.headers.update(HEADERS)


# =====================================================
# Cleaners
# =====================================================
def clean_text(text):
    if not text:
        return ""
    text = html.unescape(str(text))
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def valid_title(title: str) -> bool:
    if not title or len(title) < 25:
        return False
    low = title.lower()
    noise = ["login", "subscribe", "newsletter", "cookie", "advertisement", "menu", "share", "کلیه حقوق"]
    return not any(word in low for word in noise)


# =====================================================
# Request with Retry
# =====================================================
def get_page(url: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = SESSION.get(url, timeout=15, allow_redirects=True)
            
            if response.status_code == 403:
                logger.warning(f"🚫 403 Blocked: {url}")
                time.sleep(2)
                continue
                
            response.raise_for_status()
            return response.text

        except Exception as e:
            logger.warning(f"⚠️ Scrape attempt {attempt+1} failed for {url}: {e}")
            time.sleep(random.uniform(1.5, 3.5))
    
    return ""


# =====================================================
# Extract Articles
# =====================================================
def extract_articles(page: str, base_url: str) -> List[Dict]:
    if not page:
        return []
    
    soup = BeautifulSoup(page, "lxml")
    results = []

    for a in soup.find_all("a", href=True):
        title = clean_text(a.get_text())
        link = a["href"]

        if not valid_title(title):
            continue

        if not link.startswith("http"):
            link = base_url.rstrip("/") + "/" + link.lstrip("/")

        results.append({"title": title, "link": link})

    return results


# =====================================================
# Extract Content
# =====================================================
def extract_content(url: str) -> str:
    page = get_page(url)
    if not page:
        return ""

    soup = BeautifulSoup(page, "lxml")
    paragraphs = []

    for p in soup.find_all("p"):
        text = clean_text(p.get_text())
        if len(text) > 40:
            paragraphs.append(text)
        if len(paragraphs) >= 4:   # حداکثر ۴ پاراگراف
            break

    return " ".join(paragraphs)


# =====================================================
# Main Scraper
# =====================================================
def scrape_source(source: Dict) -> List[Dict]:
    url = source.get("url", "")
    name = source.get("name", "Unknown")
    category = source.get("category", "world")

    if not url:
        return []

    logger.info(f"🌐 Scraping: {name}")

    page = get_page(url)
    if not page:
        return []

    articles = extract_articles(page, url)
    news = []

    for article in articles[:8]:   # محدود به ۸ خبر
        content = extract_content(article["link"])
        summary = content[:320] if content else ""

        news.append({
            "title": article["title"],
            "summary": summary,
            "content": content,
            "link": article["link"],
            "source": name,
            "category": category,
            "image_url": None   # بعداً قابل گسترش
        })

    logger.info(f"✅ Scraped {len(news)} news from {name}")
    return news


# Fallback
def scrape_with_fallback(source: Dict) -> List[Dict]:
    try:
        return scrape_source(source)
    except Exception as e:
        logger.error(f"Scraper failed for {source.get('name')}: {e}")
        return []
