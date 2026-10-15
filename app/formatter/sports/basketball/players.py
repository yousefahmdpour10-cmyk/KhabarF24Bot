"""
Basketball Players Registry
KhabarF24

استانداردسازی نام بازیکنان بسکتبال.

این فایل فقط مسئول تشخیص نام بازیکنان است.
"""

from typing import Dict, List, Optional


# ============================================================
# BASKETBALL PLAYERS
# ============================================================

BASKETBALL_PLAYERS: Dict[str, List[str]] = {

    # ========================================================
    # NBA
    # ========================================================

    "LeBron James": [
        "LeBron James",
        "LeBron",
        "King James",
        "لبران جیمز",
        "لبرون جیمز",
        "لبران",
        "لبرون",
    ],

    "Stephen Curry": [
        "Stephen Curry",
        "Steph Curry",
        "Steph",
        "Stephen",
        "استفن کری",
        "استف کری",
        "کری",
    ],

    "Kevin Durant": [
        "Kevin Durant",
        "KD",
        "Kevin",
        "کوین دورنت",
        "کوین دورانت",
        "دورنت",
        "دورانت",
    ],

    "Giannis Antetokounmpo": [
        "Giannis Antetokounmpo",
        "Giannis",
        "Giannis Antetokounmpo",
        "یانیس آنتتوکومپو",
        "یانیس آنتتوکونمپو",
        "یانیس",
    ],

    "Nikola Jokic": [
        "Nikola Jokic",
        "Nikola Jokić",
        "Jokic",
        "نیکولا یوکیچ",
        "نیکولا جوکیچ",
        "یوکیچ",
        "جوکیچ",
    ],

    "Luka Doncic": [
        "Luka Doncic",
        "Luka Dončić",
        "Luka",
        "Doncic",
        "دونچیچ",
        "دونچیچ",
        "لوکا",
        "لوکا دونچیچ",
    ],

    "Jayson Tatum": [
        "Jayson Tatum",
        "Tatum",
        "جیسن تیتوم",
        "تیتوم",
    ],

    "Joel Embiid": [
        "Joel Embiid",
        "Embiid",
        "جوئل امبید",
        "امبید",
    ],

    "Anthony Davis": [
        "Anthony Davis",
        "Anthony",
        "AD",
        "آنتونی دیویس",
        "دیویس",
    ],

    "James Harden": [
        "James Harden",
        "Harden",
        "جیمز هاردن",
        "هاردن",
    ],

    "Damian Lillard": [
        "Damian Lillard",
        "Dame Lillard",
        "Dame",
        "Lillard",
        "دیمین لیلارد",
        "لیلارد",
    ],

    "Kyrie Irving": [
        "Kyrie Irving",
        "Kyrie",
        "Irving",
        "کایری اروینگ",
        "کایری ایروینگ",
        "اروینگ",
        "ایروینگ",
    ],

    "Jimmy Butler": [
        "Jimmy Butler",
        "Jimmy",
        "Butler",
        "جیمی باتلر",
        "باتلر",
    ],

    "Devin Booker": [
        "Devin Booker",
        "Booker",
        "دوین بوکر",
        "بوکر",
    ],

    "Ja Morant": [
        "Ja Morant",
        "Ja",
        "Morant",
        "جا مورنت",
        "مورنت",
    ],

    "Victor Wembanyama": [
        "Victor Wembanyama",
        "Wembanyama",
        "Wemby",
        "ویکتور ومبانیاما",
        "ویکتور وِمبانیاما",
        "ومبانیاما",
        "ومبی",
    ],

    "Shai Gilgeous-Alexander": [
        "Shai Gilgeous-Alexander",
        "Shai Gilgeous Alexander",
        "Shai",
        "SGA",
        "شای گیلجس-الکساندر",
        "شای گیلجس الکساندر",
        "شای",
    ],

    "Anthony Edwards": [
        "Anthony Edwards",
        "Ant Edwards",
        "Ant-Man",
        "Anthony",
        "آنتونی ادواردز",
        "ادواردز",
    ],

    "Donovan Mitchell": [
        "Donovan Mitchell",
        "Donovan",
        "Mitchell",
        "دانوان میچل",
        "دونووان میچل",
        "میچل",
    ],

    "Zion Williamson": [
        "Zion Williamson",
        "Zion",
        "زیون ویلیامسون",
        "زیون",
    ],

    # ========================================================
    # EUROPE / EUROLEAGUE
    # ========================================================

    "Kendrick Nunn": [
        "Kendrick Nunn",
        "Nunn",
        "کندریک نان",
        "نان",
    ],

    "Mike James": [
        "Mike James",
        "Mike",
        "مایک جیمز",
        "مایک",
    ],

    "Shane Larkin": [
        "Shane Larkin",
        "Larkin",
        "شین لارکین",
        "لارکین",
    ],

    "Vasilije Micic": [
        "Vasilije Micic",
        "Vasilije Micić",
        "Micic",
        "واسیلیه میچیچ",
        "میچیچ",
    ],

    "Sergio Llull": [
        "Sergio Llull",
        "Llull",
        "سرخیو یول",
        "سرجیو یول",
        "یول",
    ],

    "Nikola Mirotic": [
        "Nikola Mirotic",
        "Nikola Mirotić",
        "Mirotic",
        "نیکولا میروتیچ",
        "میروتیچ",
    ],

    "Kostas Sloukas": [
        "Kostas Sloukas",
        "Kostas",
        "Sloukas",
        "کوستاس اسلوکاس",
        "اسلوکاس",
    ],

    # ========================================================
    # IRAN
    # ========================================================

    "Hamed Haddadi": [
        "Hamed Haddadi",
        "Haddadi",
        "حامد حدادی",
        "حدادی",
    ],

    "Behnam Yakhchalidehkordi": [
        "Behnam Yakhchalidehkordi",
        "Behnam Yakhchali",
        "Yakhchali",
        "بهنام یخچالی",
        "یخچالی",
    ],

    "Saman Veisi": [
        "Saman Veisi",
        "Saman Vaisi",
        "Veisi",
        "Saman",
        "سامان ویسی",
        "ویسی",
    ],

    "Arsalan Kazemi": [
        "Arsalan Kazemi",
        "Kazemi",
        "ارسلان کاظمی",
        "کاظمی",
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(
    text: str,
) -> str:
    """
    نرمال‌سازی نام بازیکن برای مقایسه.
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
        "ي": "ی",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(
        text.strip().split()
    ).lower()


# ============================================================
# EXACT LOOKUP
# ============================================================

def find_player(
    text: str,
) -> Optional[str]:
    """
    تشخیص نام استاندارد بازیکن.
    """

    normalized = normalize_text(text)

    if not normalized:
        return None

    for canonical, aliases in BASKETBALL_PLAYERS.items():

        if normalize_text(canonical) == normalized:
            return canonical

        for alias in aliases:

            if normalize_text(alias) == normalized:
                return canonical

    return None


# ============================================================
# PLAYER IN TEXT
# ============================================================

def find_player_in_text(
    text: str,
) -> Optional[str]:
    """
    پیدا کردن یک بازیکن بسکتبال در متن خبر.
    """

    normalized = normalize_text(text)

    if not normalized:
        return None

    candidates = []

    for canonical, aliases in BASKETBALL_PLAYERS.items():

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

    # نام‌های طولانی‌تر اول بررسی شوند.
    candidates.sort(
        key=lambda item: len(item[1]),
        reverse=True,
    )

    for canonical, alias in candidates:

        if alias and alias in normalized:
            return canonical

    return None


# ============================================================
# FIND ALL PLAYERS
# ============================================================

def find_players_in_text(
    text: str,
) -> List[str]:
    """
    پیدا کردن تمام بازیکنان شناخته‌شده در متن.

    نتیجه بدون تکرار برگردانده می‌شود.
    """

    normalized = normalize_text(text)

    if not normalized:
        return []

    candidates = []

    for canonical, aliases in BASKETBALL_PLAYERS.items():

        names = [
            canonical,
            *aliases,
        ]

        for name in names:
            candidates.append(
                (
                    canonical,
                    normalize_text(name),
                )
            )

    candidates.sort(
        key=lambda item: len(item[1]),
        reverse=True,
    )

    found: List[str] = []

    for canonical, alias in candidates:

        if not alias:
            continue

        if alias in normalized:

            if canonical not in found:
                found.append(canonical)

    return found


# ============================================================
# GET ALIASES
# ============================================================

def get_player_aliases(
    player: str,
) -> List[str]:
    """
    دریافت Aliasهای یک بازیکن.
    """

    canonical = find_player(player)

    if not canonical:
        return []

    return list(
        BASKETBALL_PLAYERS.get(
            canonical,
            [],
        )
    )


# ============================================================
# GET ALL PLAYERS
# ============================================================

def get_all_players() -> List[str]:
    """
    دریافت فهرست بازیکنان استاندارد.
    """

    return list(
        BASKETBALL_PLAYERS.keys()
    )


# ============================================================
# CHECK
# ============================================================

def is_player(
    text: str,
) -> bool:
    """
    بررسی اینکه متن نام یک بازیکن شناخته‌شده است یا خیر.
    """

    return find_player(text) is not None
