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
    "Tasnim": "🇮🇷",
    "Fars": "🇮🇷",
    "ISNA": "🇮🇷",
    "IRNA": "🇮🇷",
    "Mehr": "🇮🇷",
    "Khabar Fouri": "🇮🇷",
    "KhabarFoori": "🇮🇷",
    "خبر فوری": "🇮🇷",
    "Vahid": "🇮🇷",
    "Vahid Online": "🇮🇷",
    "وحید آنلاین": "🇮🇷",
    "Hengaw": "🇳🇴",
    "هنگاو": "🇳🇴",
    "Iran International": "🇬🇧",
    "ایران اینترنشنال": "🇬🇧",
}

# نگاشت با حروف کوچک، تا تفاوت بزرگ/کوچک حروف (BBC در برابر bbc) باعث
# نشود منبعی که واقعاً تعریف شده، به‌اشتباه به پرچم پیش‌فرض بیفتد.
_NORMALIZED_FLAGS = {key.lower(): value for key, value in FLAGS.items()}


def get_flag(source):
    if not source:
        return "🌍"
    return _NORMALIZED_FLAGS.get(source.strip().lower(), "🌍")
