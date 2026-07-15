"""
KhabarF24 AI Processor v4.3

Pipeline:

Translate
↓
Official Names
↓
News Rewrite
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





def process_news(title, summary):


    print(
        "🤖 KhabarF24 AI v4.3"
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
    # News Rewrite
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
    # RTL Fix
    # =====================


    fa_title = fix_rtl_text(
        fa_title
    )


    fa_summary = fix_rtl_text(
        fa_summary
    )



    return {

        "title": fa_title,

        "summary": fa_summary

    }
