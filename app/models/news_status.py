"""
وضعیت‌های پردازش خبر
"""

from enum import Enum


class NewsStatus(str, Enum):
    """
    وضعیت‌های مختلف یک خبر در موتور KhabarF24
    """

    # تازه دریافت شده
    RAW = "raw"

    # اعتبار اولیه بررسی شده
    VALIDATED = "validated"

    # خبر تکراری نیست
    DEDUPLICATED = "deduplicated"

    # زبان تشخیص داده شده
    LANGUAGE_DETECTED = "language_detected"

    # ترجمه شده
    TRANSLATED = "translated"

    # خلاصه شده
    SUMMARIZED = "summarized"

    # دسته‌بندی شده
    CATEGORIZED = "categorized"

    # زیرشاخه مشخص شده
    SUBCATEGORIZED = "subcategorized"

    # امتیاز اهمیت دریافت کرده
    SCORED = "scored"

    # آماده انتشار
    READY = "ready"

    # منتشر شده
    PUBLISHED = "published"

    # رد شده
    REJECTED = "rejected"

    # خطا
    ERROR = "error"
