"""
Country Flags For News Sources
"""

FLAGS = {

    "Reuters": "🇬🇧",

    "BBC": "🇬🇧",

    "Sky Sports": "🇬🇧",

    "Guardian": "🇬🇧",

    "AP": "🇺🇸",

    "CNN": "🇺🇸",

    "ESPN": "🇺🇸",

    "FOX": "🇺🇸",

    "Di Marzio": "🇮🇹",

    "Gazzetta": "🇮🇹",

    "Fabrizio Romano": "🇮🇹",

    "Marca": "🇪🇸",

    "AS": "🇪🇸",

    "L'Équipe": "🇫🇷",

    "Kicker": "🇩🇪",

    "Bild": "🇩🇪",

    "Tasnim": "🇮🇷",

    "Fars": "🇮🇷",

    "ISNA": "🇮🇷",

    "IRNA": "🇮🇷",

    "Mehr": "🇮🇷",

    "Iran International": "🇮🇷",

}


def get_flag(source):

    return FLAGS.get(source, "🌍")
