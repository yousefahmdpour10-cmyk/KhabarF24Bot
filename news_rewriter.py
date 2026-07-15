"""
KhabarF24 News Rewriter v5

وظیفه:
- طبیعی کردن فارسی خبر
- حذف ترجمه ماشینی خشک
- اصلاح تیتر
- حفظ سبک خبری کوتاه
"""


import re



# اصلاح عبارت‌های رایج ترجمه ماشینی

REWRITE_RULES = {


    # فعل‌ها

    "به پایان دهد":
    "به پایان داد",

    "به پایان می دهد":
    "به پایان داد",

    "اعلام کرد که":
    "اعلام کرد",

    "گفت که":
    "گفت",

    "می باشد":
    "است",

    "در حال حاضر":
    "اکنون",


    # اصطلاحات خبری

    "بن بست":
    "بن‌بست",

    "تشدید جنگ":
    "تشدید تنش‌ها",

    "در بحبوحه":
    "در پی",

    "به دلیل":
    "به دنبال",

    "باعث شد":
    "موجب شد",


    # ترجمه‌های بد رایج

    "به دست آورد":
    "کسب کرد",

    "به دست می آورد":
    "کسب می‌کند",

    "برنده شد":
    "پیروز شد",

    "شکست خورد":
    "باخت",


    # سیاسی

    "رئیس جمهور آمریکا":
    "رئیس‌جمهور آمریکا",

    "ایالات متحده":
    "آمریکا",

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

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()





def shorten_title(title, limit=90):

    if len(title) <= limit:

        return title


    # اولویت با جدا کردن جمله

    for sep in [
        "؛",
        ",",
        " - ",
        ":"
    ]:

        if sep in title:

            title = title.split(sep)[0]

            break


    return title.strip()





def improve_title(title):

    title = apply_rules(
        title
    )


    title = clean_spaces(
        title
    )


    title = shorten_title(
        title
    )


    return title





def improve_summary(summary):

    summary = apply_rules(
        summary
    )


    summary = clean_spaces(
        summary
    )


    return summary





def rewrite_news(title, summary):

    return {

        "title":
        improve_title(title),


        "summary":
        improve_summary(summary)

}
