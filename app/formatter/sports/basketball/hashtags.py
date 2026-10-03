"""
Basketball Hashtag Builder
KhabarF24

ساخت هشتگ‌های هوشمند برای اخبار بسکتبال.

مسئولیت این فایل:
    Sport + League + Tournament + Team + Player
    -> Hashtags

این فایل نباید متن اصلی خبر را فرمت کند.
"""

import re
from typing import Iterable, List, Optional


# ============================================================
# CONSTANTS
# ============================================================

SPORT_HASHTAG = "#بسکتبال"

MAX_HASHTAGS = 6


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(
    text: str,
) -> str:
    """
    نرمال‌سازی متن برای ساخت هشتگ.
    """

    if not text:
        return ""

    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "‌": "",
        " ": "",
        "-": "",
        "_": "",
        ".": "",
        ",": "",
        ":": "",
        "/": "",
        "\\": "",
        "(": "",
        ")": "",
        "[": "",
        "]": "",
        "{": "",
        "}": "",
        "!": "",
        "?": "",
        "،": "",
        "؛": "",
        "«": "",
        "»": "",
        "'": "",
        '"': "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


# ============================================================
# HASH NORMALIZATION
# ============================================================

def normalize_hashtag(
    value: str,
) -> Optional[str]:
    """
    تبدیل یک مقدار به هشتگ معتبر.
    """

    if not value:
        return None

    value = value.strip()

    if not value:
        return None

    # اگر قبلاً # داشت حذف می‌کنیم.
    value = value.lstrip("#")

    value = normalize_text(value)

    if not value:
        return None

    # حذف کاراکترهای غیرمجاز.
    value = re.sub(
        r"[^\w\u0600-\u06FF]",
        "",
        value,
        flags=re.UNICODE,
    )

    if not value:
        return None

    return f"#{value}"


# ============================================================
# ADD HASHTAG
# ============================================================

def add_hashtag(
    hashtags: List[str],
    value: Optional[str],
) -> None:
    """
    افزودن هشتگ بدون تکرار.
    """

    if not value:
        return

    hashtag = normalize_hashtag(value)

    if not hashtag:
        return

    if hashtag not in hashtags:
        hashtags.append(hashtag)


# ============================================================
# ITERABLE SUPPORT
# ============================================================

def add_many(
    hashtags: List[str],
    values: Optional[Iterable[str]],
) -> None:
    """
    افزودن چند مقدار به فهرست هشتگ‌ها.
    """

    if not values:
        return

    for value in values:
        add_hashtag(
            hashtags,
            value,
        )


# ============================================================
# MAIN BUILDER
# ============================================================

def build_hashtags(
    league: Optional[str] = None,
    tournament: Optional[str] = None,
    teams: Optional[Iterable[str]] = None,
    players: Optional[Iterable[str]] = None,
    max_hashtags: int = MAX_HASHTAGS,
) -> List[str]:
    """
    ساخت هشتگ‌های هوشمند بسکتبال.

    ترتیب اولویت:

        1. بسکتبال
        2. لیگ
        3. تورنمنت
        4. تیم‌ها
        5. بازیکنان

    خروجی بدون تکرار است.
    """

    hashtags: List[str] = []

    # --------------------------------------------------------
    # SPORT
    # --------------------------------------------------------

    add_hashtag(
        hashtags,
        SPORT_HASHTAG,
    )

    # --------------------------------------------------------
    # LEAGUE
    # --------------------------------------------------------

    add_hashtag(
        hashtags,
        league,
    )

    # --------------------------------------------------------
    # TOURNAMENT
    # --------------------------------------------------------

    add_hashtag(
        hashtags,
        tournament,
    )

    # --------------------------------------------------------
    # TEAMS
    # --------------------------------------------------------

    add_many(
        hashtags,
        teams,
    )

    # --------------------------------------------------------
    # PLAYERS
    # --------------------------------------------------------

    add_many(
        hashtags,
        players,
    )

    # --------------------------------------------------------
    # LIMIT
    # --------------------------------------------------------

    if max_hashtags <= 0:
        return []

    return hashtags[:max_hashtags]


# ============================================================
# BUILD FROM DETECTED DATA
# ============================================================

def build_hashtags_from_data(
    data: dict,
    max_hashtags: int = MAX_HASHTAGS,
) -> List[str]:
    """
    ساخت هشتگ از یک دیکشنری داده.

    کلیدهای قابل قبول:

        league
        tournament
        teams
        players
    """

    if not isinstance(data, dict):
        return [SPORT_HASHTAG]

    return build_hashtags(
        league=data.get("league"),
        tournament=data.get("tournament"),
        teams=data.get("teams"),
        players=data.get("players"),
        max_hashtags=max_hashtags,
    )


# ============================================================
# FORMAT HASHTAGS
# ============================================================

def format_hashtags(
    hashtags: Iterable[str],
) -> str:
    """
    تبدیل لیست هشتگ‌ها به یک خط مناسب پست تلگرام.
    """

    if not hashtags:
        return SPORT_HASHTAG

    unique: List[str] = []

    for hashtag in hashtags:

        normalized = normalize_hashtag(
            hashtag
        )

        if normalized and normalized not in unique:
            unique.append(normalized)

    if not unique:
        return SPORT_HASHTAG

    return " ".join(unique)


# ============================================================
# DEFAULT BASKETBALL HASHTAGS
# ============================================================

def get_default_hashtags() -> List[str]:
    """
    هشتگ پیش‌فرض خبر بسکتبال.
    """

    return [
        SPORT_HASHTAG
  ]
