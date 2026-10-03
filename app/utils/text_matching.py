"""
Text Matching Utilities

تطبیق کلیدواژه‌ی «مرزدار» (word-boundary) به‌جای substring ساده.
دلیل وجود این فایل: substring ساده باعث تطبیق‌های اشتباه می‌شد، مثل:
  - "گل" (goal) داخل "گل‌آرایی" (flower decoration)
  - "AI" داخل "again", "said", "maintain"
  - "App" داخل "approach", "appeal", "happen"
"""

import re

_CACHE: dict[str, re.Pattern] = {}


def keyword_in_text(keyword: str, text: str) -> bool:
    """
    بررسی می‌کند که آیا `keyword` به‌عنوان یک کلمه‌ی مستقل
    (نه به‌عنوان بخشی از یک کلمه‌ی بزرگ‌تر) در `text` وجود دارد.
    """

    if not keyword or not text:
        return False

    pattern = _CACHE.get(keyword)

    if pattern is None:
        escaped = re.escape(keyword)
        pattern = re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE | re.UNICODE)
        _CACHE[keyword] = pattern

    return pattern.search(text) is not None
