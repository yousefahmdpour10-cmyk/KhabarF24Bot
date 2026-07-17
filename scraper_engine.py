"""
KhabarF24 Scraper Engine v1.0

SCRAPER:
- منابع بدون RSS
- خروجی استاندارد مشابه RSS
- آماده برای Telegram Formatter

Output:

{
    title,
    summary,
    link,
    source,
    category,
    sport
}
"""


import requests
from bs4 import BeautifulSoup


from sources import SCRAPER_SOURCES





HEADERS = {

    "User-Agent":
        "Mozilla/5.0 (KhabarF24 Bot)"

}





# =========================
# دریافت صفحه
# =========================


def fetch_page(url):

    try:

        response = requests.get(

            url,

            headers=HEADERS,

            timeout=10

        )


        response.encoding = "utf-8"


        return response.text



    except Exception as e:


        print(

            f"Scraper Request Error {url}: {e}"

        )


        return ""









# =========================
# پاکسازی متن
# =========================


def clean_text(text):


    if not text:

        return ""



    return (

        text

        .replace("\n", " ")

        .replace("\t", " ")

        .strip()

    )









# =========================
# استخراج عمومی
# =========================


def scrape_generic(source):


    html = fetch_page(

        source["url"]

    )



    if not html:

        return []





    soup = BeautifulSoup(

        html,

        "lxml"

    )




    news = []





    # پیدا کردن لینک‌های خبری

    links = soup.find_all(

        "a",

        href=True

    )





    for item in links[:10]:


        title = clean_text(

            item.get_text()

        )


        link = item["href"]



        if len(title) < 20:

            continue





        if link.startswith("/"):

            link = (

                source["url"].rstrip("/")

                +

                link

            )





        news.append({


            "title":

                title,


            "summary":

                "",


            "link":

                link,


            "source":

                source["name"],


            "category":

                source["category"],


            "sport":

                source.get(

                    "sport",

                    None

                )

        })





    return news











# =========================
# منابع ویژه
# =========================


def scrape_source(source):


    name = source["name"]




    # فعلاً موتور عمومی

    # بعداً برای هر سایت parser اختصاصی می‌سازیم



    return scrape_generic(

        source

    )











# =========================
# دریافت همه Scraper ها
# =========================


def fetch_scraper_news():


    all_news = []



    for source in SCRAPER_SOURCES:


        try:


            result = scrape_source(

                source

            )


            all_news.extend(

                result

            )



        except Exception as e:


            print(

                f"Scraper Error {source['name']}: {e}"

            )





    return all_news
