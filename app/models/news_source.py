"""
مدل منبع خبری

تمام منابع خبری پروژه KhabarF24 باید از این مدل استفاده کنند.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class NewsSource:
    """
    مدل اطلاعات یک منبع خبری
    """

    # ==========================================================
    # اطلاعات اصلی
    # ==========================================================

    # شناسه یکتا
    id: str

    # نام منبع
    name: str

    # نوع منبع
    # rss / website / api / social
    source_type: str

    # آدرس منبع
    url: str

    # کشور
    country: str

    # پرچم کشور
    flag: str

    # زبان
    language: str

    # ==========================================================
    # قابلیت‌های منبع
    # ==========================================================

    # آیا RSS دارد؟
    has_rss: bool = False

    # آیا API دارد؟
    has_api: bool = False

    # آیا امکان Web Scraping دارد؟
    supports_scraping: bool = False

    # آیا برای دریافت اطلاعات نیاز به مرورگر دارد؟
    requires_browser: bool = False

    # آیا نیاز به ورود (Login / Token) دارد؟
    requires_auth: bool = False

    # ==========================================================
    # تنظیمات منبع
    # ==========================================================

    # دسته‌های خبری
    categories: List[str] = field(default_factory=list)

    # میزان اعتبار منبع (۰ تا ۱۰۰)
    priority: int = 50

    # فاصله بررسی خبر (ثانیه)
    check_interval: int = 60

    # فعال یا غیرفعال بودن منبع
    enabled: bool = True
