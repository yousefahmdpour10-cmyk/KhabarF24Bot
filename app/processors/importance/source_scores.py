"""
Source Importance Scores
امتیاز اهمیت منابع خبری KhabarF24

این امتیاز برای ارزیابی داخلی اهمیت منبع است.
به‌تنهایی باعث فوری شدن خبر یا تضمین انتشار آن نمی‌شود.
"""

SOURCE_SCORES = {
    # منابع خبری بین‌المللی
    "Reuters": 10,
    "AP": 10,
    "AFP": 10,
    "BBC": 9,
    "CNN": 8,
    "Al Jazeera": 8,
    "Guardian": 8,
    "The New York Times": 8,
    "Euronews": 8,
    "Associated Press": 10,

    # منابع خبری ایران
    "IRNA": 7,
    "ISNA": 7,
    "Tasnim News": 7,
    "Mehr News": 7,
    "Fars": 7,
    "Khabar Online": 6,
    "Tabnak": 6,
    "YJC": 5,
    "KhabarFori": 6,
    "Vahid Online": 7,

    # منابع خبری و حقوق بشری ایران
    "Hengaw": 8,
    "Hengaw News": 8,
    "Hengaw Organization for Human Rights": 8,
    "Hengaw Organization": 8,
    "Iran International": 8,
    "IranIntl": 8,
    "Iran Intl": 8,

    # منابع خبری اسرائیل
    "Israel 14": 8,
    "Israel 14 News": 8,
    "Channel 14": 8,
    "Now 14": 8,
    "חדשות 14": 8,
    "Israel Hayom": 7,
    "Kan News": 7,
    "Channel 12": 7,

    # منابع ورزشی بین‌المللی
    "BBC Sport": 9,
    "BBC Football": 9,
    "ESPN": 8,
    "ESPN Soccer": 9,
    "Gianluca Di Marzio": 8,
    "Transfermarkt": 7,
    "Fabrizio Romano": 9,
    "Fabrizio Romano Telegram": 9,
    "Sky Sports Football": 8,
    "UEFA": 9,
    "FIFA": 9,
    "Premier League": 9,
    "API-Football": 8,

    # منابع ورزشی ایران
    "Varzesh3": 8,
    "Varzesh 3": 8,
    "Varzesh3.com": 8,
    "ورزش سه": 8,
    "Footballi": 7,
    "Tarafdari": 7,
}


DEFAULT_SOURCE_SCORE = 5
