"""
KhabarF24 News Rewriter v8.0
Natural Persian Rewriting + Cleaning
"""

import re
import html
import logging

logger = logging.getLogger(__name__)

print("✍️ KhabarF24 News Rewriter v8.0 Loaded")


REWRITE_RULES = {
    "اعلام کرد که": "اعلام کرد",
    "گفت که": "گفت",
    "می باشد": "است",
    "در حال حاضر": "اکنون",
    "به پایان دهد": "پایان دهد",
    "مورد حمله قرار داد": "حمله کرد",
    "مورد حمله قرار گرفت": "هدف حمله قرار گرفت",
    "فیلم نشان می دهد": "تصاویر نشان می‌دهد",
    "ویدئو نشان می دهد": "تصاویر نشان می‌دهد",
    "به وقوع پیوست": "رخ داد",
    "صورت گرفت": "انجام شد",
    "رئیس جمهور": "رئیس‌جمهور",
    "ایالات متحده": "آمریکا",
    "به دنبال آن": "پس از آن",
    "در بحبوحه": "در پی",
    "باعث شد": "موجب شد",
    "به دست آورد": "کسب کرد",
    "مدل باز": "مدل متن‌باز",
}


def apply_rules(text: str) -> str:
    if not text:
        return ""
    for old, new in REWRITE_RULES.items():
        text = text.replace(old, new)
    return text


def clean_spaces(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_rss_breaks(text: str) -> str:
    bad_endings = ["...", "…", "ادامه", "ادامه مطلب", "بیشتر بخوانید", "[...]", "ادامه خبر"]
    for item in bad_endings:
        if text.endswith(item):
            text = text[:-len(item)].strip()
    return text


def improve_title(title: str, limit: int = 85) -> str:
    title = clean_spaces(title)
    title = apply_rules(title)
    title = clean_rss_breaks(title)
    title = re.sub(r"^(در پی|گزارش می‌دهد که|طبق گزارش)", "", title, flags=re.IGNORECASE).strip()
    
    if len(title) > limit:
        for sep in ["؛", "،", "-", ":"]:
            if sep in title:
                part = title.split(sep)[0].strip()
                if len(part) > 30:
                    return part
    return title[:limit].strip()


def improve_summary(summary: str) -> str:
    summary = clean_spaces(summary)
    summary = apply_rules(summary)
    summary = clean_rss_breaks(summary)
    if summary and summary[-1] not in ".!؟":
        summary += "."
    return summary.strip()


def rewrite_news(title: str, summary: str):
    new_title = improve_title(title)
    new_summary = improve_summary(summary)
    
    logger.debug(f"Rewritten title: {new_title[:70]}...")
    
    return {
        "title": new_title,
        "summary": new_summary
    }
