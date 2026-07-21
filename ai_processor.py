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


def process_news(news: dict) -> dict:
    if not isinstance(news, dict):
        return {}

    title = news.get("title", "").strip()
    summary = news.get("summary", "").strip()
    content = news.get("content", "").strip()
    source = news.get("source", "نامشخص").strip()   # مهم!
    category = news.get("category", "world").strip()

    print(f"🤖 Processing: {source} | {title[:50]}...")

    # حفاظت از نام‌ها
    protected_title = replace_official_names(title)
    protected_summary = replace_official_names(summary)
    protected_content = replace_official_names(content)

    # ترجمه فقط اگر انگلیسی باشد
    fa_title = translate_text(protected_title)
    fa_summary = translate_text(protected_summary) or translate_text(protected_content)

    # Cleanup قوی
    fa_title = clean_text(fa_title)
    fa_summary = clean_text(fa_summary)

    # حفاظت اعداد و برند
    fa_title = protect_numbers(title, fa_title)
    fa_summary = protect_numbers(content or summary, fa_summary)

    fa_title = replace_official_names(fa_title)
    fa_summary = replace_official_names(fa_summary)

    # تیتر و خلاصه
    fa_title = create_attractive_title(fa_title)
    fa_summary = create_professional_summary(fa_title, fa_summary, content)

    # RTL
    fa_title = fix_rtl_text(fa_title)
    fa_summary = fix_rtl_text(fa_summary)

    return {
        "title": fa_title,
        "summary": fa_summary,
        "source": source,          # خیلی مهم!
        "category": category,
        "image_url": news.get("image_url")
    }
