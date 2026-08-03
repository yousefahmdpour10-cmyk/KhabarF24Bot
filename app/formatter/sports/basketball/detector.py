"""
Basketball Detector
KhabarF24

تشخیص اطلاعات ورزشی موجود در خبر بسکتبال.

مسئولیت:
    - تشخیص تیم‌ها
    - تشخیص بازیکنان
    - تشخیص لیگ
    - تشخیص تورنمنت
    - تشخیص نوع رویداد خبر
    - تشخیص نتیجه در صورت وجود

این فایل متن خبر را فرمت نمی‌کند.
فقط داده ساختاریافته برای Formatter تولید می‌کند.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .teams import find_teams_in_text
from .players import find_players_in_text
from .leagues import find_league_in_text
from .tournament import find_tournament_in_text


# ============================================================
# EVENT TYPES
# ============================================================

EVENT_UNKNOWN = "unknown"

EVENT_MATCH = "match"
EVENT_RESULT = "result"
EVENT_LINEUP = "lineup"

EVENT_PRE_MATCH_INTERVIEW = "pre_match_interview"
EVENT_POST_MATCH_INTERVIEW = "post_match_interview"

EVENT_TRANSFER = "transfer"
EVENT_INJURY = "injury"
EVENT_COACHING = "coaching"

EVENT_PLAYER_PERFORMANCE = "player_performance"
EVENT_TEAM_NEWS = "team_news"


# ============================================================
# RESULT MODEL
# ============================================================

@dataclass
class BasketballScore:
    """
    نتیجه یک مسابقه بسکتبال.
    """

    home_team: Optional[str] = None
    away_team: Optional[str] = None

    home_score: Optional[int] = None
    away_score: Optional[int] = None

    is_detected: bool = False


# ============================================================
# DETECTION RESULT
# ============================================================

@dataclass
class BasketballDetection:
    """
    خروجی استاندارد تشخیص خبر بسکتبال.
    """

    sport: str = "basketball"

    teams: List[str] = field(
        default_factory=list
    )

    players: List[str] = field(
        default_factory=list
    )

    league: Optional[str] = None

    tournament: Optional[str] = None

    event_type: str = EVENT_UNKNOWN

    score: BasketballScore = field(
        default_factory=BasketballScore
    )

    is_match_news: bool = False

    is_interview: bool = False

    is_lineup_news: bool = False

    is_transfer_news: bool = False

    is_injury_news: bool = False

    is_performance_news: bool = False


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(
    text: str,
) -> str:
    """
    نرمال‌سازی متن فارسی و انگلیسی.
    """

    if not text:
        return ""

    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "‌": " ",
        "\u200c": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(
        text.strip().split()
    )


# ============================================================
# EVENT KEYWORDS
# ============================================================

MATCH_KEYWORDS = (
    "بازی",
    "دیدار",
    "مسابقه",
    "مقابل",
    "برابر",
    "رقابت",
    "بازی کرد",
    "game",
    "match",
    "vs",
    "versus",
)

RESULT_KEYWORDS = (
    "نتیجه",
    "پیروز",
    "پیروزی",
    "برد",
    "شکست",
    "باخت",
    "برنده",
    "مغلوب",
    "score",
    "final",
    "won",
    "lost",
    "defeated",
)

LINEUP_KEYWORDS = (
    "ترکیب",
    "ترکیب اصلی",
    "ترکیب اولیه",
    "پنج نفره",
    "starting lineup",
    "starting five",
    "lineup",
)

PRE_INTERVIEW_KEYWORDS = (
    "پیش از بازی",
    "قبل از بازی",
    "پیش از دیدار",
    "قبل از دیدار",
    "کنفرانس خبری پیش از بازی",
    "مصاحبه پیش از بازی",
    "صحبت های پیش از بازی",
    "صحبت‌های پیش از بازی",
    "pre-match interview",
    "pre match interview",
    "before the game",
    "before the match",
)

POST_INTERVIEW_KEYWORDS = (
    "پس از بازی",
    "بعد از بازی",
    "پس از دیدار",
    "بعد از دیدار",
    "کنفرانس خبری پس از بازی",
    "مصاحبه پس از بازی",
    "صحبت های پس از بازی",
    "صحبت‌های پس از بازی",
    "post-match interview",
    "post match interview",
    "after the game",
    "after the match",
)

TRANSFER_KEYWORDS = (
    "انتقال",
    "نقل و انتقال",
    "نقل‌وانتقال",
    "قرارداد",
    "تمدید قرارداد",
    "به خدمت گرفت",
    "پیوست",
    "جدا شد",
    "transfer",
    "signed",
    "signing",
    "contract",
)

INJURY_KEYWORDS = (
    "مصدوم",
    "مصدومیت",
    "آسیب دیدگی",
    "آسیب‌دیدگی",
    "آسیب دید",
    "injury",
    "injured",
)

PERFORMANCE_KEYWORDS = (
    "امتیاز",
    "ریباند",
    "پاس گل",
    "پاس منجر به امتیاز",
    "سه امتیازی",
    "دانک",
    "دبل دبل",
    "تریپل دبل",
    "double-double",
    "triple-double",
    "points",
    "rebounds",
    "assists",
)

COACHING_KEYWORDS = (
    "سرمربی",
    "مربی",
    "مربیگری",
    "اخراج سرمربی",
    "coach",
    "head coach",
)

TEAM_NEWS_KEYWORDS = (
    "باشگاه",
    "تیم",
    "club",
    "team",
)


# ============================================================
# KEYWORD MATCH
# ============================================================

def contains_keyword(
    text: str,
    keywords: tuple,
) -> bool:
    """
    بررسی وجود حداقل یکی از کلیدواژه‌ها.
    """

    normalized = normalize_text(
        text
    ).lower()

    for keyword in keywords:

        if normalize_text(
            keyword
        ).lower() in normalized:
            return True

    return False


# ============================================================
# EVENT TYPE
# ============================================================

def detect_event_type(
    text: str,
) -> str:
    """
    تشخیص نوع خبر بسکتبال.

    ترتیب اهمیت عمداً مشخص شده تا خبرهای
    مصاحبه و نتیجه با نوع عمومی Match
    اشتباه نشوند.
    """

    if contains_keyword(
        text,
        PRE_INTERVIEW_KEYWORDS,
    ):
        return EVENT_PRE_MATCH_INTERVIEW

    if contains_keyword(
        text,
        POST_INTERVIEW_KEYWORDS,
    ):
        return EVENT_POST_MATCH_INTERVIEW

    if contains_keyword(
        text,
        LINEUP_KEYWORDS,
    ):
        return EVENT_LINEUP

    if contains_keyword(
        text,
        TRANSFER_KEYWORDS,
    ):
        return EVENT_TRANSFER

    if contains_keyword(
        text,
        INJURY_KEYWORDS,
    ):
        return EVENT_INJURY

    if contains_keyword(
        text,
        PERFORMANCE_KEYWORDS,
    ):
        return EVENT_PLAYER_PERFORMANCE

    if contains_keyword(
        text,
        COACHING_KEYWORDS,
    ):
        return EVENT_COACHING

    if contains_keyword(
        text,
        RESULT_KEYWORDS,
    ):
        return EVENT_RESULT

    if contains_keyword(
        text,
        MATCH_KEYWORDS,
    ):
        return EVENT_MATCH

    if contains_keyword(
        text,
        TEAM_NEWS_KEYWORDS,
    ):
        return EVENT_TEAM_NEWS

    return EVENT_UNKNOWN


# ============================================================
# SCORE DETECTION
# ============================================================

def detect_score(
    text: str,
    teams: List[str],
) -> BasketballScore:
    """
    تشخیص نتیجه مسابقه.

    الگوهای متداول:

        Team 98-92 Team
        Team 98 : 92 Team
        Team 98–92 Team
        Team 98 92 Team

    در صورت پیدا نشدن نتیجه، is_detected=False است.
    """

    result = BasketballScore()

    if len(teams) < 2:
        return result

    normalized = normalize_text(
        text
    )

    # --------------------------------------------------------
    # SCORE PATTERNS
    # --------------------------------------------------------

    patterns = [
        r"(\d{1,3})\s*[-–—:]\s*(\d{1,3})",
        r"(\d{1,3})\s+(\d{1,3})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            normalized,
        )

        if not match:
            continue

        try:

            home_score = int(
                match.group(1)
            )

            away_score = int(
                match.group(2)
            )

        except (
            ValueError,
            IndexError,
        ):
            continue

        # بسکتبال معمولاً امتیازهای
        # بالاتر از 30 دارد.
        # برای جلوگیری از تشخیص اشتباه
        # تاریخ یا شماره خبر، حداقل یکی
        # از امتیازها باید >= 30 باشد.

        if (
            home_score < 30
            and away_score < 30
        ):
            continue

        result.home_team = teams[0]
        result.away_team = teams[1]

        result.home_score = home_score
        result.away_score = away_score

        result.is_detected = True

        return result

    return result


# ============================================================
# MAIN DETECTOR
# ============================================================

def detect_basketball(
    text: str,
) -> BasketballDetection:
    """
    تحلیل کامل یک متن خبری بسکتبال.
    """

    result = BasketballDetection()

    if not text:
        return result

    normalized = normalize_text(
        text
    )

    # --------------------------------------------------------
    # TEAMS
    # --------------------------------------------------------

    result.teams = find_teams_in_text(
        normalized
    )

    # --------------------------------------------------------
    # PLAYERS
    # --------------------------------------------------------

    result.players = find_players_in_text(
        normalized
    )

    # --------------------------------------------------------
    # LEAGUE
    # --------------------------------------------------------

    result.league = find_league_in_text(
    normalized
    )

    # --------------------------------------------------------
    # TOURNAMENT
    # --------------------------------------------------------

    result.tournament = find_tournament_in_text(
    normalized
    )

    # --------------------------------------------------------
    # EVENT TYPE
    # --------------------------------------------------------

    result.event_type = detect_event_type(
        normalized
    )

    # --------------------------------------------------------
    # FLAGS
    # --------------------------------------------------------

    result.is_match_news = (
        result.event_type
        in {
            EVENT_MATCH,
            EVENT_RESULT,
            EVENT_LINEUP,
            EVENT_PRE_MATCH_INTERVIEW,
            EVENT_POST_MATCH_INTERVIEW,
        }
    )

    result.is_interview = (
        result.event_type
        in {
            EVENT_PRE_MATCH_INTERVIEW,
            EVENT_POST_MATCH_INTERVIEW,
        }
    )

    result.is_lineup_news = (
        result.event_type
        == EVENT_LINEUP
    )

    result.is_transfer_news = (
        result.event_type
        == EVENT_TRANSFER
    )

    result.is_injury_news = (
        result.event_type
        == EVENT_INJURY
    )

    result.is_performance_news = (
        result.event_type
        == EVENT_PLAYER_PERFORMANCE
    )

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    result.score = detect_score(
        normalized,
        result.teams,
    )

    # اگر نتیجه پیدا شد،
    # نوع خبر را Result در نظر می‌گیریم.
    if result.score.is_detected:
        result.event_type = EVENT_RESULT
        result.is_match_news = True

    return result


# ============================================================
# CONVENIENCE HELPERS
# ============================================================

def detect_basketball_from_parts(
    title: str = "",
    summary: str = "",
    content: str = "",
) -> BasketballDetection:
    """
    تحلیل خبر با ترکیب عنوان، خلاصه و متن.
    """

    combined = "\n".join(
        part
        for part in (
            title,
            summary,
            content,
        )
        if part
    )

    return detect_basketball(
        combined
    )


def is_basketball_news(
    text: str,
) -> bool:
    """
    بررسی اولیه اینکه متن نشانه‌های
    خبر بسکتبال دارد یا خیر.

    این تابع جای Category Engine را نمی‌گیرد.
    """

    result = detect_basketball(
        text
    )

    return bool(
        result.teams
        or result.players
        or result.league
        or result.tournament
        or result.event_type != EVENT_UNKNOWN
    )
