from deep_translator import GoogleTranslator
import re

from entities import PROTECTED_ENTITIES
from brand_dictionary import replace_official_names



# =====================================
# 🧠 KhabarF24 AI v4.1
# Persian News Writer Engine
# =====================================


NEWS_PHRASES = {

    "put off": "منصرف کردن",
    "puts off": "منصرف می‌کند",
    "steps down": "کناره‌گیری کرد",
    "steps aside": "کناره‌گیری کرد",

    "rules out": "رد کرد",
    "rules out the possibility": "احتمال را رد کرد",

    "set to": "قرار است",
    "expected to": "انتظار می‌رود",

    "amid": "در بحبوحه",

    "backs down": "عقب‌نشینی کرد",
    "backs away": "عقب‌نشینی کرد",

    "warns": "هشدار داد",
    "reveals": "فاش کرد",
    "announces": "اعلام کرد",

    "joins": "پیوست",
    "leaves": "ترک کرد",

    "wins": "پیروز شد",
    "defeats": "شکست داد",

}





def clean_text(text):

    if not text:
        return ""

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


    for entity in PROTECTED_ENTITIES:

        if entity in text:

            key = f"KEEP{counter}"

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


        return translated.strip()



    except Exception as e:

        print(
            f"Translation Error: {e}"
        )

        return original





def apply_news_phrases(text):

    for old, new in NEWS_PHRASES.items():

        text = text.replace(
            old,
            new
        )

    return text





def improve_persian_style(text):

    if not text:
        return ""


    replacements = {


        "به پایان دهد":
        "به پایان داد",


        "به دست می آورد":
        "کسب می‌کند",


        "به دست آورد":
        "کسب کرد",


        "می باشد":
        "است",


        "در حال حاضر":
        "اکنون",


        "اعلام کرد که":
        "اعلام کرد",


        "خواهد شد":
        "خواهد شد",


        "می کند":
        "می‌کند",

    }


    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )


    return text.strip()





def fix_english_start(text):

    """
    جلوگیری از شروع جمله با برند انگلیسی
    """

    if not text:
        return ""


    words = [
        "Apple",
        "Google",
        "Microsoft",
        "OpenAI",
        "Tesla",
        "Samsung",
        "Meta"
    ]


    for word in words:

        if text.startswith(word):

            text = text.replace(
                word,
                "",
                1
            )

            text = word + " " + text.strip()


    return text.strip()





def create_headline(title):

    title = improve_persian_style(
        title
    )


    title = fix_english_start(
        title
    )


    # کوتاه سازی تیتر

    if len(title) > 100:

        parts = title.split("؛")

        if len(parts) > 1:

            title = parts[0]


    return title.strip()





def summarize_text(text, max_length=320):

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
        "🤖 KhabarF24 AI v4.1"
    )


    fa_title = translate_text(
        title
    )


    fa_summary = translate_text(
        summary
    )



    # اصلاح نام رسمی برندها

    fa_title = replace_official_names(
        fa_title
    )


    fa_summary = replace_official_names(
        fa_summary
    )



    # اصلاح لحن خبری

    fa_title = apply_news_phrases(
        fa_title
    )

    fa_summary = apply_news_phrases(
        fa_summary
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
