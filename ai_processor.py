"""
KhabarF24 AI Processor v5.2

Pipeline:

Translation
↓
Translation Cleanup
↓
Number Protection
↓
Official Names
↓
Safe Rewrite
↓
Official Names Again
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


    text = html.unescape(
        text
    )


    # حذف عددهای اشتباه گوگل

    text = re.sub(
        r"\(\d+\)",
        "",
        text
    )


    # فاصله‌های اضافی

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
# Title Cleaner
# =========================


def improve_title(title):

    if not title:

        return ""


    title = title.strip()


    # حذف عبارت‌های ترجمه‌ای

    remove_words = [

        "جزئیات کامل",

        "آخرین اخبار",

        "آنچه باید بدانید",

        "در این گزارش",

    ]


    for word in remove_words:

        title = title.replace(
            word,
            ""
        )



    # حذف دو نقطه

    title = title.replace(
        ":",
        " "
    )


    title = re.sub(
        r"\s+",
        " ",
        title
    )


    # کوتاه سازی امن

    words = title.split()


    if len(words) > 12:

        title = " ".join(
            words[:12]
        )



    return title.strip()






# =========================
# Summary Cleaner
# =========================


def improve_summary(summary):

    if not summary:

        return ""


    summary = summary.strip()



    bad_words = [

        "در این گزارش",

        "آخرین اخبار",

        "جزئیات کامل",

        "اینجا جدیدترین است",

        "به شرح زیر",

    ]



    for word in bad_words:

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
        "🤖 KhabarF24 AI v5.2"
    )



    # Translation

    fa_title = translate_text(
        title
    )


    fa_summary = translate_text(
        summary
    )



    print(
        "After Translation:",
        fa_title
    )




    # Clean

    fa_title = clean_translation(
        fa_title
    )


    fa_summary = clean_translation(
        fa_summary
    )




    # Numbers

    fa_title = protect_numbers(
        title,
        fa_title
    )


    fa_summary = protect_numbers(
        summary,
        fa_summary
    )





    # Official Brands

    fa_title = replace_official_names(
        fa_title
    )


    fa_summary = replace_official_names(
        fa_summary
    )






    # Rewrite

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






    # Brands again

    fa_title = replace_official_names(
        fa_title
    )


    fa_summary = replace_official_names(
        fa_summary
    )






    # Final

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
