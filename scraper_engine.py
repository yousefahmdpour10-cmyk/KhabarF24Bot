"""
KhabarF24 Scraper Engine v2.0

Features:

- RSS fallback support
- HTML extraction
- Title extraction
- Meta description summary
- Content extraction
- Link normalization
- Source protection
- Error handling

Compatible with:
- news_fetcher v7.1
- AI Processor v7.1
- Formatter v7.0

"""


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import html
import re



print("🌐 KhabarF24 Scraper Engine v2.0 Loaded")





# =====================================
# Request Headers
# =====================================


HEADERS = {


    "User-Agent":

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "Chrome/120 Safari/537.36",


    "Accept-Language":

    "en-US,en;q=0.9"


}






# =====================================
# Blocked / Ads Text
# =====================================


BAD_TEXTS = [


    "subscribe",

    "sign up",

    "login",

    "read more",

    "advertisement",

    "cookie",

    "اشتراک",

    "عضویت",

    "تبلیغات",

    "ادامه مطلب",

    "بیشتر بخوانید",

]






# =====================================
# Clean Text
# =====================================


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



    for bad in BAD_TEXTS:


        text = text.replace(

            bad,

            ""

        )



    return text.strip()








# =====================================
# Get Page
# =====================================


def get_page(url):


    try:


        response = requests.get(

            url,

            headers=HEADERS,

            timeout=15

        )


        response.raise_for_status()



        return response.text



    except Exception as e:


        print(

            f"Scraper Request Error {url}: {e}"

        )


        return ""







# =====================================
# Extract Meta Summary
# =====================================


def extract_meta_summary(soup):


    if not soup:

        return ""



    tags = [


        soup.find(

            "meta",

            attrs={

                "name":"description"

            }

        ),



        soup.find(

            "meta",

            attrs={

                "property":"og:description"

            }

        )

    ]



    for tag in tags:


        if tag and tag.get("content"):


            text = clean_text(

                tag.get("content")

            )


            if len(text) > 30:

                return text



    return ""






# =====================================
# Extract Title
# =====================================


def extract_title(soup):


    if not soup:

        return ""



    title = soup.find(

        "h1"

    )



    if title:


        text = clean_text(

            title.get_text()

        )


        if len(text) > 10:

            return text





    if soup.title:


        return clean_text(

            soup.title.get_text()

        )



    return ""
    # =====================================
# Extract Main Content
# =====================================


def extract_content(soup):


    if not soup:

        return ""



    paragraphs = []



    for p in soup.find_all("p"):


        text = clean_text(

            p.get_text()

        )



        if len(text) > 50:


            paragraphs.append(

                text

            )



    content = " ".join(

        paragraphs[:5]

    )



    return content[:1000]







# =====================================
# Extract Article Links
# =====================================


def extract_links(html_page, base_url):


    if not html_page:

        return []



    soup = BeautifulSoup(

        html_page,

        "lxml"

    )



    results = []



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



        if len(title) < 25:

            continue



        link = urljoin(

            base_url,

            link

        )



        results.append({


            "title": title,


            "link": link


        })



    return results







# =====================================
# Scrape Article Page
# =====================================


def scrape_article(url):


    page = get_page(

        url

    )



    if not page:

        return {}



    soup = BeautifulSoup(

        page,

        "lxml"

    )



    title = extract_title(

        soup

    )



    summary = extract_meta_summary(

        soup

    )



    content = extract_content(

        soup

    )



    if not summary:


        summary = content[:250]



    return {


        "title": title,


        "summary": summary,


        "content": content,


        "link": url


    }








# =====================================
# Main Scraper
# =====================================


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





    links = extract_links(

        page,

        url

    )



    news = []





    for item in links[:10]:


        article = scrape_article(

            item["link"]

        )



        if not article:

            continue





        title = article.get(

            "title",

            item["title"]

        )



        content = article.get(

            "content",

            ""

        )



        summary = article.get(

            "summary",

            ""

        )



        if not title:

            continue





        news.append({


            "title": title,


            "summary": summary,


            "content": content,


            "link": article.get(

                "link",

                item["link"]

            ),



            "source": name,



            "category": category,



            "sport": source.get(

                "sport",

                ""

            )


        })



    return news
