"""
KhabarF24 AI Processor v8.0
Free AI Processing + Translation + Professional Formatting
"""

import re
import html
import logging
from typing import Dict

from deep_translator import GoogleTranslator
from brand_dictionary import replace_official_names
from rtl_cleaner import fix_rtl_text

logger = logging.getLogger(__name__)

print("🤖 KhabarF24 AI Processor v8.0 Loaded")

# =====================================================
# Language Detection
# =====================================================
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logger.warning("langdetect not installed. Using fallback detection.")


def detect_language(text: str) -> str:
    if not text or len(text.strip()) < 15:
        return "unknown"

    # Remove URLs
    text_clean = re.sub(r'https?://\S+|www\.\S+', '', text)

    if LANGDETECT_AVAILABLE:
        try:
            lang = detect(text_clean[:600])
            if lang in ['fa', 'ar', 'en']:
                return lang
        except:
            pass

    # Fallback Persian detection
    persian_chars = len(re.findall(r'[\u0600-\u06FF\uFB8A-\uFBFF]', text_clean))
    total_chars = len(re.sub(r'\s+', '', text_clean))
    
    if total_chars > 0 and (persian_chars / total_chars) > 0.12:
        return 'fa'
    return 'en'


# =====================================================
# Translation
# =====================================================
def translate_to_persian(text: str) -> str:
    if not text:
        return ""
    
    if detect_language(text) == 'fa':
        return text.strip()

    try:
        result = GoogleTranslator(source="auto", target="fa").translate(text[:4500])
        return result.strip() if result else text
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text


# =====================================================
# Text Cleanup
# =====================================================
BAD_PHRASES = [
    "این متن", "به پایان می‌رسد", "می‌باشد", "در این مقاله", 
    "این خبر", "ادامه مطلب", "Sponsored", "Advertisement", 
    "برای خواندن کامل", "کلیک کنید"
]

AD_PATTERNS = [
    r'تبلیغات?.*', r'Sponsored.*', r'Advertisement.*', 
    r'📌.*', r'برای خواندن ادامه.*', r'Click here.*'
]

def clean_text(text: str) -> str:
    if not text:
        return ""

    text = html.unescape(text)
    
    # Remove ad patterns
    for pattern in AD_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    # Remove bad phrases
    for phrase in BAD_PHRASES:
        text = text.replace(phrase, "")

    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def protect_numbers(original: str, translated: str) -> str:
    """Keep important numbers from original text"""
    if not original:
        return translated
    numbers = re.findall(r'\d+[.,]?\d*', original)
    for num in numbers:
        if num not in translated:
            translated = translated + f" ({num})"
    return translated.strip()


# =====================================================
# Title & Summary Generation
# =====================================================
def create_attractive_title(text: str) -> str:
    text = clean_text(text)
    if len(text) <= 75:
        return text

    # Try to find good sentence
    sentences = re.split(r'[.!؟؟!]', text)
    for sent in sentences:
        sent = sent.strip()
        if 35 <= len(sent) <= 75:
            return sent[:75]
    return text[:72] + "..."


def create_professional_summary(title: str, summary: str, content: str) -> str:
    source_text = summary or content or title
    if not source_text:
        return ""

    source_text = clean_text(source_text)
    sentences = [s.strip() for s in re.split(r'[.!؟\n]+', source_text) if len(s.strip()) > 25]

    if not sentences:
        return source_text[:280]

    # Prefer informative sentences
    for s in sentences[:5]:
        if any(c.isdigit() for c in s) or len(re.findall(r'\b[A-Z][a-z]+\b', s)) >= 1:
            return s[:285]

    return sentences[0][:280]


# =====================================================
# Main Processing Function
# =====================================================
def process_news(news: Dict) -> Dict:
    if not isinstance(news, dict):
        logger.error("Invalid news input to AI processor")
        return {}

    title = news.get("title", "")
    summary = news.get("summary", "")
    content = news.get("content", "")
    source = news.get("source", "Unknown")
    category = news.get("category", "world")
    image_url = news.get("image_url") or news.get("image")

    logger.info(f"🤖 Processing: {title[:70]}...")

    # Brand name protection
    title = replace_official_names(title)
    summary = replace_official_names(summary)
    content = replace_official_names(content)

    # Translation
    fa_title = translate_to_persian(title)
    fa_summary = translate_to_persian(summary) or translate_to_persian(content)

    # Cleanup & Enhancement
    fa_title = clean_text(fa_title)
    fa_summary = clean_text(fa_summary)

    fa_title = protect_numbers(title, fa_title)
    fa_summary = protect_numbers(content or summary, fa_summary)

    # Final Title & Summary
    fa_title = create_attractive_title(fa_title)
    fa_summary = create_professional_summary(fa_title, fa_summary, content)

    # RTL Fix
    fa_title = fix_rtl_text(fa_title)
    fa_summary = fix_rtl_text(fa_summary)

    return {
        "title": fa_title,
        "summary": fa_summary,
        "source": source,
        "category": category,
        "image_url": image_url,
        "original_title": title,   # برای لاگ و دیباگ
        "link": news.get("link")
    }
