"""
مدل خبر خام

تمام خبرهایی که از RSS، سایت، API یا شبکه‌های اجتماعی دریافت می‌شوند
ابتدا به صورت RawNews وارد سیستم خواهند شد.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class RawNews:
    """
    مدل خبر خام
    """

    # شناسه خبر
    id: Optional[str] = None

    # عنوان
    title: str = ""

    # متن کامل
    content: str = ""

    # خلاصه اولیه
    summary: str = ""

    # لینک خبر
    url: str = ""

    # تصویر اصلی
    image_url: str = ""

    # نویسنده
    author: str = ""

    # تاریخ انتشار خبر
    published_at: Optional[datetime] = None

    # زمان دریافت توسط ربات
    fetched_at: datetime = field(default_factory=datetime.utcnow)

    # نام منبع
    source: str = ""

    # شناسه منبع
    source_id: str = ""

    # کشور
    country: str = ""

    # زبان
    language: str = ""

    # دسته اولیه (اگر منبع مشخص کرده باشد)
    category: str = ""

    # برچسب‌های منبع
    tags: List[str] = field(default_factory=list)

    # لینک‌های مرتبط
    related_urls: List[str] = field(default_factory=list)

    # داده خام دریافتی
    raw_data: dict = field(default_factory=dict)
