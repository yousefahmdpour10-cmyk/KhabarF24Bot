"""
Category Detector
تشخیص دسته‌بندی خبر
"""

from collections import defaultdict

from app.models.raw_news import RawNews
from app.processors.category.keywords import CATEGORY_KEYWORDS
from app.utils.logger import logger

# حداقل امتیاز لازم برای اینکه به یک دسته اعتماد کنیم.
# اگر بهترین دسته فقط با یک کلیدواژه‌ی ضعیف/عمومی انتخاب شده باشد
# (مثلاً فقط یک بار "دولت" در کل متن آمده)، آن را نمی‌پذیریم و
# به‌جایش خبر را "general" در نظر می‌گیریم (که در فرمتر پیش‌فرض
# WorldTemplate را می‌گیرد) تا دسته‌بندی و هشتگ اشتباه نخورد.
MIN_CATEGORY_SCORE = 2


class CategoryDetector:
    """
    تشخیص دسته خبر
    """

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        text = f"{news.title} {news.summary}".lower()

        scores = defaultdict(int)

        for category, keywords in CATEGORY_KEYWORDS.items():

            for keyword in keywords:

                if keyword.lower() in text:
                    scores[category] += 1

        if scores:

            best_category = max(
                scores,
                key=scores.get,
            )

            best_score = scores[best_category]

            if best_score >= MIN_CATEGORY_SCORE:

                news.category = best_category

                logger.info(
                    f"Category: {best_category} (score={best_score})"
                )

            else:

                news.category = "general"

                logger.info(
                    f"Category: general (best guess '{best_category}' too weak, score={best_score})"
                )

        else:

            news.category = "general"
            logger.info(
                "Category: general"
            )

        return news
