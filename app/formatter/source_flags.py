"""
Country Flags For News Sources
"""

FLAGS = {
    "Reuters": "🇬🇧",
    "BBC": "🇬🇧",
    "Sky Sports": "🇬🇧",
    "Guardian": "🇬🇧",
    "The Guardian": "🇬🇧",
    "AP": "🇺🇸",
    "Associated Press": "🇺🇸",
    "CNN": "🇺🇸",
    "ESPN": "🇺🇸",
    "FOX": "🇺🇸",
    "Fox News": "🇺🇸",
    "NYTimes": "🇺🇸",
    "NY Times": "🇺🇸",
    "The New York Times": "🇺🇸",
    "Di Marzio": "🇮🇹",
    "Gazzetta": "🇮🇹",
    "Fabrizio Romano": "🇮🇹",
    "Marca": "🇪🇸",
    "AS": "🇪🇸",
    "L'Équipe": "🇫🇷",
    "AFP": "🇫🇷",
    "Euronews": "🇫🇷",
    "Kicker": "🇩🇪",
    "Bild": "🇩🇪",
    "Al Jazeera": "🇶🇦",
    "Tasnim News": "🇮🇷",
    "Fars": "🇮🇷",
    "ISNA": "🇮🇷",
    "IRNA": "🇮🇷",
    "Mehr News": "🇮🇷",
    "Khabar Online": "🇮🇷",
    "Tabnak": "🇮🇷",
    "YJC": "🇮🇷",
    "Vahid Online": "🇮🇷",
    "Hengaw": "🇳🇴",
    "Iran International": "🇬🇧",
}

_NORMALIZED_FLAGS = {key.lower(): value for key, value in FLAGS.items()}


def get_flag(source):
    if not source:
        return "🌍"
    return _NORMALIZED_FLAGS.get(source.strip().lower(), "🌍")
