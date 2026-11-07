"""
Duplicate Checker

تشخیص خبر تکراری، با حافظه‌ی ماندگار بین اجراها.

ویژگی‌ها:
- جلوگیری از انتشار دوباره‌ی همان URL
- جلوگیری از تکرار بر اساس source_id + news id
- جلوگیری از تکرار بر اساس hash محتوا
- تشخیص تشابه متنی خبر
- تشخیص تشابه تیتر خبرهای منتشرشده از منابع مختلف
- حفظ حافظه بین اجراهای GitHub Actions
- سازگاری با seen_news.json فعلی
"""

import hashlib
import json
import os
import re
import tempfile
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Optional

from app.models.raw_news import RawNews
from app.utils.logger import logger

from .normalizer import NewsNormalizer
from .similarity import SimilarityEngine


STATE_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "state"
    / "seen_news.json"
)

# سقف حافظه‌ی متن‌ها
MAX_TEXTS = 5000

# سقف تیترهای ذخیره‌شده
MAX_HEADLINES = 1000

# سقف URLها
MAX_URLS = 10000

# سقف شناسه‌های خبر
MAX_NEWS_IDS = 10000

# سقف hashهای محتوا
MAX_CONTENT_HASHES = 10000

# تشابه متن اصلی خبر
TEXT_THRESHOLD = 0.90

# پیش‌فیلتر سریع متن
PREFILTER_JACCARD = 0.40

# تشابه تیتر
HEADLINE_JACCARD = 0.65
HEADLINE_RATIO = 0.78
MIN_HEADLINE_CHARS = 12


_DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


def _words(text: str) -> frozenset:
    return frozenset(
        str(text or "").split()
    )


def _normalize_headline(text: str) -> str:
    text = str(text or "").translate(_DIGITS)

    text = (
        text
        .replace("ي", "ی")
        .replace("ك", "ک")
        .replace("\u200c", "")
        .lower()
    )

    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
    )

    return " ".join(text.split())


def _normalize_url(url: str) -> str:
    """
    نرمال‌سازی URL برای جلوگیری از تکرارهای ساده
    به دلیل تفاوت جزئی در query string یا slash انتهایی.
    """

    url = str(url or "").strip()

    if not url:
        return ""

    url = url.rstrip("/")

    return url.casefold()


def _normalize_news_id(
    source_id: str,
    news_id: str,
) -> str:
    """
    ساخت شناسه‌ی یکتا برای خبر بر اساس منبع و id خبر.
    """

    source_id = str(source_id or "").strip()
    news_id = str(news_id or "").strip()

    if not news_id:
        return ""

    if source_id:
        return (
            f"{source_id.casefold()}::{news_id.casefold()}"
        )

    return news_id.casefold()


def _content_hash(text: str) -> str:
    """
    Hash پایدار از محتوای نرمال‌شده‌ی خبر.
    """

    normalized = NewsNormalizer.normalize(
        str(text or "")
    )

    if not normalized:
        return ""

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


