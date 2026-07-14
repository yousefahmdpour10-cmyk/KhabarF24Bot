from deep_translator import GoogleTranslator
import re

from entities import PROTECTED_ENTITIES


def clean_text(text):

    if not text:
        return ""

    text = re.sub("<.*?>", "", text)

    text = " ".join(text.split())

    return text.strip()



def protect_entities(text):

    protected = {}

    counter = 0

    for entity in PROTECTED_ENTITIES:

        if entity in text:

            key = f"ENTITY_{counter}"

            protected[key] = entity

            text = text.replace(
                entity,
                key
            )

            counter += 1

    return text, protected



def restore_entities(text, protected):

    for key, value in protected.items():

        text = text.replace(
            key,
            value
        )

    return text



def translate_text(text):

    text = clean_text(text)

    if not text:
        return ""

    original_text = text


    try:

        text, protected = protect_entities(text)


        translated = GoogleTranslator(
            source="auto",
            target="fa"
        ).translate(text)


        translated = restore_entities(
            translated,
            protected
        )


        return translated.strip()


    except Exception as e:

        print(f"Translation Error: {e}")

        return original_text



def improve_news_style(text):

    if not text:
        return ""


    replacements = {

        "به دست می آورند": "کسب کردند",

        "به دست آورد": "کسب کرد",

        "نیمه نهایی": "نیمه‌نهایی",

        "برد": "پیروزی",

        "با هم": "درخشش",

        "می باشد": "است",

    }


    for old, new in replacements.items():

        text = text.replace(old, new)


    return text.strip()



def summarize_text(text, max_length=300):

    text = clean_text(text)


    if len(text) <= max_length:

        return improve_news_style(text)


    text = text[:max_length]


    last_dot = text.rfind(".")

    if last_dot > 100:

        text = text[:last_dot]


    return improve_news_style(text.strip())



def process_news(title, summary):


    print("🤖 KhabarF24 AI v2")


    fa_title = translate_text(title)

    fa_summary = translate_text(summary)


    fa_title = improve_news_style(fa_title)

    fa_summary = summarize_text(fa_summary)


    if not fa_summary:

        fa_summary = fa_title


    return {

        "title": fa_title,

        "summary": fa_summary

    }
