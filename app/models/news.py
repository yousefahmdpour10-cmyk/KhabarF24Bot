"""
مدل خبر پردازش‌شده

این مدل فقط برای خبرهایی استفاده می‌شود که مراحل پردازش را طی کرده‌اند
و آماده انتشار یا ذخیره‌سازی هستند.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from app.models.news_status import NewsStatus


@dataclass
class News:
    """
    مدل خبر نهایی
    """

    # شناسه
    id: Optional[str] = None

    # اطلاعات اصلی
    title: str = ""
    content: str = ""
    summary: str = ""

    # لینک‌ها
    url: str = ""
    image_url: str = ""

    # اطلاعات منبع
    source: str = ""
    source_id: str = ""

    # زبان و کشور
    language: str = ""
    country: str = ""

    # زمان‌ها
    published_at: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    processed_at: datetime = field(default_factory=datetime.utcnow)

    # دسته‌بندی
    category: str = ""
    subcategory: str = ""

    # فقط اگر خبر ورزشی باشد
    sport: str = ""

    # موقعیت جغرافیایی خبر (در آینده)
    location: str = ""

    # هشتگ‌ها
    hashtags: List[str] = field(default_factory=list)

    # ایموجی منتخب
    emoji: str = ""

    # امتیاز اهمیت
    priority: int = 0

    # امتیاز اعتبار (فقط داخلی)
    credibility_score: float = 0.0

    # وضعیت خبر
    status: NewsStatus = NewsStatus.RAW

    # آیا منتشر شده؟
    published: bool = False

    # اطلاعات اضافی
    metadata: dict = field(default_factory=dict)
