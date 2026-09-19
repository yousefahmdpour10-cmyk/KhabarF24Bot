"""
KhabarF24 Entity Dictionary

Standard names and aliases for entities used by the Entity Engine.
"""


# ============================================================
# FOOTBALL TEAMS
# ============================================================

FOOTBALL_TEAMS = {

    "Manchester United": [
        "Manchester United",
        "Man United",
        "Man Utd",
        "Manchester Utd",
        "Man U",
        "MUFC",
        "منچستر یونایتد",
        "منچستریونایتد",
        "منچستر یونایتد اف سی",
    ],

    "Manchester City": [
        "Manchester City",
        "Man City",
        "Man C",
        "Manchester City FC",
        "MCFC",
        "منچستر سیتی",
        "منچسترسیتی",
    ],

    "Liverpool": [
        "Liverpool",
        "Liverpool FC",
        "LFC",
        "لیورپول",
    ],

    "Arsenal": [
        "Arsenal",
        "Arsenal FC",
        "AFC",
        "آرسنال",
    ],

    "Chelsea": [
        "Chelsea",
        "Chelsea FC",
        "CFC",
        "چلسی",
    ],

    "Real Madrid": [
        "Real Madrid",
        "Real Madrid CF",
        "Los Blancos",
        "رئال مادرید",
        "رئال‌مادرید",
        "رئال‌مادريد",
    ],

    "Barcelona": [
        "Barcelona",
        "FC Barcelona",
        "Barca",
        "Barça",
        "بارسلونا",
        "بارسا",
    ],

    "Bayern Munich": [
        "Bayern Munich",
        "Bayern",
        "FC Bayern",
        "Bayern München",
        "بایرن مونیخ",
        "بایرن‌مونیخ",
    ],

    "Paris Saint-Germain": [
        "Paris Saint-Germain",
        "Paris Saint Germain",
        "PSG",
        "پاری سن ژرمن",
        "پاریس سن ژرمن",
        "پاری‌سن‌ژرمن",
    ],

    "Inter Milan": [
        "Inter Milan",
        "Inter Milano",
        "Internazionale",
        "اینتر میلان",
        "اینترمیلان",
    ],

    "AC Milan": [
        "AC Milan",
        "ACMilan",
        "آث میلان",
        "ای سی میلان",
        "میلان",
    ],

    "Juventus": [
        "Juventus",
        "Juve",
        "یوونتوس",
    ],
}


# ============================================================
# FOOTBALL LEAGUES
# ============================================================

FOOTBALL_LEAGUES = {

    "Premier League": [
        "Premier League",
        "EPL",
        "English Premier League",
        "پریمیرلیگ",
        "پریمیر لیگ",
        "لیگ برتر انگلیس",
    ],

    "La Liga": [
        "La Liga",
        "LaLiga",
        "Spanish La Liga",
        "لالیگا",
        "لالیگا اسپانیا",
    ],

    "Serie A": [
        "Serie A",
        "Italian Serie A",
        "سری آ",
        "سری‌آ",
        "سری آ ایتالیا",
    ],

    "Bundesliga": [
        "Bundesliga",
        "German Bundesliga",
        "بوندسلیگا",
        "بوندس‌لیگا",
    ],

    "Ligue 1": [
        "Ligue 1",
        "French Ligue 1",
        "لیگ ۱ فرانسه",
        "لیگ یک فرانسه",
        "لوشامپیونه",
    ],
}


# ============================================================
# FOOTBALL TOURNAMENTS
# ============================================================

FOOTBALL_TOURNAMENTS = {

    "UEFA Champions League": [
        "UEFA Champions League",
        "Champions League",
        "UCL",
        "لیگ قهرمانان اروپا",
        "لیگ قهرمانان",
    ],

    "UEFA Europa League": [
        "UEFA Europa League",
        "Europa League",
        "UEL",
        "لیگ اروپا",
    ],

    "UEFA Conference League": [
        "UEFA Conference League",
        "Conference League",
        "UECL",
        "لیگ کنفرانس اروپا",
    ],

    "FIFA World Cup": [
        "FIFA World Cup",
        "World Cup",
        "جام جهانی",
        "جام جهانی فوتبال",
    ],

    "UEFA European Championship": [
        "UEFA European Championship",
        "European Championship",
        "Euro",
        "EURO",
        "جام ملت‌های اروپا",
        "یورو",
    ],
}


# ============================================================
# COUNTRIES
# ============================================================

COUNTRIES = {

    "England": [
        "England",
        "انگلیس",
        "انگلستان",
    ],

    "Spain": [
        "Spain",
        "اسپانیا",
    ],

    "Italy": [
        "Italy",
        "ایتالیا",
    ],

    "Germany": [
        "Germany",
        "آلمان",
    ],

    "France": [
        "France",
        "فرانسه",
    ],

    "Iran": [
        "Iran",
        "ایران",
    ],
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(
    text: str,
) -> str:

    if not text:
        return ""

    replacements = {

        # Arabic → Persian
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",

        # Zero-width characters
        "\u200c": " ",
        "\u200d": " ",
        "\ufeff": " ",

        # Punctuation-like separators
        "_": " ",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new,
        )

    return " ".join(
        text.strip().split()
    )


# ============================================================
# EXACT ALIAS LOOKUP
# ============================================================

def find_canonical(
    text: str,
    dictionary: dict,
) -> str | None:

    normalized = normalize_text(text)

    if not normalized:
        return None

    normalized_lower = normalized.lower()

    for canonical, aliases in dictionary.items():

        canonical_normalized = (
            normalize_text(canonical)
            .lower()
        )

        if canonical_normalized == normalized_lower:
            return canonical

        for alias in aliases:

            alias_normalized = (
                normalize_text(alias)
                .lower()
            )

            if alias_normalized == normalized_lower:

                return canonical

    return None


# ============================================================
# TEAM LOOKUP
# ============================================================

def find_team(
    text: str,
) -> str | None:

    return find_canonical(
        text,
        FOOTBALL_TEAMS,
    )


# ============================================================
# LEAGUE LOOKUP
# ============================================================

def find_league(
    text: str,
) -> str | None:

    return find_canonical(
        text,
        FOOTBALL_LEAGUES,
    )


# ============================================================
# TOURNAMENT LOOKUP
# ============================================================

def find_tournament(
    text: str,
) -> str | None:

    return find_canonical(
        text,
        FOOTBALL_TOURNAMENTS,
    )


# ============================================================
# COUNTRY LOOKUP
# ============================================================

def find_country(
    text: str,
) -> str | None:

    return find_canonical(
        text,
        COUNTRIES,
    )
