from deep_translator import GoogleTranslator
import re

from entities import PROTECTED_ENTITIES
from brand_dictionary import replace_official_names



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


    original = text


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


        # اصلاح نام تیم‌ها و برندها

        translated = replace_official_names(
            translated
        )


        return translated.strip()



    except Exception as e:

        print(f"Translation Error: {e}")

        return original





def improve_persian_style(text):


    if not text:
        return ""



    replacements = {


        "به پایان دهد": "به پایان داد",

        "به دست می آورد": "کسب کرد",

        "به دست آورد": "کسب کرد",

        "به دست می آورند": "کسب کردند",

        "می باشد": "است",

        "در حال حاضر": "اکنون",

        "اعلام کرد که": "اعلام کرد",

        "های ": "‌های ",

        "ه ای": "ه‌ای",

    }



    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )



    return text.strip()





def create_headline(title):


    title = improve_persian_style(title)


    # تبدیل نام‌های رسمی در تیتر

    title = replace_official_names(
        title
    )


    if len(title) > 100:


        parts = title.split("؛")


        if len(parts) > 1:

            title = parts[0]



    return title.strip()





def summarize_text(text, max_length=300):


    text = clean_text(text)


    text = improve_persian_style(text)


    text = replace_official_names(
        text
    )



    if len(text) <= max_length:

        return text



    text = text[:max_length]



    last_dot = text.rfind(".")


    if last_dot > 100:

        text = text[:last_dot]



    return text.strip()





def process_news(title, summary):


    print("🤖 KhabarF24 AI v3.3")



    fa_title = translate_text(title)

    fa_summary = translate_text(summary)



    fa_title = create_headline(
        fa_title
    )


    fa_summary = summarize_text(
        fa_summary
    )



    if not fa_summary:

        fa_summary = fa_title



    return {

        "title": fa_title,

        "summary": fa_summary

    }
