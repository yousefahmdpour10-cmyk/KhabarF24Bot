"""
KhabarF24 AI Processor v8.1
Translation + Rewriting + Professional Output
"""

import re
import html
import logging
from typing import Dict

from deep_translator import GoogleTranslator
from brand_dictionary import replace_official_names
from rtl_cleaner import fix_rtl_text
from news_rewriter import rewrite_news   # ← ادغام شد

logger = logging.getLogger(__name__)

print("🤖 KhabarF24 AI Processor v8.1 Loaded")


# =====================================================
# Language Detection
# =====================================================
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


def detect_language(text: str) -> str:
    if not text or len(text.strip()) < 15:
        return "unknown"

    text_clean = re.sub(r'https?://\S+|www\.\S+', '', text)

    if LANGDETECT_AVAILABLE:
        try:
            lang = detect(text_clean[:600])
            if lang in ['fa', 'ar', 'en']:
                return lang
        except:
            pass

    persian_chars = len(re.findall(r'[\u0600-\u06FF\uFB8A-\uFBFF]', text_clean))
    total_chars = len(re.sub(r'\s+', '', text_clean))
    return 'fa' if total_chars > 0 and (persian_chars / total_chars) > 0.12 else 'en'


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
# Cleanup
# =====================================================
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def protect_numbers(original: str, translated: str) -> str:
    if not original:
        return translated
    numbers = re.findall(r'\d+[.,]?\d*', original)
    for num in numbers:
        if num not in translated:
            translated += f" ({num})"
    return translated.strip()


# =====================================================
# Main Processing
# =====================================================
def process_news(news: Dict) -> Dict:
    if not isinstance(news, dict):
        logger.error("Invalid input to AI processor")
        return {}

    title = news.get("title", "")
    summary = news.get("summary", "")
    content = news.get("content", "")
    source = news.get("source", "Unknown")
    category = news.get("category", "world")
    image_url = news.get("image_url") or news.get("image")
    link = news.get("link", "")

    logger.info(f"🤖 Processing: {title[:70]}...")

    # 1. Brand Protection
    title = replace_official_names(title)
    summary = replace_official_names(summary)
    content = replace_official_names(content)

    # 2. Translation
    fa_title = translate_to_persian(title)
    fa_summary = translate_to_persian(summary) or translate_to_persian(content)

    # 3. Natural Persian Rewriting (مهم!)
    rewritten = rewrite_news(fa_title, fa_summary)
    fa_title = rewritten["title"]
    fa_summary = rewritten["summary"]

    # 4. Final Cleanup
    fa_title = clean_text(fa_title)
    fa_summary = clean_text(fa_summary)

    fa_title = protect_numbers(title, fa_title)
    fa_summary = protect_numbers(content or summary, fa_summary)

    # 5. Attractive Title & Professional Summary
    fa_title = fa_title[:85] if len(fa_title) > 85 else fa_title
    if len(fa_summary) > 280:
        fa_summary = fa_summary[:280].rsplit(" ", 1)[0] + "..."

    # 6. RTL Fix
    fa_title = fix_rtl_text(fa_title)
    fa_summary = fix_rtl_text(fa_summary)

    return {
        "title": fa_title,
        "summary": fa_summary,
        "source": source,
        "category": category,
        "image_url": image_url,
        "link": link,
        "original_title": title
    }
