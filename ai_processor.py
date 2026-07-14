from deep_translator import GoogleTranslator
import re


def clean_text(text):
    if not text:
        return ""

    # حذف تگ‌های HTML
    text = re.sub("<.*?>", "", text)

    # حذف فاصله‌های اضافی
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



def summarize_text(text, max_length=250):

    text = clean_text(text)

    if len(text) <= max_length:
        return text

    # کوتاه‌سازی هوشمند اولیه
    text = text[:max_length]

    # جلوگیری از قطع وسط جمله
    last_dot = text.rfind(".")

    if last_dot > 80:
        text = text[:last_dot]

    return text.strip()



def process_news(title, summary):

    fa_title = translate_text(title)

    fa_summary = translate_text(summary)

    fa_summary = summarize_text(fa_summary)

    return {
        "title": fa_title,
        "summary": fa_summary
    }
