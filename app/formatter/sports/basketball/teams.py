"""
Basketball Teams Registry
KhabarF24

استانداردسازی نام تیم‌های بسکتبال برای Formatter و Hashtag Engine.
"""

from typing import Dict, List, Optional


# ============================================================
# BASKETBALL TEAMS
# ============================================================

BASKETBALL_TEAMS: Dict[str, List[str]] = {

    # ========================================================
    # NBA
    # ========================================================

    "Los Angeles Lakers": [
        "Los Angeles Lakers",
        "LA Lakers",
        "Lakers",
        "LA لیکرز",
        "لس آنجلس لیکرز",
        "لیکرز",
    ],

    "Boston Celtics": [
        "Boston Celtics",
        "Boston",
        "Celtics",
        "بوستون سلتیکس",
        "سلتیکس",
    ],

    "Golden State Warriors": [
        "Golden State Warriors",
        "Golden State",
        "Warriors",
        "GSW",
        "گلدن استیت وریرز",
        "گلدن استیت",
        "وریورز",
    ],

    "Chicago Bulls": [
        "Chicago Bulls",
        "Chicago",
        "Bulls",
        "شیکاگو بولز",
        "بولز",
    ],

    "Miami Heat": [
        "Miami Heat",
        "Miami",
        "Heat",
        "میامی هیت",
        "هیت",
    ],

    "Milwaukee Bucks": [
        "Milwaukee Bucks",
        "Milwaukee",
        "Bucks",
        "میلواکی باکس",
        "باکس",
    ],

    "Phoenix Suns": [
        "Phoenix Suns",
        "Phoenix",
        "Suns",
        "فینیکس سانز",
        "سانز",
    ],

    "Denver Nuggets": [
        "Denver Nuggets",
        "Denver",
        "Nuggets",
        "دنور ناگتس",
        "ناگتس",
    ],

    "Dallas Mavericks": [
        "Dallas Mavericks",
        "Dallas",
        "Mavericks",
        "Mavs",
        "دالاس ماوریکس",
        "ماوریکس",
    ],

    "Los Angeles Clippers": [
        "Los Angeles Clippers",
        "LA Clippers",
        "Clippers",
        "LA کلیپرز",
        "لس آنجلس کلیپرز",
        "کلیپرز",
    ],

    "New York Knicks": [
        "New York Knicks",
        "New York",
        "Knicks",
        "نیویورک نیکس",
        "نیکس",
    ],

    "Brooklyn Nets": [
        "Brooklyn Nets",
        "Brooklyn",
        "Nets",
        "بروکلین نتس",
        "نتس",
    ],

    "Philadelphia 76ers": [
        "Philadelphia 76ers",
        "Philadelphia Sixers",
        "76ers",
        "Sixers",
        "فیلادلفیا سونی‌سیکسرز",
        "فیلادلفیا سیکسزرز",
        "سیکسرز",
    ],

    "Houston Rockets": [
        "Houston Rockets",
        "Houston",
        "Rockets",
        "هیوستون راکتس",
        "راکتس",
    ],

    "San Antonio Spurs": [
        "San Antonio Spurs",
        "San Antonio",
        "Spurs",
        "سن آنتونیو اسپرز",
        "اسپرز",
    ],

    "Oklahoma City Thunder": [
        "Oklahoma City Thunder",
        "Oklahoma City",
        "Thunder",
        "OKC",
        "اوکلاهما سیتی تاندر",
        "تاندر",
    ],

    "Minnesota Timberwolves": [
        "Minnesota Timberwolves",
        "Minnesota",
        "Timberwolves",
        "Timberwolves",
        "مینسوتا تیمبروولوز",
        "تیمبروولوز",
    ],

    "Cleveland Cavaliers": [
        "Cleveland Cavaliers",
        "Cleveland",
        "Cavaliers",
        "Cavs",
        "کلیولند کاوالیرز",
        "کاوالیرز",
    ],

    "Detroit Pistons": [
        "Detroit Pistons",
        "Detroit",
        "Pistons",
        "دیترویت پیستونز",
        "پیستونز",
    ],

    "Atlanta Hawks": [
        "Atlanta Hawks",
        "Atlanta",
        "Hawks",
        "آتلانتا هاوکس",
        "هاوکس",
    ],

    "Toronto Raptors": [
        "Toronto Raptors",
        "Toronto",
        "Raptors",
        "تورنتو رپترز",
        "رپترز",
    ],

    "Sacramento Kings": [
        "Sacramento Kings",
        "Sacramento",
        "Kings",
        "ساکرامنتو کینگز",
        "کینگز",
    ],

    "New Orleans Pelicans": [
        "New Orleans Pelicans",
        "New Orleans",
        "Pelicans",
        "نیواورلئان پلیکانز",
        "پلیکانز",
    ],

    "Memphis Grizzlies": [
        "Memphis Grizzlies",
        "Memphis",
        "Grizzlies",
        "ممفیس گریزلیز",
        "گریزلیز",
    ],

    "Portland Trail Blazers": [
        "Portland Trail Blazers",
        "Portland",
        "Trail Blazers",
        "Blazers",
        "پورتلند تریل بلیزرز",
        "تریل بلیزرز",
    ],

    "Utah Jazz": [
        "Utah Jazz",
        "Utah",
        "Jazz",
        "یوتا جاز",
        "جاز",
    ],

    "Washington Wizards": [
        "Washington Wizards",
        "Washington",
        "Wizards",
        "واشنگتن ویزاردز",
        "ویزاردز",
    ],

    "Orlando Magic": [
        "Orlando Magic",
        "Orlando",
        "Magic",
        "اورلاندو مجیک",
        "مجیک",
    ],

    "Charlotte Hornets": [
        "Charlotte Hornets",
        "Charlotte",
        "Hornets",
        "شارلوت هورنتس",
        "هورنتس",
    ],

    "Indiana Pacers": [
        "Indiana Pacers",
        "Indiana",
        "Pacers",
        "ایندیانا پیسرز",
        "پیسرز",
    ],

    # ========================================================
    # EUROLEAGUE / EUROPE
    # ========================================================

    "Real Madrid Basketball": [
        "Real Madrid Basketball",
        "Real Madrid Baloncesto",
        "Real Madrid Basket",
        "رئال مادرید بسکتبال",
        "رئال مادرید",
    ],

    "Barcelona Basketball": [
        "Barcelona Basketball",
        "FC Barcelona Basketball",
        "Barça Basket",
        "Barcelona Basket",
        "بارسلونا بسکتبال",
        "بارسا بسکتبال",
    ],

    "Panathinaikos Basketball": [
        "Panathinaikos BC",
        "Panathinaikos Basketball",
        "Panathinaikos",
        "پاناتینایکوس",
        "پاناتینایکوس بسکتبال",
    ],

    "Olympiacos Basketball": [
        "Olympiacos BC",
        "Olympiacos Basketball",
        "Olympiacos",
        "المپیاکوس",
        "المپیاکوس بسکتبال",
    ],

    "Fenerbahce Basketball": [
        "Fenerbahçe Beko",
        "Fenerbahce Basketball",
        "Fenerbahce Beko Basketball",
        "Fenerbahçe",
        "فنرباغچه بسکتبال",
        "فنرباحچه بسکتبال",
    ],

    "Anadolu Efes": [
        "Anadolu Efes",
        "Anadolu Efes Istanbul",
        "Anadolu Efes Basketball",
        "آنادولو افس",
        "آنادولو افس بسکتبال",
    ],

    "Partizan Basketball": [
        "Partizan BC",
        "Partizan Basketball",
        "Partizan",
        "پارتیزان",
        "پارتیزان بسکتبال",
    ],

    "Crvena zvezda Basketball": [
        "Crvena zvezda",
        "Crvena Zvezda Basketball",
        "Red Star Belgrade Basketball",
        "ستاره سرخ بلگراد",
        "ستاره سرخ بسکتبال",
    ],

    "AS Monaco Basket": [
        "AS Monaco Basket",
        "Monaco Basketball",
        "AS Monaco",
        "موناکو بسکتبال",
    ],

    "Olympia Milano": [
        "Olimpia Milano",
        "EA7 Emporio Armani Milano",
        "Armani Milano",
        "میلان بسکتبال",
        "المپیا میلان",
    ],

    "Virtus Bologna": [
        "Virtus Bologna",
        "Virtus Segafredo Bologna",
        "Virtus",
        "ویرتوس بولونیا",
    ],

    "Bayern Munich Basketball": [
        "Bayern Munich Basketball",
        "FC Bayern Basketball",
        "Bayern Basketball",
        "بایرن مونیخ بسکتبال",
    ],

    # ========================================================
    # IRAN
    # ========================================================

    "Petro Novin Mahshahr": [
        "Petro Novin Mahshahr",
        "Petro Novin",
        "پترو نوین ماهشهر",
        "پترو نوین",
    ],

    "Shahrdari Gorgan": [
        "Shahrdari Gorgan",
        "Gorgan",
        "شهرداری گرگان",
    ],

    "Mahram Tehran": [
        "Mahram Tehran",
        "Mahram",
        "مهرام تهران",
        "مهرام",
    ],

    "Zob Ahan Isfahan Basketball": [
        "Zob Ahan Basketball",
        "Zob Ahan Isfahan Basketball",
        "ذوب آهن بسکتبال",
        "ذوب‌آهن اصفهان",
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(
    text: str,
) -> str:
    """
    نرمال‌سازی نام تیم.
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
# EXACT TEAM LOOKUP
# ============================================================

def find_team(
    text: str,
) -> Optional[str]:
    """
    تشخیص نام استاندارد تیم.
    """

    normalized = normalize_text(text)

    if not normalized:
        return None

    for canonical, aliases in BASKETBALL_TEAMS.items():

        if normalize_text(canonical) == normalized:
            return canonical

        for alias in aliases:

            if normalize_text(alias) == normalized:
                return canonical

    return None


# ============================================================
# TEAM IN TEXT
# ============================================================

def find_team_in_text(
    text: str,
) -> Optional[str]:
    """
    پیدا کردن یک تیم بسکتبال در متن خبر.
    """

    normalized = normalize_text(text)

    if not normalized:
        return None

    candidates = []

    for canonical, aliases in BASKETBALL_TEAMS.items():

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

    # تطبیق‌های طولانی‌تر اولویت دارند.
    candidates.sort(
        key=lambda item: len(item[1]),
        reverse=True,
    )

    for canonical, alias in candidates:

        if alias and alias in normalized:
            return canonical

    return None


# ============================================================
# FIND ALL TEAMS
# ============================================================

def find_teams_in_text(
    text: str,
) -> List[str]:
    """
    پیدا کردن تمام تیم‌های شناخته‌شده در متن.

    نتیجه بدون تکرار برگردانده می‌شود.
    """

    normalized = normalize_text(text)

    if not normalized:
        return []

    candidates = []

    for canonical, aliases in BASKETBALL_TEAMS.items():

        all_names = [
            canonical,
            *aliases,
        ]

        for name in all_names:

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

def get_team_aliases(
    team: str,
) -> List[str]:
    """
    دریافت Aliasهای یک تیم.
    """

    canonical = find_team(team)

    if not canonical:
        return []

    return list(
        BASKETBALL_TEAMS.get(
            canonical,
            [],
        )
    )


# ============================================================
# GET ALL TEAMS
# ============================================================

def get_all_teams() -> List[str]:
    """
    دریافت فهرست تیم‌های استاندارد.
    """

    return list(
        BASKETBALL_TEAMS.keys()
    )


# ============================================================
# CHECK
# ============================================================

def is_team(
    text: str,
) -> bool:
    """
    بررسی اینکه متن نام یک تیم شناخته‌شده است یا خیر.
    """

    return find_team(text) is not None
