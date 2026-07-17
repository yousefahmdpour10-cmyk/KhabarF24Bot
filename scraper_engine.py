"""
KhabarF24 Scraper Engine v1.0

وظیفه:
- دریافت خبر از سایت های بدون RSS
- استخراج عنوان
- استخراج لینک
- استاندارد سازی خروجی
"""


import requests
from bs4 import BeautifulSoup
import html
import re





# =========================
# تنظیمات درخواست
# =========================


HEADERS = {


    "User-Agent":

    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

}





# =========================
# پاکسازی متن
# =========================


def clean_text(text):


    if not text:

        return ""



    text = html.unescape(text)



    text = re.sub(

        r"\s+",

        " ",

        text

    )



    return text.strip()








# =========================
# دریافت صفحه
# =========================


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









# =========================
# استخراج لینک ها
# =========================


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



        link = a["href"]




        if len(title) < 20:

            continue



        if not link.startswith("http"):


            link = base_url.rstrip("/") + "/" + link.lstrip("/")



        results.append({


            "title": title,


            "link": link


        })



    return results









# =========================
# Scraper اصلی
# =========================


def scrape_source(source):


    url = source.get(

        "url",

        ""

    )


    name = source.get(

        "name",

        ""

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



    articles = extract_links(

        page,

        url

    )



    news = []



    for item in articles[:10]:


        news.append({


            "title": item["title"],


            "summary": "",


            "link": item["link"],


            "source": name,


            "category": category


        })



    return news
