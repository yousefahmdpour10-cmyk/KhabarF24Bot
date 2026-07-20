"""
KhabarF24 AI Processor v7.2

Pipeline:
    News Fetcher v7
        ↓
    Source Normalize
        ↓
    Brand Protection
        ↓
    Language Detection + Skip Persian
        ↓
    Translation (only if needed)
        ↓
    Cleanup + Ad Removal
        ↓
    Summary Generator (Professional)
        ↓
    Official Names Restore
        ↓
    RTL Cleaner
        ↓
    Formatter Ready
"""

import re
import html
from deep_translator import GoogleTranslator

# Importهای موجود پروژه
from brand_dictionary import replace_official_names
from rtl_cleaner import fix_rtl_text

print("🤖 KhabarF24 AI Processor v7.2 Loaded (8 قابلیت جدید اضافه شد)")

# =====================================================
# 1. تشخیص زبان (فارسی/انگلیسی)
# =====================================================
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0  # برای تکرارپذیری
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("⚠️ langdetect نصب نیست. از روش ساده استفاده می‌شود.")


def detect_language(text: str) -> str:
    """تشخیص زبان - اولویت با فارسی"""
    if not text or len(text.strip()) < 10:
        return "unknown"
    
    text_clean = re.sub(r'https?://\S+|www\.\S+', '', text)  # حذف لینک
    
    if LANGDETECT_AVAILABLE:
        try:
            lang = detect(text_clean[:500])  # کافی است
            if lang == 'fa':
                return 'fa'
            if lang == 'en':
                return 'en'
        except:
            pass
    
    # روش پشتیبان ساده و سریع (بدون وابستگی)
    persian_chars = len(re.findall(r'[\u0600-\u06FF\uFB8A-\uFBFF]', text_clean))
    total_chars = len(re.sub(r'\s+', '', text_clean))
    
    if total_chars == 0:
        return "unknown"
    
    persian_ratio = persian_chars / total_chars
    return 'fa' if persian_ratio > 0.15 else 'en'


# =====================================================
# 2. عدم ترجمه خبرهای فارسی
# =====================================================
def translate_text(text: str, target_lang="fa"):
    if not text:
        return ""
    
    detected = detect_language(text)
    if detected == 'fa':
        return text.strip()  # خبر فارسی → بدون ترجمه
    
    try:
        result = GoogleTranslator(source="auto", target=target_lang).translate(text)
        return result.strip()
    except Exception as e:
        print(f"Translation Error: {e}")
        return text


# =====================================================
# Cleanup + حذف متن‌های تبلیغاتی
# =====================================================
BAD_TRANSLATIONS = [
    "این متن", "به پایان می دهد", "مورد حمله قرار داد", "می باشد",
    "یک اندازه", "در این مقاله", "این خبر", "ادامه مطلب", "مطلب مرتبط",
    "لینک خبر", "منبع:", "Sponsored", "Advertisement", "Click here",
]

AD_PATTERNS = [
    r'تبلیغات?.*', r'Sponsored.*', r'Advertisement.*',
    r'📌.*', r'🔗.*', r'برای خواندن ادامه.*',
    r'فالو کنید.*', r'در اینستاگرام.*'
]

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = html.unescape(text)
    
    # حذف الگوهای تبلیغاتی
    for pattern in AD_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    for bad in BAD_TRANSLATIONS:
        text = text.replace(bad, "")
    
    text = re.sub(r"<.*?>", "", text)          # حذف تگ‌ها
    text = re.sub(r"\s+", " ", text)           # فضای اضافی
    return text.strip()


# =====================================================
# Protect Numbers + Brands (حفظ کامل)
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
# 3+4. تیتر کوتاه و جذاب + خلاصه حرفه‌ای
# =====================================================
def create_attractive_title(text: str) -> str:
    """تیتر کوتاه، جذاب و مناسب فارسی (حداکثر ۷۰ کاراکتر)"""
    text = clean_text(text)
    if len(text) <= 70:
        return text
    
    # روش ساده اما مؤثر: پیدا کردن جمله/بخش مهم
    sentences = re.split(r'[.!؟]', text)
    for sent in sentences:
        sent = sent.strip()
        if 30 <= len(sent) <= 70 and any(kw in sent for kw in ['شد', 'کرد', 'است', 'می‌شود', 'خواهد']):
            return sent[:70]
    
    return text[:68] + "..."


def create_professional_summary(title: str, summary: str, content: str) -> str:
    """خلاصه حرفه‌ای - نه اولین جمله"""
    source = summary or content or title
    if not source:
        return ""
    
    source = clean_text(source)
    
    # تقسیم به جملات
    sentences = re.split(r'[.!؟\n]+', source)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    
    if not sentences:
        return source[:250]
    
    # اولویت: جملات حاوی اعداد، نام‌ها یا فعل مهم
    important = []
    for s in sentences[:8]:  # فقط چند جمله اول را بررسی کن
        if any(c.isdigit() for c in s) or len(re.findall(r'\b[A-Z][a-z]+\b', s)) > 0:
            important.append(s)
    
    if important:
        best = max(important, key=len)
        return best[:280]
    
    # fallback: دومین یا سومین جمله (معمولاً بهتر از اول است)
    return sentences[1] if len(sentences) > 1 else sentences[0][:280]


# =====================================================
# Main Processor
# =====================================================
def process_news(news: dict) -> dict:
    if not isinstance(news, dict):
        return {}

    title = news.get("title", "")
    summary = news.get("summary", "")
    content = news.get("content", "")
    source = news.get("source", "Unknown")
    category = news.get("category", "world")

    print("🤖 KhabarF24 AI Processing...")

    # ۱. حفاظت از نام‌های رسمی (قبل از ترجمه)
    protected_title = replace_official_names(title)
    protected_summary = replace_official_names(summary)
    protected_content = replace_official_names(content)

    # ۲. ترجمه (فقط اگر لازم باشد)
    fa_title = translate_text(protected_title)
    fa_summary = translate_text(protected_summary)

    if not fa_summary:
        fa_summary = translate_text(protected_content)

    # ۳. Cleanup
    fa_title = clean_text(fa_title)
    fa_summary = clean_text(fa_summary)

    # ۴. حفاظت اعداد
    fa_title = protect_numbers(title, fa_title)
    fa_summary = protect_numbers(content or summary, fa_summary)

    # ۵. بازگردانی نام‌ها
    fa_title = replace_official_names(fa_title)
    fa_summary = replace_official_names(fa_summary)

    # ۶. تیتر کوتاه و جذاب
    fa_title = create_attractive_title(fa_title)

    # ۷. خلاصه حرفه‌ای
    fa_summary = create_professional_summary(fa_title, fa_summary, content)

    # ۸. RTL
    fa_title = fix_rtl_text(fa_title)
    fa_summary = fix_rtl_text(fa_summary)

    return {
        "title": fa_title,
        "summary": fa_summary,
        "content": content,      # محتوای اصلی انگلیسی/فارسی
        "source": source,
        "category": category
    }
