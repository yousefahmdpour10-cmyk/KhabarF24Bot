"""
News Normalizer

نرمال‌سازی متن برای تشخیص تکراری بودن خبر.
"""

import re


class NewsNormalizer:

    @staticmethod
    def normalize(text: str) -> str:

        if not text:
            return ""

        text = str(text).lower()

        # یکسان‌سازی حروف عربی و فارسی
        text = (
            text
            .replace("ي", "ی")
            .replace("ك", "ک")
            .replace("\u200c", "")
        )

        # یکسان‌سازی اعداد فارسی و عربی
        text = text.translate(
            str.maketrans(
                "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
                "01234567890123456789",
            )
        )

        # حذف فاصله‌های اضافی
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        # حذف علائم نگارشی
        text = re.sub(
            r"[^\w\s]",
            "",
            text,
        )

        return text.strip()
