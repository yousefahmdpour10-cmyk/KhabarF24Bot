"""
Source Reputation Database
امتیاز اعتبار و اولویت منابع خبری KhabarF24
"""

SOURCE_REPUTATION = {
    # منابع خبری بین‌المللی
    "Reuters": 100,
    "AP": 100,
    "AFP": 98,
    "BBC": 96,
    "CNN": 94,
    "Al Jazeera": 92,
    "Guardian": 90,
    "The New York Times": 92,

    # منابع خبری ایران
    "IRNA": 85,
    "ISNA": 84,
    "Tasnim News": 82,
    "Mehr News": 82,
    "Fars": 80,
    "Khabar Online": 78,
    "Tabnak": 75,
    "YJC": 72,

    # منابع خبری و حقوق بشری ایران
    "Hengaw": 90,
    "Hengaw Organization for Human Rights": 90,
    "Iran International": 90,
    "IranIntl": 90,
    "Vahid Online": 82,
    "KhabarFori": 78,

    # منابع خبری اسرائیل
    "Israel 14": 88,
    "Channel 14": 88,
    "Israel Hayom": 85,
    "Kan News": 85,
    "Channel 12": 85,

    # منابع ورزشی بین‌المللی
    "BBC Sport": 94,
    "BBC Football": 94,
    "ESPN": 90,
    "ESPN Soccer": 90,
    "Gianluca Di Marzio": 88,
    "Transfermarkt": 85,
    "Fabrizio Romano": 90,
    "Fabrizio Romano Telegram": 90,
    "Sky Sports Football": 90,
    "UEFA": 96,
    "FIFA": 96,
    "Premier League": 96,
    "API-Football": 95,

    # منابع ورزشی ایران
    "Varzesh3": 90,
    "Varzesh 3": 90,
    "ورزش سه": 90,
    "Footballi": 85,
    "Tarafdari": 82,
}

DEFAULT_SOURCE_REPUTATION = 60
