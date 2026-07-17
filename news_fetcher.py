"""
KhabarF24 News Fetcher v6.4

وظیفه:
- دریافت خبر از RSS
- دریافت خبر از Scraper
- استاندارد سازی خروجی
- نگهداری نام منبع
- آماده سازی برای AI / Category / Formatter
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





# =========================
# Clean Text
# =========================


def clean_text(text):


    if not text:

        return ""



    text = html.unescape(text)



    text = re.sub(

        r"<.*?>",

        "",

        text

    )



    text = re.sub(

        r"\s+",

        " ",

        text

    )



    return text.strip()







# =========================
# RSS Fetch
# =========================


def fetch_rss_news(source):


    if not source:

        return []



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



            link = item.get(

                "link",

                ""

            )




            if not title:

                continue



            news.append({


                "title": title,


                "summary": summary,


                "link": link,


                "source": name,


                "category": category


            })



    except Exception as e:


        print(

            f"RSS Error {name}: {e}"

        )



    return news







# =========================
# Scraper Fetch
# =========================


def fetch_scraper_news(source):


    try:


        return scrape_source(

            source

        )



    except Exception as e:


        print(

            f"Scraper Error {source.get('name','')}: {e}"

        )


        return []









# =========================
# Main Fetch Engine
# =========================


def get_latest_news():


    news = []



    # RSS


    for source in RSS_SOURCES:


        try:


            news.extend(

                fetch_rss_news(

                    source

                )

            )



        except Exception as e:


            print(

                f"RSS Source Error: {e}"

            )







    # SCRAPER


    for source in SCRAPER_SOURCES:


        try:


            news.extend(

                fetch_scraper_news(

                    source

                )

            )



        except Exception as e:


            print(

                f"Scraper Source Error: {e}"

            )






    return news
