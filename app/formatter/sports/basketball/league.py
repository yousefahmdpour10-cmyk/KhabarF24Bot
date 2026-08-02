"""
Basketball League Registry
KhabarF24

تشخیص و استانداردسازی نام لیگ‌های بسکتبال.

این فایل فقط مسئول لیگ است.
تورنمنت‌ها در tournament.py مدیریت می‌شوند.
باشگاه‌ها و بازیکنان در فایل‌های مربوط به Entity مدیریت می‌شوند.
"""

from typing import Dict, List, Optional


# ============================================================
# BASKETBALL LEAGUES
# ============================================================

BASKETBALL_LEAGUES: Dict[str, List[str]] = {

    # --------------------------------------------------------
    # UNITED STATES
    # --------------------------------------------------------

    "NBA": [
        "NBA",
        "National Basketball Association",
        "ان بی ای",
        "ان‌بی‌ای",
        "لیگ NBA",
        "لیگ ان بی ای",
    ],

    "WNBA": [
        "WNBA",
        "Women's National Basketball Association",
        "Women National Basketball Association",
        "لیگ WNBA",
        "ان بی ای زنان",
        "ان‌بی‌ای زنان",
    ],

    "NCAA": [
        "NCAA",
        "NCAA Basketball",
        "College Basketball",
        "بسکتبال NCAA",
        "بسکتبال دانشگاهی آمریکا",
    ],

    # --------------------------------------------------------
    # EUROPE
    # --------------------------------------------------------

    "EuroLeague": [
        "EuroLeague",
        "Euro League",
        "Turkish Airlines EuroLeague",
        "یورولیگ",
        "یورو لیگ",
    ],

    "EuroCup Basketball": [
        "EuroCup",
        "EuroCup Basketball",
        "BKT EuroCup",
        "یوروکاپ",
        "یورو کاپ",
    ],

    "Basketball Champions League": [
        "Basketball Champions League",
        "BCL",
        "FIBA Basketball Champions League",
        "لیگ قهرمانان بسکتبال",
        "لیگ قهرمانان بسکتبال اروپا",
    ],

    "FIBA Europe Cup": [
        "FIBA Europe Cup",
        "Europe Cup",
        "فیبا اروپا کاپ",
        "جام اروپا فیبا",
    ],

    # --------------------------------------------------------
    # SPAIN
    # --------------------------------------------------------

    "Liga ACB": [
        "Liga ACB",
        "ACB",
        "Liga Endesa",
        "Endesa League",
        "لیگ ACB",
        "لیگ بسکتبال اسپانیا",
        "لیگا اندسا",
    ],

    # --------------------------------------------------------
    # ITALY
    # --------------------------------------------------------

    "Lega Basket Serie A": [
        "LBA",
        "Lega Basket Serie A",
        "Serie A Basket",
        "Italian Basketball League",
        "سری آ بسکتبال ایتالیا",
        "لیگ بسکتبال ایتالیا",
    ],

    # --------------------------------------------------------
    # GERMANY
    # --------------------------------------------------------

    "Basketball Bundesliga": [
        "Basketball Bundesliga",
        "BBL",
        "easyCredit BBL",
        "German Basketball League",
        "بوندسلیگا بسکتبال",
        "لیگ بسکتبال آلمان",
    ],

    # --------------------------------------------------------
    # FRANCE
    # --------------------------------------------------------

    "LNB Pro A": [
        "LNB Pro A",
        "Betclic Elite",
        "French Pro A",
        "French Basketball League",
        "لیگ بسکتبال فرانسه",
        "پرو A فرانسه",
    ],

    # --------------------------------------------------------
    # TURKEY
    # --------------------------------------------------------

    "Basketbol Süper Ligi": [
        "Basketbol Süper Ligi",
        "BSL",
        "Turkish Basketball Super League",
        "Turkish Super League",
        "سوپر لیگ بسکتبال ترکیه",
        "لیگ بسکتبال ترکیه",
    ],

    # --------------------------------------------------------
    # GREECE
    # --------------------------------------------------------

    "Greek Basket League": [
        "Greek Basket League",
        "GBL",
        "Greek Basketball League",
        "لیگ بسکتبال یونان",
    ],

    # --------------------------------------------------------
    # ISRAEL
    # --------------------------------------------------------

    "Israeli Basketball Premier League": [
        "Israeli Basketball Premier League",
        "Israeli Premier League Basketball",
        "Winner League",
        "Israel Basketball League",
        "لیگ بسکتبال اسرائیل",
        "لیگ برتر بسکتبال اسرائیل",
    ],

    # --------------------------------------------------------
    # AUSTRALIA
    # --------------------------------------------------------

    "NBL": [
        "NBL",
        "National Basketball League",
        "Australian NBL",
        "لیگ NBL",
        "لیگ بسکتبال استرالیا",
    ],

    "WNBL": [
        "WNBL",
        "Women's National Basketball League",
        "Australian WNBL",
        "لیگ بسکتبال زنان استرالیا",
    ],

    # --------------------------------------------------------
    # CANADA
    # --------------------------------------------------------

    "CEBL": [
        "CEBL",
        "Canadian Elite Basketball League",
        "لیگ بسکتبال نخبگان کانادا",
    ],

    # --------------------------------------------------------
    # IRAN
    # --------------------------------------------------------

    "Iranian Basketball Super League": [
        "Iranian Basketball Super League",
        "Iran Basketball Super League",
        "Iran Super League Basketball",
        "لیگ برتر بسکتبال ایران",
        "سوپر لیگ بسکتبال ایران",
        "لیگ بسکتبال ایران",
    ],

    # --------------------------------------------------------
    # CHINA
    # --------------------------------------------------------

    "CBA": [
        "CBA",
        "Chinese Basketball Association",
        "Chinese Basketball League",
        "لیگ CBA",
        "لیگ بسکتبال چین",
    ],

    "WCBA": [
        "WCBA",
        "Women's Chinese Basketball Association",
        "Chinese Women's Basketball League",
        "لیگ بسکتبال زنان چین",
    ],

    # --------------------------------------------------------
    # JAPAN
    # --------------------------------------------------------

    "B.League": [
        "B.League",
        "B League",
        "Japan B.League",
        "Japanese B.League",
        "بی لیگ ژاپن",
        "لیگ بسکتبال ژاپن",
    ],

    # --------------------------------------------------------
    # SOUTH KOREA
    # --------------------------------------------------------

    "KBL": [
        "KBL",
        "Korean Basketball League",
        "South Korean Basketball League",
        "لیگ KBL",
        "لیگ بسکتبال کره جنوبی",
    ],

    "WKBL": [
        "WKBL",
        "Women's Korean Basketball League",
        "Women's Korean Basketball",
        "لیگ بسکتبال زنان کره جنوبی",
    ],

    # --------------------------------------------------------
    # PHILIPPINES
    # --------------------------------------------------------

    "PBA": [
        "PBA",
        "Philippine Basketball Association",
        "لیگ PBA",
        "لیگ بسکتبال فیلیپین",
    ],

    # --------------------------------------------------------
    # BRAZIL
    # --------------------------------------------------------

    "Novo Basquete Brasil": [
        "NBB",
        "Novo Basquete Brasil",
        "Brazilian Basketball League",
        "Brazil Basketball League",
        "لیگ بسکتبال برزیل",
        "ان بی بی",
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    نرمال‌سازی متن برای مقایسه نام لیگ‌ها.
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
        "_": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(
        text.strip().split()
    ).lower()


# ============================================================
# FIND LEAGUE
# ============================================================

def find_league(
    text: str,
) -> Optional[str]:
    """
    پیدا کردن نام استاندارد لیگ از روی نام یا Alias.
    """

    normalized = normalize_text(text)

    if not normalized:
        return None

    for canonical, aliases in BASKETBALL_LEAGUES.items():

        if normalize_text(canonical) == normalized:
            return canonical

        for alias in aliases:

            if normalize_text(alias) == normalized:
                return canonical

    return None


# ============================================================
# FIND LEAGUE IN TEXT
# ============================================================

def find_league_in_text(
    text: str,
) -> Optional[str]:
    """
    جست‌وجوی لیگ داخل یک متن خبری.

    برخلاف find_league، این تابع لازم نیست کل متن
    دقیقاً برابر نام لیگ باشد.
    """

    normalized = normalize_text(text)

    if not normalized:
        return None

    # Aliasهای طولانی‌تر ابتدا بررسی می‌شوند تا
    # تطابق‌های دقیق‌تر اولویت داشته باشند.
    candidates = []

    for canonical, aliases in BASKETBALL_LEAGUES.items():

        candidates.append(
            (
                canonical,
                normalize_text(canonical),
            )
        )

        for alias in aliases:
            candidates.append(
                (
                    canonical,
                    normalize_text(alias),
                )
            )

    candidates.sort(
        key=lambda item: len(item[1]),
        reverse=True,
    )

    for canonical, alias in candidates:

        if alias and alias in normalized:
            return canonical

    return None


# ============================================================
# GET ALIASES
# ============================================================

def get_league_aliases(
    league: str,
) -> List[str]:
    """
    دریافت تمام Aliasهای یک لیگ.
    """

    canonical = find_league(league)

    if not canonical:
        return []

    return list(
        BASKETBALL_LEAGUES.get(
            canonical,
            [],
        )
    )


# ============================================================
# GET ALL LEAGUES
# ============================================================

def get_all_leagues() -> List[str]:
    """
    دریافت فهرست نام‌های استاندارد تمام لیگ‌ها.
    """

    return list(
        BASKETBALL_LEAGUES.keys()
    )


# ============================================================
# CHECK LEAGUE
# ============================================================

def is_league(
    text: str,
) -> bool:
    """
    بررسی اینکه متن نام یک لیگ شناخته‌شده است یا خیر.
    """

    return find_league(text) is not None
