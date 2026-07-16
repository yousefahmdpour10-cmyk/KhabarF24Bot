"""
KhabarF24 AI Processor v5.0

Pipeline:

Translation
↓
Official Names
↓
News Rewrite Safe Mode
↓
Fact Protection
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





def translate_text(text):

    if not text:
        return ""


    try:

        translated = GoogleTranslator(
            source="auto",
            target="fa"
        ).translate(text)


        return translated.strip()


    except Exception as e:

        print(
            f"Translation Error: {e}"
        )

        return text






def protect_numbers(original, translated):


    if not original or not translated:

        return translated



    original_numbers = re.findall(
        r"\d+",
        original
    )


    for number in original_numbers:


        if number not in translated:


            translated += f" ({number})"



    return translated






def shorten_title(title):


    if not title:

        return ""



    words = title.split()



    # تیتر حرفه‌ای کوتاه

    if len(words) > 12:

        title = " ".join(
            words[:12]
        )



    return title






def clean_summary(summary):


    if not summary:

        return ""



    # حذف عبارت‌های ماشینی

    bad_words = [

        "طبق گزارش",

        "در این گزارش",

        "به گفته منابع",

        "آخرین اخبار",

    ]



    for word in bad_words:

        summary = summary.replace(
            word,
            ""
        )


    return summary.strip()






def process_news(title, summary):


    print(
        "🤖 KhabarF24 AI v5.0"
    )



    # =====================
    # Translation
    # =====================


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



    # =====================
    # Fact Protection
    # =====================


    fa_title = protect_numbers(
        title,
        fa_title
    )


    fa_summary = protect_numbers(
        summary,
        fa_summary
    )





    # =====================
    # Official Names
    # =====================


    fa_title = replace_official_names(
        fa_title
    )


    fa_summary = replace_official_names(
        fa_summary
    )





    # =====================
    # Safe Rewrite
    # =====================


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





    # =====================
    # Final Cleaning
    # =====================


    fa_title = shorten_title(
        fa_title
    )


    fa_summary = clean_summary(
        fa_summary
    )





    fa_title = replace_official_names(
        fa_title
    )


    fa_summary = replace_official_names(
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
