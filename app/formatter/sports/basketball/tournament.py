"""
Basketball Tournament Registry
KhabarF24

تشخیص و استانداردسازی نام تورنمنت‌های بسکتبال.

نکته:
League و Tournament عمداً از هم جدا هستند.
"""

from typing import Dict, List, Optional


# ============================================================
# BASKETBALL TOURNAMENTS
# ============================================================

BASKETBALL_TOURNAMENTS: Dict[str, List[str]] = {

    # ========================================================
    # INTERNATIONAL / FIBA
    # ========================================================

    "FIBA Basketball World Cup": [
        "FIBA Basketball World Cup",
        "FIBA World Cup",
        "Basketball World Cup",
        "World Basketball Cup",
        "جام جهانی بسکتبال",
        "جام جهانی بسکتبال فیبا",
        "جام جهانی بسکتبال مردان",
    ],

    "FIBA Women's Basketball World Cup": [
        "FIBA Women's Basketball World Cup",
        "Women's Basketball World Cup",
        "Women Basketball World Cup",
        "جام جهانی بسکتبال زنان",
        "جام جهانی بسکتبال زنان فیبا",
    ],

    "FIBA Asia Cup": [
        "FIBA Asia Cup",
        "FIBA Asian Cup",
        "Asia Cup Basketball",
        "جام ملت‌های بسکتبال آسیا",
        "جام بسکتبال آسیا",
        "جام آسیا بسکتبال",
    ],

    "FIBA Women's Asia Cup": [
        "FIBA Women's Asia Cup",
        "Women's Asia Cup Basketball",
        "Women's FIBA Asia Cup",
        "جام ملت‌های بسکتبال زنان آسیا",
        "جام بسکتبال زنان آسیا",
    ],

    "FIBA EuroBasket": [
        "FIBA EuroBasket",
        "EuroBasket",
        "EuroBasket Championship",
        "یوروبسکت",
        "یورو بسکت",
        "جام ملت‌های بسکتبال اروپا",
    ],

    "FIBA Women's EuroBasket": [
        "FIBA Women's EuroBasket",
        "Women's EuroBasket",
        "EuroBasket Women",
        "یوروبسکت زنان",
        "جام ملت‌های بسکتبال زنان اروپا",
    ],

    "FIBA AmeriCup": [
        "FIBA AmeriCup",
        "AmeriCup",
        "FIBA Americas Championship",
        "جام بسکتبال آمریکا",
        "آمریکاپ بسکتبال",
    ],

    "FIBA Women's AmeriCup": [
        "FIBA Women's AmeriCup",
        "Women's AmeriCup",
        "AmeriCup Women",
        "آمریکاپ بسکتبال زنان",
    ],

    "FIBA AfroBasket": [
        "FIBA AfroBasket",
        "AfroBasket",
        "جام بسکتبال آفریقا",
        "آفروبَسکت",
    ],

    "FIBA Women's AfroBasket": [
        "FIBA Women's AfroBasket",
        "Women's AfroBasket",
        "AfroBasket Women",
        "جام بسکتبال زنان آفریقا",
    ],

    "FIBA U19 Basketball World Cup": [
        "FIBA U19 Basketball World Cup",
        "U19 Basketball World Cup",
        "U19 World Cup Basketball",
        "جام جهانی بسکتبال زیر ۱۹ سال",
    ],

    "FIBA U17 Basketball World Cup": [
        "FIBA U17 Basketball World Cup",
        "U17 Basketball World Cup",
        "U17 World Cup Basketball",
        "جام جهانی بسکتبال زیر ۱۷ سال",
    ],

    "FIBA Women's U19 Basketball World Cup": [
        "FIBA Women's U19 Basketball World Cup",
        "Women's U19 Basketball World Cup",
        "جام جهانی بسکتبال زنان زیر ۱۹ سال",
    ],

    "FIBA Women's U17 Basketball World Cup": [
        "FIBA Women's U17 Basketball World Cup",
        "Women's U17 Basketball World Cup",
        "جام جهانی بسکتبال زنان زیر ۱۷ سال",
    ],

    # ========================================================
    # OLYMPIC
    # ========================================================

    "Olympic Basketball Tournament": [
        "Olympic Basketball",
        "Olympic Basketball Tournament",
        "Olympic Games Basketball",
        "بسکتبال المپیک",
        "مسابقات بسکتبال المپیک",
    ],

    "Olympic Women's Basketball Tournament": [
        "Olympic Women's Basketball",
        "Women's Olympic Basketball",
        "Women's Olympic Basketball Tournament",
        "بسکتبال زنان المپیک",
        "مسابقات بسکتبال زنان المپیک",
    ],

    # ========================================================
    # EUROPE
    # ========================================================

    "EuroLeague Final Four": [
        "EuroLeague Final Four",
        "Euroleague Final Four",
        "Final Four EuroLeague",
        "فاینال فور یورولیگ",
        "فینال فور یورولیگ",
    ],

    "EuroCup Basketball Playoffs": [
        "EuroCup Playoffs",
        "EuroCup Basketball Playoffs",
        "یوروکاپ پلی‌آف",
        "پلی آف یوروکاپ",
    ],

    "Basketball Champions League Final Four": [
        "Basketball Champions League Final Four",
        "BCL Final Four",
        "فاینال فور لیگ قهرمانان بسکتبال",
    ],

    # ========================================================
    # UNITED STATES
    # ========================================================

    "NBA Playoffs": [
        "NBA Playoffs",
        "NBA Postseason",
        "پلی آف NBA",
        "پلی‌آف ان‌بی‌ای",
        "پلی آف بسکتبال NBA",
    ],

    "NBA Finals": [
        "NBA Finals",
        "NBA Final",
        "Finals",
        "فینال NBA",
        "فینال ان‌بی‌ای",
    ],

    "WNBA Playoffs": [
        "WNBA Playoffs",
        "WNBA Postseason",
        "پلی آف WNBA",
        "پلی‌آف ان‌بی‌ای زنان",
    ],

    "WNBA Finals": [
        "WNBA Finals",
        "WNBA Final",
        "فینال WNBA",
        "فینال ان‌بی‌ای زنان",
    ],

    "NBA In-Season Tournament": [
        "NBA In-Season Tournament",
        "NBA Cup",
        "Emirates NBA Cup",
        "NBA Cup Tournament",
        "جام NBA",
        "جام ان‌بی‌ای",
    ],

    # ========================================================
    # COLLEGE
    # ========================================================

    "NCAA March Madness": [
        "NCAA March Madness",
        "March Madness",
        "NCAA Tournament",
        "NCAA Basketball Tournament",
        "مارچ مدنس",
        "مسابقات NCAA",
        "تورمنت NCAA",
    ],

    "NCAA Final Four": [
        "NCAA Final Four",
        "March Madness Final Four",
        "فاینال فور NCAA",
        "فینال فور بسکتبال دانشگاهی",
    ],

    # ========================================================
    # ASIA
    # ========================================================

    "FIBA Asia Champions Cup": [
        "FIBA Asia Champions Cup",
        "Asia Champions Cup Basketball",
        "Basketball Champions Cup Asia",
        "لیگ قهرمانان بسکتبال آسیا",
        "جام قهرمانان بسکتبال آسیا",
    ],

    "East Asia Super League": [
        "East Asia Super League",
        "EASL",
        "East Asian Super League",
        "سوپر لیگ شرق آسیا",
        "لیگ شرق آسیا",
    ],

    # ========================================================
    # NATIONAL / REGIONAL COMPETITIONS
    # ========================================================

    "Asian Games Basketball": [
        "Asian Games Basketball",
        "Basketball at the Asian Games",
        "بسکتبال بازی‌های آسیایی",
        "بسکتبال بازی های آسیایی",
    ],

    "Asian Games Women's Basketball": [
        "Asian Games Women's Basketball",
        "Women's Basketball at the Asian Games",
        "بسکتبال زنان بازی‌های آسیایی",
    ],

    # ========================================================
    # IRAN
    # ========================================================

    "Iran Basketball Cup": [
        "Iran Basketball Cup",
        "Iran Cup Basketball",
        "جام حذفی بسکتبال ایران",
        "جام بسکتبال ایران",
        "جام حذفی بسکتبال",
    ],

    "Iran Basketball Super Cup": [
        "Iran Basketball Super Cup",
        "Iran Super Cup Basketball",
        "سوپرجام بسکتبال ایران",
        "سوپر جام بسکتبال ایران",
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(
    text: str,
) -> str:
    """
    نرمال‌سازی متن برای تشخیص تورنمنت.
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
# EXACT LOOKUP
# ============================================================

def find_tournament(
    text: str,
) -> Optional[str]:
    """
    تشخیص نام استاندارد تورنمنت.
    """

    normalized = normalize_text(text)

    if not normalized:
        return None

    for canonical, aliases in BASKETBALL_TOURNAMENTS.items():

        if normalize_text(canonical) == normalized:
            return canonical

        for alias in aliases:

            if normalize_text(alias) == normalized:
                return canonical

    return None


# ============================================================
# TEXT LOOKUP
# ============================================================

def find_tournament_in_text(
    text: str,
) -> Optional[str]:
    """
    پیدا کردن تورنمنت در متن کامل خبر.
    """

    normalized = normalize_text(text)

    if not normalized:
        return None

    candidates = []

    for canonical, aliases in BASKETBALL_TOURNAMENTS.items():

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

    # Aliasهای طولانی‌تر اول بررسی شوند.
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

def get_tournament_aliases(
    tournament: str,
) -> List[str]:
    """
    دریافت Aliasهای یک تورنمنت.
    """

    canonical = find_tournament(
        tournament
    )

    if not canonical:
        return []

    return list(
        BASKETBALL_TOURNAMENTS.get(
            canonical,
            [],
        )
    )


# ============================================================
# GET ALL TOURNAMENTS
# ============================================================

def get_all_tournaments() -> List[str]:
    """
    دریافت تمام تورنمنت‌های استاندارد.
    """

    return list(
        BASKETBALL_TOURNAMENTS.keys()
    )


# ============================================================
# CHECK
# ============================================================

def is_tournament(
    text: str,
) -> bool:
    """
    بررسی اینکه متن یک تورنمنت شناخته‌شده است یا خیر.
    """

    return (
        find_tournament(text)
        is not None
)
