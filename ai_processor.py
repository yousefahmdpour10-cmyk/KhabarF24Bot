"""
KhabarF24 AI Processor v5.1

Pipeline:

Translation
↓
Fact Protection
↓
Official Names
↓
Safe Rewrite
↓
Text Cleanup
↓
RTL Cleaner
↓
Telegram
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
# حذف ایرادهای ترجمه
# =========================


def clean_translation(text):


    if not text:
        return ""



    text = html.unescape(
        text
    )



    # حذف عددهای اضافی ترجمه گوگل
    text = re.sub(
        r"\(\d+\)",
        "",
        text
    )


    # حذف فاصله‌های خراب

    text = re.sub(
        r"\s+",
        " ",
        text
    )



    # اصلاح چسبیدن انگلیسی به فارسی

    text = re.sub(
        r"([آ-ی])([A-Za-z])",
        r"\1 \2",
        text
    )


    text = re.sub(
        r"([A-Za-z])([آ-ی])",
        r"\1 \2",
        text
    )



    return text.strip()







# =========================
# محافظت عددها
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
# تیتر حرفه‌ای
# =========================


def improve_title(title):


    if not title:

        return ""



    title = clean_translation(
        title
    )


    words = title.split()



    # کوتاه سازی تیتر

    if len(words) > 10:

        title = " ".join(
            words[:10]
        )



    # حذف علامت‌های بد

    title = title.replace(
        ":",
        " "
    )


    title = title.replace(
        "؟",
        ""
    )



    return title.strip()







# =========================
# خلاصه خبری
# =========================


def improve_summary(summary):


    if not summary:

        return ""



    summary = clean_translation(
        summary
    )



    bad = [

        "در این گزارش",

        "آخرین",

        "به شرح زیر",

        "اینجا جدیدترین است",

        "جزئیات کامل",

    ]



    for word in bad:


        summary = summary.replace(

            word,

            ""

        )



    return summary.strip()






# =========================
# اصلی
# =========================


def process_news(title, summary):


    print(
        "🤖 KhabarF24 AI v5.1"
    )



    # ترجمه

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




    # عددها

    fa_title = protect_numbers(

        title,

        fa_title

    )


    fa_summary = protect_numbers(

        summary,

        fa_summary

    )





    # پاکسازی اولیه

    fa_title = clean_translation(

        fa_title

    )


    fa_summary = clean_translation(

        fa_summary

    )






    # نام رسمی

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






    # دوباره نام‌ها

    fa_title = replace_official_names(

        fa_title

    )


    fa_summary = replace_official_names(

        fa_summary

    )






    # اصلاح نهایی

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
