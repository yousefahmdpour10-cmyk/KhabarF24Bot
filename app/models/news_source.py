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

    # فعال یا غیرفعال بودن
    enabled: bool = True
