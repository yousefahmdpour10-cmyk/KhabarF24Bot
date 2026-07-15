"""
KhabarF24 AI Processor v4.4

Pipeline:

Translate
↓
Official Names
↓
News Rewrite
↓
Official Names Again
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
        "🤖 KhabarF24 AI v4.4"
    )



    # =====================
    # 1. Translation
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
    # 2. Official Names
    # =====================


    fa_title = replace_official_names(
        fa_title
    )


    fa_summary = replace_official_names(
        fa_summary
    )



    # =====================
    # 3. News Rewrite
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
    # 4. Official Names Again
    # =====================


    fa_title = replace_official_names(
        fa_title
    )


    fa_summary = replace_official_names(
        fa_summary
    )



    # =====================
    # 5. RTL Cleaner
    # =====================


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
