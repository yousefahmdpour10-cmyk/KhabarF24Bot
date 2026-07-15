"""
KhabarF24 AI Processor v4.2

Pipeline:

RSS News
   ↓
Translation
   ↓
Official Name Replacement
   ↓
Persian Style Cleanup
   ↓
Headline Optimization
   ↓
Summary Cleanup
   ↓
RTL/LTR Fix
   ↓
Telegram
"""


from news_rewriter import (
    translate_text,
    improve_persian_style,
    create_headline,
    summarize_text,
)


from brand_dictionary import (
    replace_official_names,
)


from rtl_cleaner import (
    fix_rtl_text,
)




def process_news(title, summary):


    print("🤖 KhabarF24 AI v4.2")



    # =================================
    # Translation
    # =================================


    fa_title = translate_text(
        title
    )


    fa_summary = translate_text(
        summary
    )



    # =================================
    # Official names
    # Apple
    # Manchester United
    # Google
    # etc.
    # =================================


    fa_title = replace_official_names(
        fa_title
    )


    fa_summary = replace_official_names(
        fa_summary
    )



    # =================================
    # Persian style
    # =================================


    fa_title = improve_persian_style(
        fa_title
    )


    fa_summary = improve_persian_style(
        fa_summary
    )



    # =================================
    # Headline
    # =================================


    fa_title = create_headline(
        fa_title
    )



    # =================================
    # Summary
    # =================================


    fa_summary = summarize_text(
        fa_summary,
        max_length=300
    )



    if not fa_summary:

        fa_summary = fa_title



    # =================================
    # RTL / LTR Fix
    # جلوگیری از:
    #
    # Apple has...
    # Iran threatens...
    # US-ایران
    #
    # =================================


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
