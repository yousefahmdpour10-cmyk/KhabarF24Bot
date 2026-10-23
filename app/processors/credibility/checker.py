"""
Credibility Checker
اعتبارسنجی منبع خبری KhabarF24
"""

from app.models.raw_news import RawNews
from app.utils.logger import logger

from .rules import MIN_CREDIBILITY_SCORE
from .source_reputation import (
    SOURCE_REPUTATION,
    DEFAULT_SOURCE_REPUTATION,
)


SOURCE_ALIASES = {
    "hengaw": (
        "hengaw",
        "hengaw news",
        "hengaw organization for human rights",
    ),
    "iran international": (
        "iran international",
        "iranintl",
        "iran intl",
    ),
    "varzesh3": (
        "varzesh3",
        "varzesh 3",
        "ورزش سه",
    ),
    "israel 14": (
        "israel 14",
        "channel 14",
        "now 14",
        "חדשות 14",
    ),
}


def normalize_source_name(name: str) -> str:
    """یکسان‌سازی نام منبع برای مقایسه."""

    return " ".join(
        str(name or "").casefold().replace("_", " ").split()
    )


def get_source_reputation(source_name: str) -> int:
    """پیداکردن امتیاز منبع با تطبیق دقیق و نام‌های جایگزین."""

    normalized = normalize_source_name(source_name)

    # تطبیق دقیق پس از یکسان‌سازی نام
    for name, score in SOURCE_REPUTATION.items():
        if normalize_source_name(name) == normalized:
            return score

    # تطبیق نام‌های جایگزین
    for canonical, aliases in SOURCE_ALIASES.items():
        if normalized in {
            normalize_source_name(alias) for alias in aliases
        }:
            for name, score in SOURCE_REPUTATION.items():
                if normalize_source_name(name) == canonical:
                    return score

    # تطبیق محدود برای نام‌های طولانی‌تر
    # از تطبیق زیررشته‌های بسیار کوتاه خودداری می‌کنیم.
    for name, score in SOURCE_REPUTATION.items():
        candidate = normalize_source_name(name)

        if len(candidate) >= 5 and (
            normalized.startswith(candidate + " ")
            or candidate.startswith(normalized + " ")
        ):
            return score

    return DEFAULT_SOURCE_REPUTATION


class CredibilityChecker:

    async def process(self, news: RawNews) -> RawNews:
        source = str(getattr(news, "source", "") or "Unknown")

        score = get_source_reputation(source)

        news.credibility_score = score
        news.is_verified = score >= MIN_CREDIBILITY_SCORE

        logger.info(
            "Credibility Check | source=%s | score=%s | "
            "minimum=%s | verified=%s",
            source,
            score,
            MIN_CREDIBILITY_SCORE,
            news.is_verified,
        )

        return news
