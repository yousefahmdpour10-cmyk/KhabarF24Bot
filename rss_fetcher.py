"""
KhabarF24 RSS Fetcher v6.1

Features:
- Browser User-Agent
- Timeout protection
- Better RSS error handling
- Keep bot alive when one source fails
"""


import feedparser
import requests



HEADERS = {

    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

}



def fetch_news(source_info):


    rss_url = source_info["url"]

    source_name = source_info["name"]

    category = source_info["category"]


    news = []



    try:


        response = requests.get(

            rss_url,

            headers=HEADERS,

            timeout=20

        )


        if response.status_code != 200:


            print(

                f"⚠️ RSS HTTP Error: {source_name} | {response.status_code}"

            )


            return []



        feed = feedparser.parse(

            response.content

        )



        if feed.bozo:


            print(

                f"⚠️ RSS Parse Warning: {source_name}"

            )



        for entry in feed.entries:



            news.append({


                "title":

                entry.get(

                    "title",

                    ""

                ).strip(),



                "link":

                entry.get(

                    "link",

                    ""

                ).strip(),



                "summary":

                entry.get(

                    "summary",

                    ""

                ).strip(),



                "source":

                source_name,



                "category":

                category

            })



    except requests.exceptions.Timeout:


        print(

            f"⏱ RSS Timeout: {source_name}"

        )



    except Exception as e:


        print(

            f"❌ RSS Failed: {source_name} | {e}"

        )



    return news
