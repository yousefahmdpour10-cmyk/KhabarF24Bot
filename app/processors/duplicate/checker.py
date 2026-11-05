"""
Duplicate Checker

تشخیص خبر تکراری، با حافظه‌ی ماندگار بین اجراها.

قبلاً حافظه فقط در RAM بود و با هر ری‌استارت ربات (هر ~۶ ساعت)
خالی می‌شد؛ پس هر خبری که هنوز در RSS مانده بود دوباره منتشر می‌شد.
حالا خبرهای دیده‌شده در data/state/seen_news.json ذخیره می‌شوند
(در GitHub Actions با cache بین اجراها منتقل می‌شود، bot.yml را ببین).
"""

import json
import os
import re
import tempfile
from difflib import SequenceMatcher
from pathlib import Path

from app.models.raw_news import RawNews
from app.utils.logger import logger

from .normalizer import NewsNormalizer
from .similarity import SimilarityEngine


STATE_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "state" / "seen_news.json"
)

# سقف حافظه (قدیمی‌ترین‌ها حذف می‌شوند)
MAX_TEXTS = 3000
MAX_HEADLINES = 400

# تشابه متن اصلی خبر (قبل از Gemini)
TEXT_THRESHOLD = 0.90

# مقایسه‌ی کامل فقط با متن‌هایی که حداقل این‌قدر کلمه‌ی مشترک دارند.
# متنی که ≥۰.۹ مشابه است حتماً کلمه‌های مشترک زیادی دارد، پس چیزی از
# دست نمی‌رود، ولی با هزاران خبر ذخیره‌شده هر مقایسه میلی‌ثانیه‌ای می‌ماند.
PREFILTER_JACCARD = 0.4

# «همان خبر از منبع دیگر»: تیتر فارسیِ تولیدشده با تیتر پست‌های اخیر
HEADLINE_JACCARD = 0.65
HEADLINE_RATIO = 0.78
MIN_HEADLINE_CHARS = 12

_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def _words(text: str) -> frozenset:
    return frozenset(str(text or "").split())


def _normalize_headline(text: str) -> str:
    text = str(text or "").translate(_DIGITS)
    text = (
        text.replace("ي", "ی")
        .replace("ك", "ک")
        .replace("\u200c", "")
        .lower()
    )
    text = re.sub(r"[^\w\s]", " ", text)

    return " ".join(text.split())


class DuplicateChecker:

    def __init__(self):

        # متن‌های نرمال‌شده‌ی خبرهای منتشرشده (به ترتیب انتشار)
        self.cache = []
        self._wordsets = []
        self._seen = set()

        # تیتر فارسی پست‌های اخیر
        self.headlines = []

        self._load()

    # ------------------------------------------------------------------
    # حافظه‌ی ماندگار
    # ------------------------------------------------------------------

    def _load(self) -> None:
        try:
            data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return
        except Exception as exc:
            logger.warning(f"DuplicateChecker: خواندن حافظه ناموفق بود ({exc})")
            return

        if not isinstance(data, dict):
            return

        texts = [t for t in data.get("texts", []) if isinstance(t, str)]
        headlines = [h for h in data.get("headlines", []) if isinstance(h, str)]

        for text in texts[-MAX_TEXTS:]:
            self._add_text(text)

        self.headlines = headlines[-MAX_HEADLINES:]

        logger.info(
            f"DuplicateChecker: {len(self.cache)} خبر و "
            f"{len(self.headlines)} تیتر از اجراهای قبلی بارگذاری شد"
        )

    def _save(self) -> None:
        try:
            STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

            payload = json.dumps(
                {
                    "version": 1,
                    "texts": self.cache[-MAX_TEXTS:],
                    "headlines": self.headlines[-MAX_HEADLINES:],
                },
                ensure_ascii=False,
            )

            # نوشتن اتمی: وسط نوشتن قطع شد، فایل قبلی سالم می‌ماند
            fd, tmp_path = tempfile.mkstemp(
                dir=str(STATE_PATH.parent),
                prefix=".seen_",
                suffix=".tmp",
            )

            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                tmp.write(payload)

            os.replace(tmp_path, STATE_PATH)

        except Exception as exc:
            logger.warning(f"DuplicateChecker: ذخیره‌ی حافظه ناموفق بود ({exc})")

    def _add_text(self, text: str) -> bool:
        if not text or text in self._seen:
            return False

        self.cache.append(text)
        self._wordsets.append(_words(text))
        self._seen.add(text)

        if len(self.cache) > MAX_TEXTS:
            oldest = self.cache.pop(0)
            self._wordsets.pop(0)
            self._seen.discard(oldest)

        return True

    # ------------------------------------------------------------------
    # تشخیص
    # ------------------------------------------------------------------

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

        if text in self._seen:
            news.is_duplicate = True
            news.duplicate_score = 1.0
            logger.info("Duplicate (1.00)")
            return news

        words = _words(text)

        for old_text, old_words in zip(self.cache, self._wordsets):

            if words and old_words:
                union = len(words | old_words)

                if union and len(words & old_words) / union < PREFILTER_JACCARD:
                    continue

            similarity = SimilarityEngine.compare(
                text,
                old_text,
            )

            if similarity >= TEXT_THRESHOLD:

                news.is_duplicate = True
                news.duplicate_score = similarity

                logger.info(
                    f"Duplicate ({similarity:.2f})"
                )

                return news

        logger.info("Unique News")

        return news

    def is_story_repeat(
        self,
        news: RawNews,
    ) -> bool:
        """
        بعد از Gemini: آیا همین خبر (با تیتر فارسیِ تقریباً یکسان) قبلاً
        از منبع دیگری منتشر شده؟ خبر یکسان از چند رسانه متن اصلی متفاوت
        دارد ولی تیتر فارسی‌اش شبیه است.
        """

        headline = _normalize_headline(getattr(news, "title", ""))

        if len(headline) < MIN_HEADLINE_CHARS:
            return False

        words = set(headline.split())

        for old in self.headlines:
            old_words = set(old.split())
            union = len(words | old_words)

            if not union:
                continue

            jaccard = len(words & old_words) / union

            if jaccard >= HEADLINE_JACCARD:
                logger.info(f"Same story as a recent post (words {jaccard:.2f})")
                return True

            if jaccard >= 0.3 and (
                SequenceMatcher(None, headline, old).ratio() >= HEADLINE_RATIO
            ):
                logger.info("Same story as a recent post (similar headline)")
                return True

        return False

    def mark_seen(
        self,
        news: RawNews,
    ) -> None:
        """
        فقط بعد از انتشار موفق خبر (یا وقتی خبر برای همیشه رد می‌شود)
        صدا زده می‌شود -- تا خبری که هنوز واقعاً منتشر نشده (مثلاً
        به‌خاطر شکست AI)، بتواند در چرخه‌ی بعدی دوباره امتحان شود.
        """

        changed = self._add_text(getattr(news, "_dedup_text", None))

        # تیتر فارسی فقط برای خبری که واقعاً ترجمه شده نگه داشته می‌شود
        if getattr(news, "content_generated", False):
            headline = _normalize_headline(getattr(news, "title", ""))

            if len(headline) >= MIN_HEADLINE_CHARS and headline not in self.headlines:
                self.headlines.append(headline)
                self.headlines = self.headlines[-MAX_HEADLINES:]
                changed = True

        if changed:
            self._save()
