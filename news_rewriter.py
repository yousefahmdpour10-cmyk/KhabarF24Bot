"""
KhabarF24 News Rewriter v6.2

وظیفه:
- طبیعی کردن فارسی خبر
- حذف ترجمه ماشینی
- ساخت تیتر کوتاه و کامل
- پاکسازی RSS
- اصلاح اصطلاحات خبری
- آماده سازی برای تلگرام
"""


import re
import html



REWRITE_RULES = {


    "اعلام کرد که":
        "اعلام کرد",

    "گفت که":
        "گفت",

    "می باشد":
        "است",

    "در حال حاضر":
        "اکنون",

    "به پایان دهد":
        "پایان دهد",

    "به پایان می دهد":
        "پایان می‌دهد",



    "مورد حمله قرار داد":
        "حمله کرد",

    "مورد حمله قرار گرفت":
        "هدف حمله قرار گرفت",

    "فیلم نشان می دهد":
        "تصاویر نشان می‌دهد",

    "ویدئو نشان می دهد":
        "تصاویر نشان می‌دهد",

    "به وقوع پیوست":
        "رخ داد",

    "صورت گرفت":
        "انجام شد",



    "رئیس جمهور":
        "رئیس‌جمهور",

    "ایالات متحده":
        "آمریکا",

    "به دنبال آن":
        "پس از آن",

    "در بحبوحه":
        "در پی",



    "باعث شد":
        "موجب شد",

    "به دست آورد":
        "کسب کرد",

    "برنده شد":
        "پیروز شد",

    "شکست خورد":
        "باخت",



    "مدل باز":
        "مدل متن‌باز",

    "زیرساخت های":
        "زیرساخت‌های",



    "رای گیری":
        "رأی‌گیری",

    "رای موافق":
        "رأی موافق",

    "رای مخالف":
        "رأی مخالف",

    "رای":
        "رأی",

}





def apply_rules(text):

    if not text:
        return ""


    for old, new in REWRITE_RULES.items():

        text = text.replace(
            old,
            new
        )


    return text





def clean_spaces(text):

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
# حذف پایان‌های خراب RSS
# =========================


def clean_rss_breaks(text):

    if not text:
        return ""


    bad_endings = [

        "...",

        "…",

        "ادامه",

        "ادامه مطلب",

        "بیشتر بخوانید",

    ]


    for item in bad_endings:

        if text.endswith(item):

            text = text[:-len(item)]


    return text.strip()





# =========================
# حذف شروع‌های ضعیف تیتر
# =========================


def clean_title_start(title):


    starts = [

        "در پی گزارش‌هایی مبنی بر",

        "در پی گزارش هایی مبنی بر",

        "گزارش می دهد که",

        "گزارش شده است که",

        "به گفته منابع",

        "طبق گزارش‌ها",

        "طبق گزارش ها",

    ]


    for item in starts:

        if title.startswith(item):

            title = title.replace(
                item,
                "",
                1
            ).strip()


    return title





# =========================
# کوتاه سازی تیتر
# =========================


def shorten_title(title, limit=90):


    title = clean_spaces(title)


    if len(title) <= limit:

        return title



    separators = [

        "؛",

        "،",

        "-",

        ":"

    ]


    for sep in separators:

        if sep in title:

            part = title.split(sep)[0].strip()


            if len(part) > 25:

                return part



    words = title.split()


    result = ""


    for word in words:

        if len(result + " " + word) > limit:

            break


        result += " " + word


    return result.strip()





# =========================
# اصلاح تیتر
# =========================


def improve_title(title):


    if not title:
        return ""


    title = html.unescape(title)


    title = apply_rules(title)


    title = clean_spaces(title)


    title = clean_rss_breaks(title)


    title = clean_title_start(title)


    title = shorten_title(title)


    title = title.rstrip(
        ".!؟"
    )


    return title.strip()





# =========================
# اصلاح خلاصه
# =========================


def improve_summary(summary):


    if not summary:
        return ""


    summary = html.unescape(summary)


    summary = apply_rules(summary)


    summary = clean_spaces(summary)


    summary = clean_rss_breaks(summary)



    summary = summary.replace(
        "[...]",
        ""
    )


    summary = re.sub(
        r"\.{2,}",
        "",
        summary
    )


    if summary and summary[-1] not in [

        ".",

        "!",

        "؟"

    ]:

        summary += "."


    return summary.strip()





# =========================
# حذف تکرار تیتر در خلاصه
# =========================


def remove_title_repeat(title, summary):


    if not title or not summary:

        return summary



    words = title.split()


    if len(words) < 4:

        return summary



    check = " ".join(
        words[:4]
    )


    if check in summary:


        summary = summary.replace(

            check,

            "",

            1

        ).strip()



    return summary





# =========================
# Main
# =========================


def rewrite_news(title, summary):


    new_title = improve_title(title)


    new_summary = improve_summary(summary)



    new_summary = remove_title_repeat(

        new_title,

        new_summary

    )



    return {

        "title":

            new_title,


        "summary":

            new_summary

    }
