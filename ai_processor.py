"""
KhabarF24 AI Processor v4.1

- Translation
- Brand replacement
- Persian cleanup
- RTL fix
"""


from translator import (
    translate_text,
    improve_persian_style,
    create_headline,
    summarize_text,
)

from brand_dictionary import replace_official_names

from rtl_cleaner import fix_rtl_text



def process_news(title, summary):

    print("🤖 KhabarF24 AI v4.1")


    # ترجمه عنوان
    fa_title = translate_text(title)


    # ترجمه خلاصه
    fa_summary = translate_text(summary)



    # اصلاح نام‌های رسمی
    fa_title = replace_official_names(
        fa_title
    )

    fa_summary = replace_official_names(
        fa_summary
    )



    # اصلاح لحن فارسی
    fa_title = improve_persian_style(
        fa_title
    )

    fa_summary = improve_persian_style(
        fa_summary
    )



    # تیتر
    fa_title = create_headline(
        fa_title
    )



    # خلاصه
    fa_summary = summarize_text(
        fa_summary
    )



    if not fa_summary:

        fa_summary = fa_title



    # اصلاح RTL
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
