"""
KhabarF24 News Rewriter v5.2

وظیفه:
- طبیعی کردن فارسی خبر
- حذف ترجمه ماشینی خشک
- اصلاح تیتر
- حفظ سبک خبری کوتاه
- پاکسازی خروجی RSS
"""


import re
import html



REWRITE_RULES = {


    # =====================
    # فعل‌های ماشینی
    # =====================


    "اعلام کرد که":
    "اعلام کرد",

    "گفت که":
    "گفت",

    "می باشد":
    "است",

    "در حال حاضر":
    "اکنون",

    "خواهد داشت":
    "دارد",

    "به پایان دهد":
    "پایان دهد",

    "به پایان می دهد":
    "پایان می‌دهد",



    # =====================
    # خبری
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

    "کشور ایالات متحده":
    "آمریکا",

    "به دنبال آن":
    "پس از آن",

    "در بحبوحه":
    "در پی",



    # =====================
    # جنگ و درگیری
    # =====================


    "تشدید جنگ":
    "تشدید تنش‌ها",

    "حملات هوایی":
    "حملات هوایی",

    "حمله موشکی":
    "حمله موشکی",

    "حملات موشکی و پهپادی":
    "حملات موشکی و پهپادی",

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


    "هوش مصنوعی":
    "هوش مصنوعی",

    "مدل باز":
    "مدل متن‌باز",

    "زیرساخت های":
    "زیرساخت‌های",

    "شرط خود را":
    "سرمایه‌گذاری خود را",



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
