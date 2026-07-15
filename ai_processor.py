from deep_translator import GoogleTranslator
import re
import html

from entities import PROTECTED_ENTITIES
from places import PROTECTED_PLACES
from brand_dictionary import replace_official_names


print("🤖 KhabarF24 AI v4.5 RTL + Brand Mode")



NEWS_PHRASES = {

    "claims": "مدعی شد",
    "alleges": "مدعی شد",
    "accuses": "متهم کرد",

    "lawsuit": "شکایت حقوقی",

    "files a lawsuit":
    "شکایتی مطرح کرد",

    "joins":
    "پیوست",

    "announces":
    "اعلام کرد",

    "reveals":
    "فاش کرد",

}



STYLE_REPLACEMENTS = {

    "می شود":
    "می‌شود",

    "می شود":
    "شد",

    "بن بست":
    "بن‌بست",

    "بدون جنگ، بدون صلح":
    "نه جنگ، نه صلح",

    "در حال حاضر":
    "اکنون",

    "می باشد":
    "است",

}





def clean_text(text):

    if not text:
        return ""

    # تبدیل HTML entities

    text = html.unescape(text)


    # حذف تگ HTML

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


        return translated.strip()



    except Exception as e:

        print(
            f"Translation Error: {e}"
        )

        return original





def improve_style(text):

    for old,new in NEWS_PHRASES.items():

        text=text.replace(
            old,
            new
        )


    for old,new in STYLE_REPLACEMENTS.items():

        text=text.replace(
            old,
            new
        )


    return text.strip()





def fix_rtl_headline(text):

    if not text:
        return ""


    # اگر تیتر با انگلیسی شروع شد

    english_start = re.match(
        r"^[A-Za-z]",
        text
    )


    if english_start:


        words = text.split()


        if len(words) > 1:


            first = words[0]


            text = (
                first
                +
                " "
                +
                " ".join(words[1:])
            )


            text = replace_official_names(
                text
            )


    return text





def rewrite_headline(title):

    title = improve_style(
        title
    )


    title = replace_official_names(
        title
    )


    title = fix_rtl_headline(
        title
    )


    if len(title)>100:

        title = title[:100]


    return title.strip()





def rewrite_summary(summary):

    summary = improve_style(
        summary
    )


    summary = replace_official_names(
        summary
    )


    if len(summary)>320:

        summary=summary[:320]


    return summary.strip()





def process_news(title,summary):


    title = translate_text(
        title
    )


    summary = translate_text(
        summary
    )


    title = rewrite_headline(
        title
    )


    summary = rewrite_summary(
        summary
    )


    if not summary:

        summary=title


    return {

        "title":title,

        "summary":summary

    }
