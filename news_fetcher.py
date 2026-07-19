"""
KhabarF24 News Fetcher v7.0

Features:

- RSS Support
- Scraper Support
- Content Extraction
- HTML Cleaning
- Source Protection
- AI Ready Output

Pipeline:

RSS / Scraper
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





print("📰 KhabarF24 News Fetcher v7.0 Loaded")





# =====================================================
# Text Cleaner
# =====================================================


def clean_text(text):


    if not text:

        return ""



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
# Remove Ads / Website Noise
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


    news = []



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



    try:


        feed = feedparser.parse(

            url

        )



     for item in feed.entries[:10]:
             
if isinstance(item.get("title"), list):
    continue

if isinstance(item.get("summary"), list):
    item["summary"] = " ".join(item["summary"])

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

                    ""

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


                "summary": remove_ads(summary),


                "content": remove_ads(content),


                "link": link,


                "source": name,


                "category": category


            })



    except Exception as e:


        print(

            f"RSS ERROR {name}: {e}"

        )



    return news







# =====================================================
# Scraper Fetch
# =====================================================


def fetch_scraper_news(source):


    try:


        result = scrape_source(

            source

        )



        cleaned = []



        for item in result:



            cleaned.append({


                "title":

                    clean_text(

                        item.get(

                            "title",

                            ""

                        )

                    ),


                "summary":

                    clean_text(

                        item.get(

                            "summary",

                            ""

                        )

                    ),



                "content":

                    clean_text(

                        item.get(

                            "content",

                            ""

                        )

                    ),



                "link":

                    item.get(

                        "link",

                        ""

                    ),



                "source":

                    source.get(

                        "name",

                        "Unknown"

                    ),



                "category":

                    source.get(

                        "category",

                        "world"

                    )


            })



        return cleaned



    except Exception as e:


        print(

            f"SCRAPER ERROR: {e}"

        )


        return []







# =====================================================
# Main Fetch
# =====================================================


def get_latest_news():


    news = []



    # RSS


    for source in RSS_SOURCES:


        news.extend(

            fetch_rss_news(

                source

            )

        )





    # SCRAPER


    for source in SCRAPER_SOURCES:


        news.extend(

            fetch_scraper_news(

                source

            )

        )





    return news
