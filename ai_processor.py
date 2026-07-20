"""
KhabarF24 AI Processor v7.1

Pipeline:

News Fetcher v7
        ↓
Source Normalize
        ↓
Brand Protection
        ↓
Translation
        ↓
Cleanup
        ↓
Summary Generator
        ↓
Official Names Restore
        ↓
RTL Cleaner
        ↓
Formatter Ready
"""


import re
import html


from deep_translator import GoogleTranslator


from brand_dictionary import (
    replace_official_names
)


from rtl_cleaner import (
    fix_rtl_text
)



print("🤖 KhabarF24 AI Processor v7.1 Loaded")





# =====================================================
# Translation
# =====================================================


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







# =====================================================
# Cleanup
# =====================================================


BAD_TRANSLATIONS = [

    "این متن",

    "به پایان می دهد",

    "مورد حمله قرار داد",

    "می باشد",

    "یک اندازه",

    "در این مقاله",

    "این خبر",

]





def clean_text(text):

    if not text:

        return ""


    text = html.unescape(text)



    for bad in BAD_TRANSLATIONS:

        text = text.replace(
            bad,
            ""
        )



    text = re.sub(

        r"<.*?>",

        "",

        text

    )



    text = re.sub(

        r"\s+",

        " ",

        text

    )


    return text.strip()







# =====================================================
# Protect Numbers
# =====================================================


def protect_numbers(original, translated):

    if not original:

        return translated



    numbers = re.findall(

        r"\d+",

        original

    )



    for number in numbers:


        if number not in translated:

            translated += f" {number}"



    return translated.strip()







# =====================================================
# Summary Generator
# =====================================================


def create_summary(title, summary, content):


    # اگر خلاصه خوب وجود دارد

    if summary and len(summary) >= 40:

        return summary





    source = summary or content or title


    if not source:

        return ""




    source = clean_text(

        source

    )



    sentences = re.split(

        r"[.!؟\n]",

        source

    )



    for sentence in sentences:


        sentence = sentence.strip()



        if len(sentence) >= 40:


            return sentence[:250]




    return source[:250]









# =====================================================
# Main AI Processor
# =====================================================


def process_news(news):


    if not isinstance(news, dict):

        return {}





    title = news.get(

        "title",

        ""

    )


    summary = news.get(

        "summary",

        ""

    )


    content = news.get(

        "content",

        ""

    )


    source = news.get(

        "source",

        "Unknown"

    )


    category = news.get(

        "category",

        "world"

    )





    print(

        "🤖 KhabarF24 AI Processing..."

    )







    # ---------------------------------
    # Protect official names
    # ---------------------------------


    protected_title = replace_official_names(

        title

    )


    protected_summary = replace_official_names(

        summary

    )


    protected_content = replace_official_names(

        content

    )








    # ---------------------------------
    # Translate title
    # ---------------------------------


    fa_title = translate_text(

        protected_title

    )







    # ---------------------------------
    # Translate summary/content
    # ---------------------------------


    fa_summary = translate_text(

        protected_summary

    )



    if not fa_summary:


        fa_summary = translate_text(

            protected_content

        )








    # ---------------------------------
    # Cleanup
    # ---------------------------------


    fa_title = clean_text(

        fa_title

    )


    fa_summary = clean_text(

        fa_summary

    )









    # ---------------------------------
    # Numbers protection
    # ---------------------------------


    fa_title = protect_numbers(

        title,

        fa_title

    )


    fa_summary = protect_numbers(

        content or summary,

        fa_summary

    )









    # ---------------------------------
    # Restore names
    # ---------------------------------


    fa_title = replace_official_names(

        fa_title

    )


    fa_summary = replace_official_names(

        fa_summary

    )









    # ---------------------------------
    # Generate final summary
    # ---------------------------------


    fa_summary = create_summary(

        fa_title,

        fa_summary,

        content

    )









    # ---------------------------------
    # RTL
    # ---------------------------------


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

            fa_summary,


        "content":

            content,


        "source":

            source,


        "category":

            category

            }
