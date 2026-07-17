"""
KhabarF24 News Fetcher v6.4

وظیفه:
- دریافت RSS
- دریافت Scraper Sources
- استاندارد سازی خروجی
- حفظ نام منبع
- آماده سازی برای AI Engine
"""


import feedparser
import html
import re


from sources import (
    RSS_SOURCES,
    SCRAPER_SOURCES
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


def fetch_news(source):


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



    if not url:

        return []




    try:


        feed = feedparser.parse(

            url

        )



        news = []



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


                "category": source.get(

                    "category"

                )


            })



        return news




    except Exception as e:


        print(

            f"RSS Error {name}: {e}"

        )


        return []








# =========================
# Scraper Placeholder
# =========================


def fetch_scraper_news(source):


    """
    بعداً برای سایت‌های بدون RSS
    مثل تسنیم، فارس، NBA و...
    Scraper اختصاصی اضافه می‌شود.
    """

    return []








# =========================
# Main Collector
# =========================


def get_latest_news():


    news = []



    # RSS

    for source in RSS_SOURCES:


        try:


            news.extend(

                fetch_news(source)

            )


        except Exception as e:


            print(

                f"RSS Error {source.get('name','')}: {e}"

            )





    # Scraper

    for source in SCRAPER_SOURCES:


        try:


            news.extend(

                fetch_scraper_news(source)

            )


        except Exception as e:


            print(

                f"Scraper Error {source.get('name','')}: {e}"

            )




    return news
