"""
KhabarF24 AI Processor v6.2

Pipeline:

Official Names Protection
↓
Translation
↓
Translation Cleanup
↓
Number Protection
↓
Official Names Restore
↓
News Rewrite
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



    # حذف شماره های ترجمه‌ای اضافی

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


            translated = translated + " " + number



    return translated.strip()







# =========================
# Main Processor
# =========================


def process_news(title, summary):


    print(

        "🤖 KhabarF24 AI v6.2"

    )




    # -------------------------
    # Official names protection
    # -------------------------


    protected_title = replace_official_names(

        title

    )


    protected_summary = replace_official_names(

        summary

    )






    # -------------------------
    # Translation
    # -------------------------


    fa_title = translate_text(

        protected_title

    )


    fa_summary = translate_text(

        protected_summary

    )






    # -------------------------
    # Cleanup
    # -------------------------


    fa_title = clean_translation(

        fa_title

    )


    fa_summary = clean_translation(

        fa_summary

    )







    # -------------------------
    # Number protection
    # -------------------------


    fa_title = protect_numbers(

        title,

        fa_title

    )


    fa_summary = protect_numbers(

        summary,

        fa_summary

    )








    # -------------------------
    # Restore official names
    # -------------------------


    fa_title = replace_official_names(

        fa_title

    )


    fa_summary = replace_official_names(

        fa_summary

    )








    # -------------------------
    # News rewrite
    # فقط اینجا تیتر و خلاصه اصلاح می‌شود
    # -------------------------


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








    # -------------------------
    # RTL Final
    # -------------------------


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
