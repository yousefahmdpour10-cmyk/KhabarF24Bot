"""
News Normalizer
"""

import re


class NewsNormalizer:

    @staticmethod
    def normalize(text: str) -> str:

        if not text:
            return ""

        text = text.lower()

        # حذف فاصله‌های اضافی
        text = re.sub(r"\s+", " ", text)

        # حذف علائم نگارشی
        text = re.sub(r"[^\w\s]", "", text)

        return text.strip()
