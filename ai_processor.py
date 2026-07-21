"""
KhabarF24 AI Processor v8.1
هوش مصنوعی پردازش خبر - بهینه شده با تمام ویژگی‌های درخواستی
"""

import re
import html
import logging
from typing import Dict

from deep_translator import GoogleTranslator
from brand_dictionary import replace_official_names
from rtl_cleaner import fix_rtl_text
from news_rewriter import rewrite_news

logger = logging.getLogger(__name__)

print("🤖 KhabarF24 AI Processor v8.1 Loaded")


def detect_language(text: str) -> str:
    """تشخیص زبان (فارسی یا انگلیسی)"""
    if not text or len(text.strip()) < 15:
        return "unknown"

    text_clean = re.sub(r'https?://\S+|www\.\S+', '', text)

    try:
        from langdetect import detect, DetectorFactory
        DetectorFactory.seed = 0
        lang = detect(text_clean[:700])
        if lang in ['fa', 'ar']:
            return 'fa'
        if lang == 'en':
            return 'en'
    except:
        pass

    # روش پشتیبان فارسی
    persian_ratio = len(re.findall(r'[\u0600-\u06FF\uFB8A-\uFBFF]', text_clean)) / max(1, len(text_clean))
    return 'fa' if persian_ratio > 0.15 else 'en'


def translate_to_persian(text: str) -> str:
    """ترجمه فقط در صورت نیاز"""
    if detect_language(text) == 'fa':
        return text.strip()   # ✅ عدم ترجمه خبر فارسی
    
    try:
        result = GoogleTranslator(source="auto", target="fa").translate(text[:4500])
        return result.strip() if result else text
    except:
        return text


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def process_news(news: Dict) -> Dict:
    title = news.get("title", "")
    summary = news.get("summary", "")
    content = news.get("content", "")
    source = news.get("source", "Unknown")
    category = news.get("category", "world")
    image_url = news.get("image_url")
    link = news.get("link")

    logger.info(f"🤖 Processing: {title[:65]}...")

    # حفاظت از برندها
    title = replace_official_names(title)
    summary = replace_official_names(summary)

    # ترجمه هوشمند
    fa_title = translate_to_persian(title)
    fa_summary = translate_to_persian(summary) or translate_to_persian(content)

    # طبیعی‌سازی فارسی
    rewritten = rewrite_news(fa_title, fa_summary)
    fa_title = rewritten["title"]
    fa_summary = rewritten["summary"]

    # تمیزکاری نهایی
    fa_title = clean_text(fa_title)
    fa_summary = clean_text(fa_summary)

    # تیتر کوتاه و جذاب
    if len(fa_title) > 85:
        fa_title = fa_title[:82] + "..."

    # خلاصه حرفه‌ای
    if len(fa_summary) > 280:
        fa_summary = fa_summary[:277] + "..."

    # RTL + نهایی
    fa_title = fix_rtl_text(fa_title)
    fa_summary = fix_rtl_text(fa_summary)

    return {
        "title": fa_title,
        "summary": fa_summary,
        "source": source,
        "category": category,
        "image_url": image_url,
        "link": link
    }
