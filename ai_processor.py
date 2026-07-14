from deep_translator import GoogleTranslator
import re

from entities import PROTECTED_ENTITIES
from brand_dictionary import replace_official_names


print("🤖 KhabarF24 AI v4.2 News Writer")



NEWS_PHRASES = {

    "put off": "منصرف کردن",
    "puts off": "منصرف می‌کند",

    "steps down": "کناره‌گیری کرد",

    "rules out": "رد کرد",

    "set to": "قرار است",

    "expected to": "انتظار می‌رود",

    "amid": "در بحبوحه",

    "backs down": "عقب‌نشینی کرد",

    "warns": "هشدار داد",

    "reveals": "فاش کرد",

    "announces": "اعلام کرد",

    "joins": "پیوست",

    "leaves": "ترک کرد",

    "wins": "پیروز شد",

    "defeats": "شکست داد",

}



# اصلاح عبارت‌های ماشینی رایج
STYLE_REPLACEMENTS = {

    "ممکن است پایان یابد":
        "احتمال پایان آن افزایش یافته است",

    "در پیش است":
        "در انتظار است",

    "پیامدهای منطقه ای در پیش است":
        "می‌تواند پیامدهای منطقه‌ای داشته باشد",

    "صلح شکننده":
        "آتش‌بس شکننده",

    "بن بست طولانی":
        "بن‌بست چندساله",

    "بدون جنگ، بدون صلح":
        "وضعیت «نه جنگ، نه صلح»",

    "به شدت افزایش یافته":
        "افزایش یافته",

    "در حال حاضر":
        "اکنون",

    "می باشد":
        "است",

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

        print(
            f"Translation Error: {e}"
        )

        return original





def apply_dictionary(text):

    for old, new in NEWS_PHRASES.items():

        text = text.replace(
            old,
            new
        )


    for old, new in STYLE_REPLACEMENTS.items():

        text = text.replace(
            old,
            new
        )


    return text





def create_headline(title):

    title = apply_dictionary(
        title
    )


    title = replace_official_names(
        title
    )


    # حذف نقل قول‌های اضافی

    title = title.replace(
        '"',
        ""
    )


    # کوتاه سازی

    if len(title) > 95:

        title = title[:95]


        if " " in title:

            title = title.rsplit(
                " ",
                1
            )[0]


    return title.strip()





def create_summary(summary):

    summary = apply_dictionary(
        summary
    )


    summary = replace_official_names(
        summary
    )


    if len(summary) > 320:

        summary = summary[:320]


        if "." in summary:

            summary = summary.rsplit(
                ".",
                1
            )[0]


    return summary.strip()





def process_news(title, summary):


    title = translate_text(
        title
    )


    summary = translate_text(
        summary
    )



    title = create_headline(
        title
    )


    summary = create_summary(
        summary
    )


    if not summary:

        summary = title



    return {

        "title": title,

        "summary": summary

    }
