"""
مدل منبع خبری

تمام منابع خبری پروژه KhabarF24 باید از این مدل استفاده کنند.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class NewsSource:
    """
    اطلاعات یک منبع خبری
    """

    # شناسه یکتا
    id: str

    # نام نمایشی
    name: str

    # نوع منبع
# rss / website / api / social
source_type: str

# آیا RSS دارد؟
has_rss: bool = False

# آیا از API استفاده می‌کند؟
has_api: bool = False

# آیا امکان Web Scraping دارد؟
supports_scraping: bool = False

# آیا برای دریافت اطلاعات نیاز به مرورگر دارد؟
requires_browser: bool = False

# آدرس منبع
url: str

# کشور
country: str

# پرچم کشور
flag: str

# زبان
language: str

# دسته‌های خبری
categories: List[str] = field(default_factory=list)

# میزان اعتبار منبع (0 تا 100)
priority: int = 50

# فاصله بررسی این منبع (بر حسب ثانیه)
check_interval: int = 60

# فعال یا غیرفعال بودن
enabled: bool = True
