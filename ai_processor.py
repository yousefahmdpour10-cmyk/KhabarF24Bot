"""
KhabarF24 AI Processor v5

Pipeline:

Raw News
 ↓
Clean
 ↓
Protect Entities
 ↓
Translate Persian
 ↓
Official Names
 ↓
News Rewriter
 ↓
Telegram Formatter

"""


from deep_translator import GoogleTranslator
import re
import html


from entities import PROTECTED_ENTITIES
from places import PROTECTED_PLACES

from brand_dictionary import (
    replace_official_names
)

from news_rewriter import (
    rewrite_news
)



print("🤖 KhabarF24 AI v5 Engine Started")




STYLE_RULES = {


    "می باشد":
    "است",

    "در حال حاضر":
    "اکنون",

    "به پایان دهد":
    "به پایان داد",

    "به دست آورد":
    "کسب کرد",

    "به دست می آورد":
    "کسب می‌کند",

    "بن بست":
    "بن‌بست",

    "بدون جنگ، بدون صلح":
    "نه جنگ، نه صلح",

}




def clean_text(text):

    if not text:

        return ""


    text = html.unescape(
        text
    )


    text = re.sub(
        r"<.*?>",
        "",
        text
    )


    text = " ".join(
        text.split()
    )


    return text.strip()





def protect_entities(text):

    protected = {}

    counter = 0


    entities = (
        PROTECTED_ENTITIES
        +
        PROTECTED_PLACES
    )


    for item in entities:


        if item in text:


            key = f"KEEP_{counter}"


            protected[key] = item


            text = text.replace(
                item,
                key
            )


            counter += 1



    return text, protected





def restore_entities(text, protected):


    for key,value in protected.items():


        text = text.replace(
            key,
            value
        )


    return text





def translate_text(text):


    text = clean_text(
        text
    )


    if not text:

        return ""



    original = text



    try:


        text, protected = protect_entities(
            text
        )


        translated = GoogleTranslator(
            source="auto",
            target="fa"
        ).translate(
            text
        )


        translated = restore_entities(
            translated,
            protected
        )


        translated = replace_official_names(
            translated
        )


        return translated.strip()



    except Exception as e:


        print(
            f"Translation Error: {e}"
        )


        return original





def apply_style(text):


    if not text:

        return ""



    for old,new in STYLE_RULES.items():

        text = text.replace(
            old,
            new
        )



    return text.strip()





def fix_rtl_start(text):


    if not text:

        return ""



    # جلوگیری از شروع جمله با انگلیسی

    match = re.match(
        r"^([A-Za-z]+)[\s-](.*)",
        text
    )



    if match:


        first = match.group(1)

        rest = match.group(2)



        converted = replace_official_names(
            first
        )


        text = (
            converted
            +
            " "
            +
            rest
        )



    return text





def process_news(title, summary):


    print(
        "🤖 Processing News..."
    )


    fa_title = translate_text(
        title
    )


    fa_summary = translate_text(
        summary
    )



    fa_title = apply_style(
        fa_title
    )


    fa_summary = apply_style(
        fa_summary
    )



    fa_title = fix_rtl_start(
        fa_title
    )



    # ورود به موتور بازنویسی

    rewritten = rewrite_news(

        fa_title,

        fa_summary

    )



    final_title = rewritten.get(

        "title",

        fa_title

    )



    final_summary = rewritten.get(

        "summary",

        fa_summary

    )



    # آخرین چک اسم‌ها

    final_title = replace_official_names(

        final_title

    )


    final_summary = replace_official_names(

        final_summary

    )



    if not final_summary:


        final_summary = final_title




    return {


        "title":

        final_title,



        "summary":

        final_summary


    }
