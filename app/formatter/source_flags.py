"""
Country Flags For News Sources
پرچم کشور منابع خبری KhabarF24

ترتیب جست‌وجو:
۱) فهرست دستی (FLAGS)، با تطبیق دقیق اسم
۲) فیلد «flag» همان منبع در data/sources/*.json، با تطبیق دقیق اسم
۳) فهرست دستی، با تطبیق پیشوند ("BBC Football RSS" ← "BBC Football")
۴) پرچم پیش‌فرض 🌍
"""

FLAGS = {
    # United Kingdom
    "Reuters": "🇬🇧",
    "BBC": "🇬🇧",
    "BBC Sport": "🇬🇧",
    "BBC Football": "🇬🇧",
    "Sky Sports": "🇬🇧",
    "Sky Sports Football": "🇬🇧",
    "Guardian": "🇬🇧",
    "The Guardian": "🇬🇧",
    "Premier League": "🇬🇧",
    "Iran International": "🇬🇧",

    # United States
    "AP": "🇺🇸",
    "Associated Press": "🇺🇸",
    "CNN": "🇺🇸",
    "ESPN": "🇺🇸",
    "ESPN Soccer": "🇺🇸",
    "FOX": "🇺🇸",
    "Fox News": "🇺🇸",
    "NYTimes": "🇺🇸",
    "NY Times": "🇺🇸",
    "The New York Times": "🇺🇸",

    # Italy
    "Di Marzio": "🇮🇹",
    "Gianluca Di Marzio": "🇮🇹",
    "Gazzetta": "🇮🇹",
    "Fabrizio Romano": "🇮🇹",
    "Fabrizio Romano Telegram": "🇮🇹",

    # Spain
    "Marca": "🇪🇸",
    "AS": "🇪🇸",

    # France
    "L'Équipe": "🇫🇷",
    "AFP": "🇫🇷",
    "Euronews": "🇫🇷",
    "API-Football": "🇫🇷",

    # Germany
    "Kicker": "🇩🇪",
    "Bild": "🇩🇪",
    "Transfermarkt": "🇩🇪",

    # Qatar
    "Al Jazeera": "🇶🇦",

    # Iran
    "Tasnim News": "🇮🇷",
    "Tasnim": "🇮🇷",
    "Fars": "🇮🇷",
    "ISNA": "🇮🇷",
    "IRNA": "🇮🇷",
    "Mehr News": "🇮🇷",
    "Khabar Online": "🇮🇷",
    "Tabnak": "🇮🇷",
    "YJC": "🇮🇷",
    "Vahid Online": "🇮🇷",

    # Norway
    "Hengaw": "🇳🇴",

    # Switzerland
    "UEFA": "🇨🇭",
    "FIFA": "🇨🇭",
}


def _normalize(name) -> str:
    return " ".join(
        str(name or "").replace("\u200c", "").strip().casefold().split()
    )


_NORMALIZED_FLAGS = {
    _normalize(key): value for key, value in FLAGS.items()
}

_json_flags = None
_json_attempts = 0


def _flags_from_sources() -> dict:
    """نام منبع ← پرچم، از فایل‌های data/sources/*.json (یک‌بار خوانده می‌شود)."""
    global _json_flags, _json_attempts

    if _json_flags is not None:
        return _json_flags

    if _json_attempts >= 3:
        return {}

    _json_attempts += 1

    flags = {}

    try:
        from config.sources import load_sources

        for source in load_sources():
            name = _normalize(getattr(source, "name", ""))
            flag = str(getattr(source, "flag", "") or "").strip()

            if name and flag:
                flags[name] = flag

    except Exception:
        flags = {}

    if flags:
        _json_flags = flags

    return flags


def get_flag(source):
    """
    Return the flag for a known news source.
    """

    if not source:
        return "🌍"

    name = _normalize(source)

    if not name:
        return "🌍"

    # ۱) فهرست دستی، تطبیق دقیق
    flag = _NORMALIZED_FLAGS.get(name)

    if flag:
        return flag

    # ۲) پرچم خود منبع در JSON، تطبیق دقیق
    flag = _flags_from_sources().get(name)

    if flag:
        return flag

    # ۳) فهرست دستی، تطبیق پیشوند؛ بلندترین اسم‌ها اول
    for known_name in sorted(
        _NORMALIZED_FLAGS,
        key=len,
        reverse=True,
    ):
        if name.startswith(known_name + " "):
            return _NORMALIZED_FLAGS[known_name]

    return "🌍"
