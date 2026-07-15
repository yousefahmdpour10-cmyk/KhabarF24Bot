"""
KhabarF24 News Rewriter v5.3

وظیفه:
- طبیعی کردن فارسی خبر
- حذف ترجمه ماشینی خشک
- اصلاح تیتر
- پاکسازی RSS
- اصلاح اصطلاحات خبری
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
    # اخبار عمومی
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
    # ترجمه‌های بد
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
    # رای گیری
    # =====================

    "رای":
    "رأی",

    "رای گیری":
    "رأی‌گیری",

    "رای موافق":
    "رأی موافق",

    "رای مخالف":
    "رأی مخالف",



    # =====================
    # عبارت‌های ترجمه ماشینی خاص
    # =====================

    "کمک به مرگ":
    "مرگ با کمک پزشکی",

    "متن را تصویب کرد":
    "لایحه را تصویب کرد",


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


    text = html.unescape(
        text
    )


    text = re.sub(
        r"\s+",
        " ",
        text
    )


    return text.strip()





def finish_sentence(text):

    if not text:
        return ""


    text = text.strip()


    if text[-1] not in [
        ".",
        "!",
        "؟",
        "؛"
    ]:

        text += "."


    return text





def shorten_title(title, limit=95):

    if len(title) <= limit:

        return title


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

    title = html.unescape(
        title
    )


    title = apply_rules(
        title
    )


    title = clean_spaces(
        title
    )


    title = shorten_title(
        title
    )


    return finish_sentence(
        title
    )





def improve_summary(summary):

    summary = html.unescape(
        summary
    )


    summary = apply_rules(
        summary
    )


    summary = clean_spaces(
        summary
    )


    return finish_sentence(
        summary
    )





def rewrite_news(title, summary):

    return {

        "title":
        improve_title(title),


        "summary":
        improve_summary(summary)

    }
