"""
KhabarF24 News Rewriter v6.0

وظیفه:
- طبیعی کردن فارسی خبر
- حذف ترجمه ماشینی
- ساخت تیتر کوتاه
- پاکسازی RSS
- اصلاح اصطلاحات خبری
- آماده سازی برای تلگرام
"""


import re
import html





REWRITE_RULES = {


    # =====================
    # افعال ماشینی
    # =====================

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



    # =====================
    # عمومی
    # =====================

    "مورد حمله قرار داد":
        "حمله کرد",

    "مورد حمله قرار گرفت":
        "هدف حمله قرار گرفت",

    "فیلم نشان می دهد":
        "تصاویر نشان می‌دهد",

    "ویدئو نشان می دهد":
        "تصاویر نشان می‌دهد",

    "آتش نشانان":
        "آتش‌نشانان",

    "آتش گسترده ای":
        "آتش‌سوزی گسترده",

    "خاموش می کنند":
        "مهار می‌کنند",

    "به وقوع پیوست":
        "رخ داد",

    "صورت گرفت":
        "انجام شد",



    # =====================
    # سیاسی
    # =====================

    "رئیس جمهور":
        "رئیس‌جمهور",

    "رئیس جمهور آمریکا":
        "رئیس‌جمهور آمریکا",

    "ایالات متحده":
        "آمریکا",

    "به دنبال آن":
        "پس از آن",

    "در بحبوحه":
        "در پی",



    # =====================
    # جنگ
    # =====================

    "تشدید جنگ":
        "تشدید تنش‌ها",

    "مناطق آزمایشی":
        "مناطق حائل",

    "طرح خروج":
        "برنامه خروج",



    # =====================
    # ترجمه بد
    # =====================

    "باعث شد":
        "موجب شد",

    "به دلیل":
        "به دنبال",

    "به دست آورد":
        "کسب کرد",

    "به دست می آورد":
        "کسب می‌کند",

    "برنده شد":
        "پیروز شد",

    "شکست خورد":
        "باخت",



    # =====================
    # فناوری
    # =====================

    "مدل باز":
        "مدل متن‌باز",

    "زیرساخت های":
        "زیرساخت‌های",



    # =====================
    # رای
    # =====================

    "رای گیری":
        "رأی‌گیری",

    "رای موافق":
        "رأی موافق",

    "رای مخالف":
        "رأی مخالف",

    "رای":
        "رأی",



    # =====================
    # اصطلاحات خاص
    # =====================

    "کمک به مرگ":
        "مرگ با کمک پزشکی",

    "متن را تصویب کرد":
        "لایحه را تصویب کرد",

}








def apply_rules(text):

    if not text:
        return ""


    for old,new in REWRITE_RULES.items():

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







# ==========================
# حذف عبارت‌های ضعیف تیتر
# ==========================


def clean_title_start(title):


    starts = [

        "در پی گزارش‌هایی مبنی بر",

        "در پی گزارش هایی مبنی بر",

        "گزارش می دهد که",

        "گزارش شده است که",

        "به گفته منابع",

    ]


    for item in starts:

        if title.startswith(item):

            title = title.replace(
                item,
                "",
                1
            ).strip()


    return title








# ==========================
# کوتاه سازی تیتر
# ==========================


def shorten_title(title, limit=80):


    title = clean_spaces(title)



    if len(title) <= limit:

        return title



    for sep in [

        "؛",

        "،",

        ",",

        " - ",

        ":"

    ]:


        if sep in title:

            title = title.split(sep)[0]

            break



    if len(title) > limit:


        words = title.split()


        title = " ".join(

            words[:11]

        )


    return title.strip()








# ==========================
# تیتر نهایی
# ==========================


def improve_title(title):


    title = html.unescape(title)


    title = apply_rules(title)


    title = clean_spaces(title)


    title = clean_title_start(title)


    title = shorten_title(title)



    # حذف نقطه از تیتر

    title = title.rstrip(
        ".!؟"
    )


    return title







# ==========================
# خلاصه
# ==========================


def improve_summary(summary):


    summary = html.unescape(summary)


    summary = apply_rules(summary)


    summary = clean_spaces(summary)


    summary = summary.replace(
        "[...]",
        ""
    )


    summary = summary.replace(
        "...",
        ""
    )



    if summary and summary[-1] not in [

        ".",
        "!",
        "؟"

    ]:

        summary += "."



    return summary








# ==========================
# حذف تکرار تیتر
# ==========================


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







# ==========================
# Main
# ==========================


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
