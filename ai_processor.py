from deep_translator import GoogleTranslator
import re


def clean_text(text):

    if not text:
        return ""

    text = re.sub("<.*?>", "", text)

    text = " ".join(text.split())

    return text.strip()



def translate_text(text):

    text = clean_text(text)

    if not text:
        return ""

    try:

        translated = GoogleTranslator(
            source="auto",
            target="fa"
        ).translate(text)

        return translated.strip()

    except Exception as e:

        print(f"Translation Error: {e}")

        return text



def improve_news_style(text):

    if not text:
        return ""


    replacements = {

        "جام جهانی لالیگا": "جام جهانی فوتبال",

        "نیمه نهایی": "نیمه‌نهایی",

        "ستاره های": "ستاره‌های",

        "به تعویق افتاد": "به تعویق افتاده است",

        "حضور دارند": "حضور دارند",

        "پس از یک شکست": "پس از شکست",

        "اعلام کرد که": "اعلام کرد",

        "می باشد": "است",

    }


    for old, new in replacements.items():

        text = text.replace(old, new)


    return text.strip()



def create_headline(title):

    title = improve_news_style(title)


    if len(title) > 90:

        parts = title.split("؛")

        if len(parts) > 1:
            title = parts[0]


    return title.strip()



def summarize_text(text, max_length=280):

    text = clean_text(text)


    if len(text) <= max_length:

        return improve_news_style(text)


    text = text[:max_length]


    last_dot = text.rfind(".")

    if last_dot > 100:

        text = text[:last_dot]


    return improve_news_style(text.strip())



def process_news(title, summary):


    print("🤖 Processing news...")


    fa_title = translate_text(title)

    fa_summary = translate_text(summary)


    fa_title = create_headline(fa_title)

    fa_summary = summarize_text(fa_summary)



    if not fa_summary:

        fa_summary = fa_title



    print("TITLE:", fa_title)

    print("SUMMARY:", fa_summary)



    return {

        "title": fa_title,

        "summary": fa_summary

    }
