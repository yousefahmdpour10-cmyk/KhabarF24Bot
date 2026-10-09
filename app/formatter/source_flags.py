```python
"""
Country Flags For News Sources
پرچم کشور منابع خبری KhabarF24
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

_NORMALIZED_FLAGS = {
    key.strip().lower(): value
    for key, value in FLAGS.items()
}


def get_flag(source):
    """
    Return the flag for a known news source.
    Supports exact names and source names with suffixes.
    """

    if not source:
        return "🌍"

    name = str(source).strip().lower()

    if not name:
        return "🌍"

    # First, try an exact match.
    flag = _NORMALIZED_FLAGS.get(name)

    if flag:
        return flag

    # Then match known source prefixes, longest names first.
    # This supports names such as "BBC Football RSS".
    for known_name in sorted(
        _NORMALIZED_FLAGS,
        key=len,
        reverse=True,
    ):
        if name.startswith(known_name + " "):
            return _NORMALIZED_FLAGS[known_name]

    return "🌍"
