"""
KhabarF24 AI Processor v7.3
Compatible with formatter v7.2
"""

import re
import html
from deep_translator import GoogleTranslator

from brand_dictionary import replace_official_names
from rtl_cleaner import fix_rtl_text

print("🤖 KhabarF24 AI Processor v7.3 Loaded")


# =====================================================
# تشخیص زبان
# =====================================================
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


def detect_language(text: str) -> str:
    if not text or len(text.strip()) < 10:
        return "unknown"
    
    text_clean = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    if LANGDETECT_AVAILABLE:
        try:
            lang = detect(text_clean[:500])
            if lang in ['fa', 'en']:
                return lang
        except:
            pass
    
    # روش پشتیبان
    persian_chars = len(re.findall(r'[\u0600-\u06FF\uFB8A-\uFBFF]', text_clean))
    total_chars = len(re.sub(r'\s+', '', text_clean))
    return 'fa' if total_chars > 0 and (persian_chars / total_chars) > 0.15 else 'en'


# =====================================================
# ترجمه
# =====================================================
def translate_text(text: str) -> str:
    if not text:
        return ""
    
    if detect_language(text) == 'fa':
        return text.strip()
    
    try:
        result = GoogleTranslator(source="auto", target="fa").translate(text)
        return result.strip()
    except Exception as e:
        print(f"Translation Error: {e}")
        return text


# =====================================================
# Cleanup
# =====================================================
BAD_TRANSLATIONS = ["این متن", "به پایان می دهد", "می باشد", "در این مقاله", "این خبر", "ادامه مطلب", "Sponsored", "Advertisement"]

AD_PATTERNS = [r'تبلیغات?.*', r'Sponsored.*', r'Advertisement.*', r'📌.*', r'برای خواندن ادامه.*']

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = html.unescape(text)
    
    for pattern in AD_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    for bad in BAD_TRANSLATIONS:
        text = text.replace(bad, "")
    
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =====================================================
# Protect Numbers
# =====================================================
def protect_numbers(original: str, translated: str) -> str:
    if not original:
        return translated
    numbers = re.findall(r'\d+[.,]?\d*', original)
    for num in numbers:
        if num not in translated:
            translated += f" {num}"
    return translated.strip()


# =====================================================
# Title & Summary
# =====================================================
def create_attractive_title(text: str) -> str:
    text = clean_text(text)
    if len(text) <= 70:
        return text
    
    sentences = re.split(r'[.!؟]', text)
    for sent in sentences:
        sent = sent.strip()
        if 30 <= len(sent) <= 70:
            return sent[:70]
    return text[:68] + "..."


def create_professional_summary(title: str, summary: str, content: str) -> str:
    source = summary or content or title
    if not source:
        return ""
    
    source = clean_text(source)
    sentences = [s.strip() for s in re.split(r'[.!؟\n]+', source) if len(s.strip()) > 30]
    
    if not sentences:
        return source[:250]
    
    # اولویت به جملات مهم
    for s in sentences:
        if any(c.isdigit() for c in s) or len(re.findall(r'\b[A-Z][a-z]+\b', s)) > 1:
            return s[:280]
    
    return sentences[1] if len(sentences) > 1 else sentences[0][:280]


# =====================================================
# Main Process
# =====================================================
def process_news(news: dict) -> dict:
    if not isinstance(news, dict):
        return {}

    title = news.get("title", "")
    summary = news.get("summary", "")
    content = news.get("content", "")
    source = news.get("source", "Unknown")
    category = news.get("category", "world")
    image_url = news.get("image_url") or news.get("image") or news.get("media_url")  # برای آینده

    print("🤖 KhabarF24 AI Processing...")

    # Brand Protection
    protected_title = replace_official_names(title)
    protected_summary = replace_official_names(summary)
    protected_content = replace_official_names(content)

    # Translation
    fa_title = translate_text(protected_title)
    fa_summary = translate_text(protected_summary) or translate_text(protected_content)

    # Cleanup
    fa_title = clean_text(fa_title)
    fa_summary = clean_text(fa_summary)

    # Numbers
    fa_title = protect_numbers(title, fa_title)
    fa_summary = protect_numbers(content or summary, fa_summary)

    # Restore Names
    fa_title = replace_official_names(fa_title)
    fa_summary = replace_official_names(fa_summary)

    # Attractive Title + Professional Summary
    fa_title = create_attractive_title(fa_title)
    fa_summary = create_professional_summary(fa_title, fa_summary, content)

    # RTL
    fa_title = fix_rtl_text(fa_title)
    fa_summary = fix_rtl_text(fa_summary)

    return {
        "title": fa_title,
        "summary": fa_summary,
        "source": source,
        "category": category,
        "image_url": image_url,          # برای استفاده در formatter و image_processor
        "content": content
    }
