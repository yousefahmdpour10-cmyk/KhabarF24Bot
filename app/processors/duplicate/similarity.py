"""
Similarity Engine
"""

from difflib import SequenceMatcher


class SimilarityEngine:

    @staticmethod
    def compare(
        text1: str,
        text2: str,
    ) -> float:

        return SequenceMatcher(
            None,
            text1,
            text2,
        ).ratio()
