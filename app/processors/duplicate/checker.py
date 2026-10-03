"""
Duplicate Checker
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger

from .normalizer import NewsNormalizer
from .similarity import SimilarityEngine


class DuplicateChecker:

    def __init__(self):

        # بعداً این قسمت با دیتابیس جایگزین می‌شود
        self.cache = []

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        text = NewsNormalizer.normalize(
            f"{news.title} {news.summary}"
        )

        # این متن را برای مرحله‌ی بعد (mark_seen) نگه می‌داریم، ولی
        # هنوز به کش اضافه نمی‌کنیم -- چون هنوز معلوم نیست این خبر
        # واقعاً منتشر می‌شود یا در مراحل بعدی (مثلاً شکست AI) رد
        # می‌شود. اگر همین‌جا اضافه‌اش کنیم، خبری که فقط به‌خاطر
        # محدودیت موقت Gemini شکست خورده، برای همیشه "دیده‌شده"
        # علامت می‌خورد و دیگر هیچ‌وقت دوباره امتحان نمی‌شود.
        news._dedup_text = text

        news.is_duplicate = False
        news.duplicate_score = 0

        for old_text in self.cache:

            similarity = SimilarityEngine.compare(
                text,
                old_text,
            )

            if similarity >= 0.90:

                news.is_duplicate = True
                news.duplicate_score = similarity

                logger.info(
                    f"Duplicate ({similarity:.2f})"
                )

                return news

        logger.info("Unique News")

        return news

    def mark_seen(
        self,
        news: RawNews,
    ) -> None:
        """
        فقط بعد از انتشار موفق خبر صدا زده می‌شود -- تا خبری که
        هنوز واقعاً منتشر نشده (مثلاً به‌خاطر شکست AI)، بتواند در
        چرخه‌ی بعدی دوباره امتحان شود.
        """

        text = getattr(news, "_dedup_text", None)

        if text and text not in self.cache:
            self.cache.append(text)
