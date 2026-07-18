"""
KhabarF24 AI Processor v7.0

Pipeline:

News Fetcher v7
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



print("🤖 KhabarF24 AI Processor v7.0 Loaded")





# =====================================================
# Translator
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



    for num in numbers:


        if num not in translated:


            translated += f" {num}"



    return translated.strip()







# =====================================================
# Create Summary
# =====================================================


def create_summary(title, content, summary):


    if summary and len(summary) > 40:

        return summary



    source = content or title



    if not source:

        return ""



    sentences = re.split(

        r"[.!؟]",

        source

    )



    result = ""



    for sentence in sentences:


        sentence = sentence.strip()



        if len(sentence) > 40:


            result = sentence

            break



    if not result:


        result = source[:180]



    return result.strip()







# =====================================================
# AI Processing
# =====================================================


def process_news(news):


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

        ""

    )


    category = news.get(

        "category",

        "world"

    )






    print(

        "🤖 KhabarF24 AI v7.0"

    )





    # ---------------------------------
    # Protect official names
    # ---------------------------------


    title = replace_official_names(

        title

    )


    summary = replace_official_names(

        summary

    )


    content = replace_official_names(

        content

    )






    # ---------------------------------
    # Translation
    # ---------------------------------


    fa_title = translate_text(

        title

    )


    fa_summary = translate_text(

        summary

    )



    if not fa_summary:


        fa_summary = translate_text(

            content

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
    # Number Protection
    # ---------------------------------


    fa_title = protect_numbers(

        title,

        fa_title

    )


    fa_summary = protect_numbers(

        summary or content,

        fa_summary

    )







    # ---------------------------------
    # Restore official names
    # ---------------------------------


    fa_title = replace_official_names(

        fa_title

    )


    fa_summary = replace_official_names(

        fa_summary

    )







    # ---------------------------------
    # Create final summary
    # ---------------------------------


    fa_summary = create_summary(

        fa_title,

        fa_summary,

        fa_summary

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
