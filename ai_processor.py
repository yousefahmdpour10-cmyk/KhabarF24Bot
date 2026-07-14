from deep_translator import GoogleTranslator
import re

from entities import PROTECTED_ENTITIES
from brand_dictionary import replace_official_names


print("🤖 KhabarF24 AI v4.3 Headline Writer")



NEWS_PHRASES = {

    # اصطلاحات خبری

    "claims": "مدعی شد",
    "claimed": "مدعی شد",

    "alleges": "مدعی شد",
    "alleged": "ادعا شده",

    "accuses": "متهم کرد",
    "accused": "متهم کرد",

    "sues": "شکایت کرد",

    "files a lawsuit": "شکایتی مطرح کرد",
    "files lawsuit": "شکایتی ثبت کرد",

    "lawsuit": "شکایت حقوقی",

    "officials": "مقام‌ها",

    "official": "رسمی",

    "administration": "دولت",

    "government officials": "مقام‌های دولتی",


    "put off": "منصرف کردن",

    "steps down": "کناره‌گیری کرد",

    "rules out": "رد کرد",

    "set to": "قرار است",

    "expected to": "انتظار می‌رود",

    "amid": "در بحبوحه",

    "warns": "هشدار داد",

    "reveals": "فاش کرد",

    "announces": "اعلام کرد",

    "joins": "پیوست",

    "wins": "پیروز شد",

    "defeats": "شکست داد",

}



STYLE_REPLACEMENTS = {


    "مدعی توطئه می شود":
    "مدعی توطئه شد",


    "مدعی توطئه می‌شود":
    "مدعی توطئه شد",


    "به دلیل":
    "به‌دلیل",


    "در حال حاضر":
    "اکنون",


    "می باشد":
    "است",


    "پیامدهای منطقه ای":
    "پیامدهای منطقه‌ای",


    "بن بست":
    "بن‌بست",


    "بدون جنگ، بدون صلح":
    "نه جنگ، نه صلح",


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





def improve_news_style(text):

    if not text:
        return ""


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


    return text.strip()





def rewrite_headline(title):

    title = improve_news_style(
        title
    )


    title = replace_official_names(
        title
    )


    # اصلاح شروع‌های ضعیف

    replacements = {


        "چرا":
        "بررسی",


        "ممکن است":
        "احتمال",


        "به نظر می رسد":
        "به نظر می‌رسد",


        "مدعی شد که":
        "مدعی شد",


    }


    for old, new in replacements.items():

        title = title.replace(
            old,
            new
        )


    # حذف علامت‌های اضافی

    title = title.replace(
        '"',
        ""
    )


    # کوتاه سازی تیتر

    if len(title) > 100:

        title = title[:100]

        if " " in title:

            title = title.rsplit(
                " ",
                1
            )[0]


    return title.strip()





def rewrite_summary(summary):

    summary = improve_news_style(
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


    title = rewrite_headline(
        title
    )


    summary = rewrite_summary(
        summary
    )


    if not summary:

        summary = title



    return {

        "title": title,

        "summary": summary

    }
