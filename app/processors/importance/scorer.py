"""
Importance Scorer
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger
from app.utils.text_matching import keyword_in_text

from .category_scores import CATEGORY_SCORES
from .keywords import KEYWORD_SCORES
from .source_scores import SOURCE_SCORES

# اگر امتیاز اهمیت به این حد یا بیشتر برسد، خبر "فوری" علامت‌گذاری
# می‌شود (هشتگ #خبرفوری). این آستانه عمداً بالاست تا فقط خبرهای
# واقعاً بزرگ (جنگ، فاجعه‌ی طبیعی و مانند آن) را بگیرد، نه اخبار
# روزمره‌ی سیاسی/ورزشی که فقط به‌خاطر منبع معتبر امتیاز پایه می‌گیرند.
BREAKING_THRESHOLD = 25


class ImportanceScorer:

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        score = 0

        text = f"{news.title} {news.summary}"

        for keyword, value in KEYWORD_SCORES.items():
            if keyword_in_text(keyword, text):
                score += value

        score += CATEGORY_SCORES.get(
            news.category,
            0,
        )

        score += SOURCE_SCORES.get(
            news.source,
            0,
        )

        news.importance_score = score
        news.is_breaking = score >= BREAKING_THRESHOLD

        logger.info(
            f"Importance Score: {score}"
            + (" [BREAKING]" if news.is_breaking else "")
        )

        return news
