"""
KhabarF24 News Fetcher v7.0

وظیفه:

- دریافت RSS
- دریافت Scraper بدون RSS
- استانداردسازی خروجی
- ارسال content کامل برای AI
- حفظ منبع
- آماده سازی Pipeline

Pipeline:

news_fetcher
      ↓
ai_processor
      ↓
category_engine
      ↓
quality_engine
      ↓
importance_engine
      ↓
formatter
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
# RSS
# =========================


def fetch_rss_news(source):


    news = []


    if not source:
        return news



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
        return news




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

                # برای RSS خالی است
                "content": summary,


                "link": link,


                "source": name,


                "category": category,


                "type": "rss"

            })



    except Exception as e:


        print(
            f"RSS Error {name}: {e}"
        )



    return news







# =========================
# SCRAPER
# =========================


def fetch_scraper_news(source):


    result = []


    try:


        scraped = scrape_source(
            source
        )



        for item in scraped:


            title = clean_text(
                item.get(
                    "title",
                    ""
                )
            )


            content = clean_text(

                item.get(

                    "content",

                    item.get(

                        "text",

                        item.get(

                            "summary",

                            ""

                        )

                    )

                )

            )



            link = item.get(

                "link",

                ""

            )



            if not title:

                continue



            result.append({


                "title": title,


                # فعلاً خالی
                # AI خودش خلاصه می‌سازد

                "summary": "",


                # متن کامل سایت

                "content": content,


                "link": link,


                "source": source.get(

                    "name",

                    "Unknown"

                ),


                "category": source.get(

                    "category",

                    "world"

                ),


                "type": "scraper"

            })




    except Exception as e:


        print(

            f"Scraper Error: {e}"

        )



    return result







# =========================
# MAIN
# =========================


def get_latest_news():


    news = []



    # RSS Sources

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





    # Scraper Sources


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
