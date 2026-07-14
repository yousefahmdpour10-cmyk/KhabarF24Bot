from deep_translator import GoogleTranslator
import re

from entities import PROTECTED_ENTITIES


# اصطلاحات رایج خبری که ترجمه ماشینی خراب می‌کند
NEWS_PHRASES = {

    "put off": "منصرف کردن",
    "steps down": "کناره‌گیری کردن",
    "steps aside": "کناره‌گیری کردن",
    "rules out": "منتفی دانستن",
    "rules out the possibility": "احتمال را رد کرد",
    "set to": "قرار است",
    "expected to": "انتظار می‌رود",
    "amid": "در بحبوحه",
    "amid growing": "در پی افزایش",
    "backs down": "عقب‌نشینی کرد",
    "backs away": "عقب‌نشینی کرد",
    "warns": "هشدار داد",
    "claims": "ادعا کرد",
    "reveals": "فاش کرد",
    "announces": "اعلام کرد",
    "launches": "راه‌اندازی کرد",
    "joins": "پیوست",
    "leaves": "ترک کرد",
    "wins": "پیروز شد",
    "defeats": "شکست داد",

}



def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        "<.*?>",
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


    for entity in PROTECTED_ENTITIES:

        if entity in text:

            key = f"ENTITY{counter}"

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





def apply_news_dictionary(text):

    for old, new in NEWS_PHRASES.items():

        text = text.replace(
            old,
            new
        )

    return text





def translate_text(text):

    text = clean_text(text)

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


        translated = apply_news_dictionary(
            translated
        )


        return translated.strip()



    except Exception as e:

        print(
            f"Translation Error: {e}"
        )

        return original





def improve_persian_style(text):

    if not text:
        return ""


    replacements = {

        "به پایان دهد": "به پایان داد",

        "به پایان می رساند": "به پایان رساند",

        "به دست می آورد": "کسب می‌کند",

        "به دست آورد": "کسب کرد",

        "می باشد": "است",

        "در حال حاضر": "اکنون",

        "اعلام کرد که": "اعلام کرد",

        "می کند": "می‌کند",

        "خواهد کرد": "خواهد کرد",

    }



    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )


    return text.strip()





def create_headline(title):

    title = improve_persian_style(
        title
    )


    # حذف تیترهای خیلی طولانی

    if len(title) > 90:

        parts = title.split("؛")

        if len(parts) > 1:

            title = parts[0]


    return title.strip()





def summarize_text(text, max_length=300):

    text = clean_text(
        text
    )


    text = improve_persian_style(
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

    print(
        "🤖 KhabarF24 AI v4"
    )


    fa_title = translate_text(
        title
    )


    fa_summary = translate_text(
        summary
    )


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
