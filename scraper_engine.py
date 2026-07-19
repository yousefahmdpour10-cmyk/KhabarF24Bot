"""
KhabarF24 Scraper Engine v2.1

Features:

- Smart HTTP Session
- Retry System
- Anti 403 Handling
- Redirect Protection
- HTML Extraction
- Summary Extraction
- Clean Output

Compatible with:
- news_fetcher v7.1 Hybrid
- AI Processor v7.1
- Formatter v7.0

"""


import requests

from bs4 import BeautifulSoup

import html

import re

import time



print(
    "🌐 KhabarF24 Scraper Engine v2.1 Loaded"
)





# =====================================================
# HTTP SESSION
# =====================================================


SESSION = requests.Session()



HEADERS = {


    "User-Agent":

    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120 Safari/537.36"
    ),


    "Accept":

    (
        "text/html,"
        "application/xhtml+xml,"
        "application/xml;q=0.9,"
        "*/*;q=0.8"
    ),


    "Accept-Language":

    "en-US,en;q=0.9"

}



SESSION.headers.update(

    HEADERS

)







# =====================================================
# TEXT CLEANER
# =====================================================


def clean_text(text):


    if not text:

        return ""



    text = html.unescape(

        str(text)

    )



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
# REQUEST ENGINE
# =====================================================


def get_page(url):


    if not url:

        return ""



    try:



        response = SESSION.get(

            url,

            timeout=15,

            allow_redirects=True

        )



        if response.status_code == 403:


            print(

                f"🚫 Access Denied: {url}"

            )


            return ""





        response.raise_for_status()



        return response.text





    except requests.exceptions.TooManyRedirects:


        print(

            f"🔁 Redirect Loop: {url}"

        )


        return ""





    except requests.exceptions.RequestException as e:


        print(

            f"⚠️ Request Failed {url}: {e}"

        )


        return ""








# =====================================================
# REMOVE NOISE
# =====================================================


NOISE_WORDS = [


    "login",

    "subscribe",

    "newsletter",

    "cookie",

    "advertisement",

    "menu",

    "share"

]





def valid_title(title):


    if not title:

        return False



    if len(title) < 25:

        return False



    low = title.lower()



    for word in NOISE_WORDS:


        if word in low:

            return False



    return True
    # =====================================================
# EXTRACT ARTICLES
# =====================================================


def extract_articles(page, base_url):


    if not page:

        return []



    soup = BeautifulSoup(

        page,

        "lxml"

    )



    results = []



    # پیدا کردن لینک های خبری

    for a in soup.find_all(

        "a",

        href=True

    ):



        title = clean_text(

            a.get_text()

        )



        link = a.get(

            "href",

            ""

        )



        if not valid_title(title):

            continue



        if not link.startswith(

            "http"

        ):


            link = (

                base_url.rstrip("/")

                +

                "/"

                +

                link.lstrip("/")

            )




        results.append({

            "title": title,

            "link": link

        })



    return results








# =====================================================
# EXTRACT CONTENT
# =====================================================


def extract_content(url):


    page = get_page(

        url

    )



    if not page:

        return ""



    soup = BeautifulSoup(

        page,

        "lxml"

    )



    paragraphs = []



    for p in soup.find_all(

        "p"

    ):


        text = clean_text(

            p.get_text()

        )



        if len(text) > 40:


            paragraphs.append(

                text

            )



        if len(paragraphs) >= 3:

            break





    return " ".join(

        paragraphs

    )









# =====================================================
# SMART SCRAPER
# =====================================================


def scrape_source(source):


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




    page = get_page(

        url

    )



    if not page:


        return []





    articles = extract_articles(

        page,

        url

    )



    news = []





    for article in articles[:10]:


        content = extract_content(

            article["link"]

        )



        summary = content[:300]



        news.append({

            "title":

                article["title"],


            "summary":

                summary,



            "content":

                content,



            "link":

                article["link"],



            "source":

                name,



            "category":

                category


        })



    return news








# =====================================================
# SAFE FALLBACK
# =====================================================


def scrape_with_fallback(source):


    try:


        return scrape_source(

            source

        )



    except Exception as e:


        print(

            f"SCRAPER FALLBACK {source.get('name')}: {e}"

        )


        return []
