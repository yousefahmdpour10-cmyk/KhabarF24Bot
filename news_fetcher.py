"""
KhabarF24 News Fetcher v7.1 Hybrid

Features:

- RSS First
- Scraper Fallback
- Content Extraction
- HTML Cleaning
- Source Protection
- AI Processor Ready

Pipeline:

Source
 ↓
RSS
 ↓
Scraper Fallback
 ↓
news_fetcher
 ↓
AI Processor
"""


import feedparser
import html
import re



from sources import (
    RSS_SOURCES,
    SCRAPER_SOURCES
)



from scraper_engine import (
    scrape_source
)





print("📰 KhabarF24 News Fetcher v7.1 Hybrid Loaded")





# =====================================================
# Text Cleaner
# =====================================================


def clean_text(text):


    if not text:

        return ""



    if isinstance(text, list):

        text = " ".join(text)



    text = html.unescape(text)



    text = re.sub(

        r"<[^>]+>",

        "",

        text

    )



    text = re.sub(

        r"\s+",

        " ",

        text

    )


    return text.strip()







# =====================================================
# Remove Ads
# =====================================================


BAD_TEXTS = [


    "برای مشاهده ادامه خبر",

    "ادامه مطلب",

    "عضویت در کانال",

    "subscribe",

    "click here",

    "read more",

]





def remove_ads(text):


    if not text:

        return ""



    for bad in BAD_TEXTS:


        text = text.replace(

            bad,

            ""

        )


    return text.strip()







# =====================================================
# RSS Fetch
# =====================================================


def fetch_rss_news(source):


    url = source.get(

        "url",

        ""

    )


    name = source.get(

        "name",

        "Unknown"

    )


    category = source.get(

        "category",

        "world"

    )



    if not url:

        return []



    news = []



    try:


        feed = feedparser.parse(

            url

        )



        if not feed.entries:


            raise Exception(

                "Empty RSS"

            )





        for item in feed.entries[:10]:


            title = clean_text(

                item.get(

                    "title",

                    ""

                )

            )



            summary = clean_text(

                item.get(

                    "summary",

                    ""

                )

            )



            content = clean_text(

                item.get(

                    "content",

                    summary

                )

            )



            link = item.get(

                "link",

                ""

            )




            if not title:

                continue




            news.append({

                "title": title,

                "summary": summary,

                "content": content,

                "link": link,

                "source": name,

                "category": category

            })




        if news:


            print(

                f"✅ RSS OK: {name}"

            )



    except Exception as e:


        print(

            f"⚠️ RSS Failed {name}: {e}"

        )



        return []




    return news
        # =====================================================
# Scraper Fetch
# =====================================================


def fetch_scraper_news(source):


    name = source.get(

        "name",

        "Unknown"

    )


    category = source.get(

        "category",

        "world"

    )


    try:


        result = scrape_source(

            source

        )



        news = []



        for item in result:



            title = clean_text(

                item.get(

                    "title",

                    ""

                )

            )



            summary = clean_text(

                item.get(

                    "summary",

                    ""

                )

            )



            content = clean_text(

                item.get(

                    "content",

                    summary

                )

            )



            link = item.get(

                "link",

                ""

            )



            if not title:

                continue



            news.append({

                "title": title,

                "summary": summary,

                "content": content,

                "link": link,

                "source": name,

                "category": category

            })





        if news:


            print(

                f"✅ Scraper OK: {name}"

            )



        return news




    except Exception as e:


        print(

            f"⚠️ Scraper Failed {name}: {e}"

        )


        return []









# =====================================================
# Hybrid Source Fetch
# =====================================================


def fetch_hybrid_news(source):


    """
    اول RSS
    اگر شکست خورد Scraper
    """



    rss_news = fetch_rss_news(

        source

    )



    if rss_news:


        return rss_news





    print(

        f"🔄 Trying Scraper: {source.get('name','Unknown')}"

    )



    return fetch_scraper_news(

        source

    )









# =====================================================
# Main Fetch
# =====================================================


def get_latest_news():


    news = []




    # =========================
    # RSS + Hybrid
    # =========================


    for source in RSS_SOURCES:



        news.extend(

            fetch_hybrid_news(

                source

            )

        )






    # =========================
    # Scraper Only
    # =========================


    for source in SCRAPER_SOURCES:



        news.extend(

            fetch_scraper_news(

                source

            )

        )






    return news
