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

        print("ORIGINAL:")
        print(text[:200])

        print("TRANSLATED:")
        print(translated[:200])

        return translated.strip()

    except Exception as e:
        print(f"Translation Error: {e}")
        return text



def summarize_text(text, max_length=300):

    text = clean_text(text)

    if not text:
        return ""

    if len(text) <= max_length:
        return text

    text = text[:max_length]

    last_dot = text.rfind(".")

    if last_dot > 100:
        text = text[:last_dot]

    return text.strip()



def process_news(title, summary):

    title = clean_text(title)
    summary = clean_text(summary)

    print("🤖 AI PROCESS START")
    print("TITLE:", title)
    print("SUMMARY:", summary[:200])


    fa_title = translate_text(title)

    fa_summary = translate_text(summary)


    if not fa_summary:
        fa_summary = fa_title


    fa_summary = summarize_text(fa_summary)


    print("FINAL TITLE:", fa_title)
    print("FINAL SUMMARY:", fa_summary)


    return {
        "title": fa_title,
        "summary": fa_summary
    }
