"""
KhabarF24 News Fetcher v6.3

وظیفه:
- دریافت خبر از RSS
- استاندارد سازی خروجی
- نگهداری نام منبع
- آماده سازی برای Category / AI / Formatter
"""

import feedparser
import html
import re



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

                "source": name

            })



        return news




    except Exception as e:


        print(
            f"Fetch Error {name}: {e}"
        )


        return []
