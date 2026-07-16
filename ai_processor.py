"""
KhabarF24 AI Processor v6.0

Pipeline:

Official Names Protection
↓
Translation
↓
Translation Cleanup
↓
Number Protection
↓
Official Names
↓
News Rewrite
↓
Title Cleanup
↓
Summary Cleanup
↓
RTL Cleaner
"""


from deep_translator import GoogleTranslator


from brand_dictionary import (
    replace_official_names,
)


from news_rewriter import (
    rewrite_news,
)


from rtl_cleaner import (
    fix_rtl_text,
)


import re
import html






# =========================
# Translation
# =========================


def translate_text(text):

    if not text:

        return ""



    try:


        result = GoogleTranslator(

            source="auto",

            target="fa"

        ).translate(text)



        return result.strip()



    except Exception as e:


        print(

            f"Translation Error: {e}"

        )


        return text







# =========================
# Clean Translation
# =========================


def clean_translation(text):


    if not text:

        return ""



    text = html.unescape(text)



    text = re.sub(

        r"\(\d+\)",

        "",

        text

    )



    text = re.sub(

        r"\s+",

        " ",

        text

    )



    return text.strip()







# =========================
# Protect Numbers
# =========================


def protect_numbers(original, translated):


    if not original or not translated:

        return translated



    numbers = re.findall(

        r"\d+",

        original

    )



    for number in numbers:


        if number not in translated:


            translated += f" {number}"



    return translated







# =========================
# Title Cleanup
# =========================


def improve_title(title):


    if not title:

        return ""



    remove_words = [


        "جزئیات کامل",

        "آخرین اخبار",

        "آنچه باید بدانید",

        "در این گزارش",

        "گزارش کامل",

    ]



    for word in remove_words:


        title = title.replace(

            word,

            ""

        )



    title = title.replace(

        ":",

        " "

    )



    title = re.sub(

        r"\s+",

        " ",

        title

    )



    words = title.split()



    if len(words) > 12:


        title = " ".join(

            words[:12]

        )



    return title.strip()







# =========================
# Summary Cleanup
# =========================


def improve_summary(summary):


    if not summary:

        return ""



    remove_words = [


        "در این گزارش",

        "آخرین اخبار",

        "جزئیات کامل",

        "به شرح زیر",

        "مطابق گزارش",

    ]



    for word in remove_words:


        summary = summary.replace(

            word,

            ""

        )



    summary = re.sub(

        r"\s+",

        " ",

        summary

    )



    return summary.strip()







# =========================
# Main Processor
# =========================


def process_news(title, summary):


    print(

        "🤖 KhabarF24 AI v6.0"

    )




    # مرحله اول:
    # محافظت نام‌های رسمی


    protected_title = replace_official_names(

        title

    )


    protected_summary = replace_official_names(

        summary

    )







    # ترجمه


    fa_title = translate_text(

        protected_title

    )


    fa_summary = translate_text(

        protected_summary

    )






    # پاکسازی


    fa_title = clean_translation(

        fa_title

    )


    fa_summary = clean_translation(

        fa_summary

    )







    # عددها


    fa_title = protect_numbers(

        title,

        fa_title

    )


    fa_summary = protect_numbers(

        summary,

        fa_summary

    )







    # نام‌های رسمی دوباره


    fa_title = replace_official_names(

        fa_title

    )


    fa_summary = replace_official_names(

        fa_summary

    )







    # بازنویسی خبری


    rewritten = rewrite_news(

        fa_title,

        fa_summary

    )



    fa_title = rewritten.get(

        "title",

        fa_title

    )


    fa_summary = rewritten.get(

        "summary",

        fa_summary

    )







    # پاکسازی نهایی


    fa_title = improve_title(

        fa_title

    )


    fa_summary = improve_summary(

        fa_summary

    )







    # RTL


    fa_title = fix_rtl_text(

        fa_title

    )


    fa_summary = fix_rtl_text(

        fa_summary

    )







    return {


        "title":

            fa_title,


        "summary":

            fa_summary

    }
