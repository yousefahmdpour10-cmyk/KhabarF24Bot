"""
Similarity Engine

مقایسه‌ی دو متن برای تشخیص خبرهای تکراری.
"""

from difflib import SequenceMatcher


class SimilarityEngine:

    @staticmethod
    def compare(
        text1: str,
        text2: str,
    ) -> float:

        if not text1 or not text2:
            return 0.0

        if text1 == text2:
            return 1.0

        return SequenceMatcher(
            None,
            str(text1),
            str(text2),
        ).ratio()