class DuplicateChecker:

    def __init__(self):

        # متن‌های نرمال‌شده‌ی خبرهای منتشرشده
        self.cache = []

        # wordset متن‌ها برای prefilter سریع
        self._wordsets = []

        # مجموعه‌ی سریع برای exact text
        self._seen = set()

        # تیترهای فارسی پست‌های منتشرشده
        self.headlines = []

        # URLهای خبرهای منتشرشده
        self.urls = []

        # شناسه‌های یکتای خبر
        self.news_ids = []

        # hash محتوای خبر
        self.content_hashes = []

        self._url_set = set()
        self._news_id_set = set()
        self._content_hash_set = set()

        self._load()

    # ------------------------------------------------------------------
    # حافظه‌ی ماندگار
    # ------------------------------------------------------------------

    def _load(self) -> None:
        try:
            data = json.loads(
                STATE_PATH.read_text(
                    encoding="utf-8"
                )
            )

        except FileNotFoundError:
            logger.info(
                "DuplicateChecker: حافظه‌ی قبلی وجود ندارد"
            )
            return

        except Exception as exc:
            logger.warning(
                "DuplicateChecker: خواندن حافظه ناموفق بود "
                f"({exc})"
            )
            return

        if not isinstance(data, dict):
            logger.warning(
                "DuplicateChecker: ساختار حافظه نامعتبر است"
            )
            return

        # --------------------------------------------------------------
        # حافظه‌ی قدیمی
        # --------------------------------------------------------------

        texts = [
            value
            for value in data.get("texts", [])
            if isinstance(value, str)
        ]

        headlines = [
            value
            for value in data.get("headlines", [])
            if isinstance(value, str)
        ]

        # --------------------------------------------------------------
        # حافظه‌ی جدید
        # --------------------------------------------------------------

        urls = [
            value
            for value in data.get("urls", [])
            if isinstance(value, str)
        ]

        news_ids = [
            value
            for value in data.get("news_ids", [])
            if isinstance(value, str)
        ]

        content_hashes = [
            value
            for value in data.get("content_hashes", [])
            if isinstance(value, str)
        ]

        # --------------------------------------------------------------
        # بارگذاری متن‌ها
        # --------------------------------------------------------------

        for text in texts[-MAX_TEXTS:]:
            self._add_text(
                text,
                save=False,
            )

        # --------------------------------------------------------------
        # بارگذاری تیترها
        # --------------------------------------------------------------

        self.headlines = (
            headlines[-MAX_HEADLINES:]
        )

        # --------------------------------------------------------------
        # بارگذاری URLها
        # --------------------------------------------------------------

        for url in urls[-MAX_URLS:]:

            normalized = _normalize_url(url)

            if normalized and normalized not in self._url_set:
                self.urls.append(normalized)
                self._url_set.add(normalized)

        # --------------------------------------------------------------
        # بارگذاری شناسه‌ها
        # --------------------------------------------------------------

        for news_id in news_ids[-MAX_NEWS_IDS:]:

            normalized = str(
                news_id or ""
            ).strip().casefold()

            if (
                normalized
                and normalized not in self._news_id_set
            ):
                self.news_ids.append(normalized)
                self._news_id_set.add(normalized)

        # --------------------------------------------------------------
        # بارگذاری hashها
        # --------------------------------------------------------------

        for content_hash in content_hashes[
            -MAX_CONTENT_HASHES:
        ]:

            value = str(
                content_hash or ""
            ).strip()

            if (
                value
                and value not in self._content_hash_set
            ):
                self.content_hashes.append(value)
                self._content_hash_set.add(value)

        logger.info(
            "DuplicateChecker: "
            f"{len(self.cache)} خبر، "
            f"{len(self.headlines)} تیتر، "
            f"{len(self.urls)} URL، "
            f"{len(self.news_ids)} شناسه و "
            f"{len(self.content_hashes)} hash "
            "از اجراهای قبلی بارگذاری شد"
        )

    def _save(self) -> None:

        try:

            STATE_PATH.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            payload = json.dumps(
                {
                    "version": 2,

                    "texts": self.cache[
                        -MAX_TEXTS:
                    ],

                    "headlines": self.headlines[
                        -MAX_HEADLINES:
                    ],

                    "urls": self.urls[
                        -MAX_URLS:
                    ],

                    "news_ids": self.news_ids[
                        -MAX_NEWS_IDS:
                    ],

                    "content_hashes": (
                        self.content_hashes[
                            -MAX_CONTENT_HASHES:
                        ]
                    ),
                },

                ensure_ascii=False,
            )

            # نوشتن اتمی
            fd, tmp_path = tempfile.mkstemp(
                dir=str(STATE_PATH.parent),
                prefix=".seen_",
                suffix=".tmp",
            )

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as tmp:

                tmp.write(payload)

            os.replace(
                tmp_path,
                STATE_PATH,
            )

        except Exception as exc:

            logger.warning(
                "DuplicateChecker: ذخیره‌ی حافظه "
                f"ناموفق بود ({exc})"
            )

    # ------------------------------------------------------------------
    # ثبت متن
    # ------------------------------------------------------------------

    def _add_text(
        self,
        text: Optional[str],
        save: bool = False,
    ) -> bool:

        if not text:
            return False

        if text in self._seen:
            return False

        self.cache.append(text)

        self._wordsets.append(
            _words(text)
        )

        self._seen.add(text)

        if len(self.cache) > MAX_TEXTS:

            oldest = self.cache.pop(0)

            self._wordsets.pop(0)

            self._seen.discard(
                oldest
            )

        if save:
            self._save()

        return True

    # ------------------------------------------------------------------
    # ثبت URL
    # ------------------------------------------------------------------

    def _add_url(
        self,
        url: str,
    ) -> bool:

        normalized = _normalize_url(url)

        if not normalized:
            return False

        if normalized in self._url_set:
            return False

        self.urls.append(
            normalized
        )

        self._url_set.add(
            normalized
        )

        if len(self.urls) > MAX_URLS:

            oldest = self.urls.pop(0)

            self._url_set.discard(
                oldest
            )

        return True

    # ------------------------------------------------------------------
    # ثبت شناسه خبر
    # ------------------------------------------------------------------

    def _add_news_id(
        self,
        source_id: str,
        news_id: str,
    ) -> bool:

        normalized = _normalize_news_id(
            source_id,
            news_id,
        )

        if not normalized:
            return False

        if normalized in self._news_id_set:
            return False

        self.news_ids.append(
            normalized
        )

        self._news_id_set.add(
            normalized
        )

        if len(self.news_ids) > MAX_NEWS_IDS:

            oldest = self.news_ids.pop(0)

            self._news_id_set.discard(
                oldest
            )

        return True

    # ------------------------------------------------------------------
    # ثبت hash محتوا
    # ------------------------------------------------------------------

    def _add_content_hash(
        self,
        content_hash: str,
    ) -> bool:

        value = str(
            content_hash or ""
        ).strip()

        if not value:
            return False

        if value in self._content_hash_set:
            return False

        self.content_hashes.append(
            value
        )

        self._content_hash_set.add(
            value
        )

        if (
            len(self.content_hashes)
            > MAX_CONTENT_HASHES
        ):

            oldest = self.content_hashes.pop(0)

            self._content_hash_set.discard(
                oldest
            )

        return True

    # ------------------------------------------------------------------
    # اطلاعات شناسایی خبر
    # ------------------------------------------------------------------

    @staticmethod
    def _get_news_identity(
        news: RawNews,
    ) -> Dict[str, str]:

        source_id = str(
            getattr(
                news,
                "source_id",
                ""
            )
            or ""
        ).strip()

        news_id = str(
            getattr(
                news,
                "id",
                ""
            )
            or ""
        ).strip()

        url = _normalize_url(
            getattr(
                news,
                "url",
                ""
            )
        )

        content = NewsNormalizer.normalize(
            f"{getattr(news, 'title', '')} "
            f"{getattr(news, 'summary', '')} "
            f"{getattr(news, 'content', '')}"
        )

        content_hash = _content_hash(
            content
        )

        return {
            "source_id": source_id,
            "news_id": news_id,
            "url": url,
            "content_hash": content_hash,
        }

    # ------------------------------------------------------------------
    # تشخیص
    # ------------------------------------------------------------------

    async def process(
        self,
        news: RawNews,
    ) -> RawNews:

        identity = self._get_news_identity(
            news
        )

        # اطلاعات شناسایی را برای mark_seen نگه می‌داریم
        news._dedup_text = NewsNormalizer.normalize(
            f"{news.title} {news.summary}"
        )

        news._dedup_url = identity[
            "url"
        ]

        news._dedup_news_id = _normalize_news_id(
            identity["source_id"],
            identity["news_id"],
        )

        news._dedup_content_hash = identity[
            "content_hash"
        ]

        news.is_duplicate = False
        news.duplicate_score = 0

        # --------------------------------------------------------------
        # 1. بررسی URL
        # --------------------------------------------------------------

        if (
            identity["url"]
            and identity["url"] in self._url_set
        ):

            news.is_duplicate = True
            news.duplicate_score = 1.0

            logger.info(
                "Duplicate (URL already published) | "
                f"url={identity['url']}"
            )

            return news

        # --------------------------------------------------------------
        # 2. بررسی source_id + news id
        # --------------------------------------------------------------

        if (
            news._dedup_news_id
            and news._dedup_news_id
            in self._news_id_set
        ):

            news.is_duplicate = True
            news.duplicate_score = 1.0

            logger.info(
                "Duplicate "
                "(source_id + news id already published) | "
                f"id={news._dedup_news_id}"
            )

            return news

        # --------------------------------------------------------------
        # 3. بررسی hash محتوای کامل
        # --------------------------------------------------------------

        if (
            identity["content_hash"]
            and identity["content_hash"]
            in self._content_hash_set
        ):

            news.is_duplicate = True
            news.duplicate_score = 1.0

            logger.info(
                "Duplicate "
                "(content hash already published)"
            )

            return news

        # --------------------------------------------------------------
        # 4. بررسی exact text
        # --------------------------------------------------------------

        text = news._dedup_text

        if text and text in self._seen:

            news.is_duplicate = True
            news.duplicate_score = 1.0

            logger.info(
                "Duplicate (exact normalized text)"
            )

            return news

        # --------------------------------------------------------------
        # 5. بررسی تشابه متن
        # --------------------------------------------------------------

        words = _words(text)

        for old_text, old_words in zip(
            self.cache,
            self._wordsets,
        ):

            if words and old_words:

                union = len(
                    words | old_words
                )

                if (
                    union
                    and (
                        len(words & old_words)
                        / union
                    )
                    < PREFILTER_JACCARD
                ):
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

        logger.info(
            "Unique News"
        )

        return news

    # ------------------------------------------------------------------
    # تشخیص تکرار داستان بعد از Gemini
    # ------------------------------------------------------------------

    def is_story_repeat(
        self,
        news: RawNews,
    ) -> bool:

        """
        بعد از Gemini:

        آیا این خبر همان داستانی است که قبلاً
        از منبع دیگری منتشر شده؟

        خبر یکسان از چند رسانه ممکن است
        متن اصلی متفاوت داشته باشد،
        ولی تیتر فارسی نهایی مشابه باشد.
        """

        headline = _normalize_headline(
            getattr(
                news,
                "title",
                ""
            )
        )

        if len(headline) < MIN_HEADLINE_CHARS:
            return False

        words = set(
            headline.split()
        )

        for old in self.headlines:

            old_words = set(
                old.split()
            )

            union = len(
                words | old_words
            )

            if not union:
                continue

            jaccard = (
                len(words & old_words)
                / union
            )

            if jaccard >= HEADLINE_JACCARD:

                logger.info(
                    "Same story as a recent post "
                    f"(words {jaccard:.2f})"
                )

                return True

            if (
                jaccard >= 0.3
                and SequenceMatcher(
                    None,
                    headline,
                    old,
                ).ratio()
                >= HEADLINE_RATIO
            ):

                logger.info(
                    "Same story as a recent post "
                    "(similar headline)"
                )

                return True

        return False

    # ------------------------------------------------------------------
    # ثبت خبر منتشرشده
    # ------------------------------------------------------------------

    def mark_seen(
        self,
        news: RawNews,
    ) -> None:

        """
        فقط بعد از انتشار موفق خبر صدا زده می‌شود.

        بنابراین خبری که به دلیل شکست موقت Gemini
        منتشر نشده، در حافظه ثبت نمی‌شود.
        """

        changed = False

        # --------------------------------------------------------------
        # متن
        # --------------------------------------------------------------

        if self._add_text(
            getattr(
                news,
                "_dedup_text",
                None,
            ),
            save=False,
        ):
            changed = True

        # --------------------------------------------------------------
        # URL
        # --------------------------------------------------------------

        if self._add_url(
            getattr(
                news,
                "_dedup_url",
                "",
            )
        ):
            changed = True

        # --------------------------------------------------------------
        # source_id + news id
        # --------------------------------------------------------------

        dedup_news_id = getattr(
            news,
            "_dedup_news_id",
            "",
        )

        if dedup_news_id:

            # چون _dedup_news_id از قبل ترکیبی است،
            # مستقیماً ثبت می‌کنیم.
            if (
                dedup_news_id
                not in self._news_id_set
            ):

                self.news_ids.append(
                    dedup_news_id
                )

                self._news_id_set.add(
                    dedup_news_id
                )

                if (
                    len(self.news_ids)
                    > MAX_NEWS_IDS
                ):

                    oldest = self.news_ids.pop(0)

                    self._news_id_set.discard(
                        oldest
                    )

                changed = True

        # --------------------------------------------------------------
        # content hash
        # --------------------------------------------------------------

        if self._add_content_hash(
            getattr(
                news,
                "_dedup_content_hash",
                "",
            )
        ):
            changed = True

        # --------------------------------------------------------------
        # تیتر فارسی
        # --------------------------------------------------------------

        if getattr(
            news,
            "content_generated",
            False,
        ):

            headline = _normalize_headline(
                getattr(
                    news,
                    "title",
                    "",
                )
            )

            if (
                len(headline)
                >= MIN_HEADLINE_CHARS
                and headline
                not in self.headlines
            ):

                self.headlines.append(
                    headline
                )

                self.headlines = (
                    self.headlines[
                        -MAX_HEADLINES:
                    ]
                )

                changed = True

        # --------------------------------------------------------------
        # ذخیره‌ی دائمی
        # --------------------------------------------------------------

        if changed:
            self._save()
