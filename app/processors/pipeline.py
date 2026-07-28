"""
Processing Pipeline

اجرای تمام پردازش‌های خبر به ترتیب مشخص
"""

from typing import List

from app.models.raw_news import RawNews
from app.models.news import News
from app.utils.logger import logger


class ProcessingPipeline:
    """
    موتور پردازش خبر
    """

    def __init__(self):
        self.processors = []

    def register(self, processor):
        """
        ثبت یک Processor
        """

        self.processors.append(processor)

        logger.info(
            f"Registered processor: {processor.__class__.__name__}"
        )

    async def process(
        self,
        raw_news: RawNews,
    ) -> News | None:
        """
        پردازش یک خبر
        """

        data = raw_news

        for processor in self.processors:

            try:

                data = await processor.process(data)

                if data is None:

                    logger.warning(
                        f"News dropped by {processor.__class__.__name__}"
                    )

                    return None

            except Exception as e:

                logger.exception(e)

                return None

        return data

    async def process_many(
        self,
        news_list: List[RawNews],
    ) -> List[News]:
        """
        پردازش چند خبر
        """

        result = []

        for news in news_list:

            processed = await self.process(news)

            if processed:

                result.append(processed)

        logger.info(
            f"Processed {len(result)} news."
        )

        return result
