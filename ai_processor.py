from deep_translator import GoogleTranslator
import re
import html

from entities import PROTECTED_ENTITIES
from places import PROTECTED_PLACES
from brand_dictionary import replace_official_names


print("🤖 KhabarF24 AI v4.6 Translation Engine")



STYLE_REPLACEMENTS = {

    "می شود":
    "می‌شود",

    "می شود":
    "شد",

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

    "بدون جنگ، بدون صلح":
    "نه جنگ، نه صلح",

    "بن بست":
    "بن‌بست",

}



NEWS_WORDS = {

    "claims":
    "مدعی شد",

    "alleges":
    "مدعی شد",

    "accuses":
    "متهم کرد",

    "lawsuit":
    "شکایت حقوقی",

    "announces":
    "اعلام کرد",

    "reveals":
    "فاش کرد",

    "warns":
    "هشدار داد",

    "joins":
    "پیوست",

}





def clean_text(text):

    if not text:
        return ""

    text = html.unescape(text)

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


    all_entities = (
        PROTECTED_ENTITIES
        +
        PROTECTED_PLACES
    )


    for entity in all_entities:

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

    for key,value in protected.items():

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


        # اصلاح نام‌ها بعد از ترجمه

        translated = replace_official_names(
            translated
        )


        return translated.strip()


    except Exception as e:

        print(
            f"Translation Error: {e}"
        )

        return original





def improve_style(text):

    if not text:
        return ""


    for old,new in NEWS_WORDS.items():

        text = text.replace(
            old,
            new
        )


    for old,new in STYLE_REPLACEMENTS.items():

        text = text.replace(
            old,
            new
        )


    return text.strip()





def fix_rtl(text):

    if not text:
        return ""


    # اگر جمله با کلمه انگلیسی شروع شد

    match = re.match(
        r"^([A-Za-z]+)\s+(.*)",
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





def rewrite_title(title):

    title = improve_style(
        title
    )


    title = replace_official_names(
        title
    )


    title = fix_rtl(
        title
    )


    return title.strip()





def rewrite_summary(summary):

    summary = improve_style(
        summary
    )


    summary = replace_official_names(
        summary
    )


    return summary.strip()





def process_news(title, summary):


    fa_title = translate_text(
        title
    )


    fa_summary = translate_text(
        summary
    )


    fa_title = rewrite_title(
        fa_title
    )


    fa_summary = rewrite_summary(
        fa_summary
    )


    if not fa_summary:

        fa_summary = fa_title



    return {

        "title":
        fa_title,

        "summary":
        fa_summary

    }
