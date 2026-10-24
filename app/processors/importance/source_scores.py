"""
Source Importance Scores
امتیاز اولیه اهمیت منبع برای اولویت‌بندی خبرهای KhabarF24
"""

SOURCE_SCORES = {
    # خبرگزاری‌ها و رسانه‌های بین‌المللی
    "Reuters": 10,
    "Associated Press": 10,
    "AP News": 10,
    "AFP": 10,
    "BBC": 9,
    "BBC Business": 9,
    "BBC Health": 8,
    "BBC Technology": 8,
    "Al Jazeera": 9,
    "France 24": 8,
    "The Guardian": 8,
    "CNN": 8,

    # اقتصاد و بازار جهانی
    "CNBC": 9,
    "CNBC Top News": 9,
    "WSJ Markets": 9,
    "Wall Street Journal": 9,
    "MarketWatch": 8,
    "CoinDesk": 9,
    "Cointelegraph": 8,
    "Decrypt": 7,
    "Investing.com": 8,

    # اقتصاد ایران
    "تجارت‌نیوز": 9,
    "تجارت نیوز": 9,
    "Tejarat News": 9,
    "اقتصاد آنلاین": 9,
    "اقتصادآنلاین": 9,
    "Eghtesad Online": 9,
    "دنیای اقتصاد": 9,
    "Donya-e-Eqtesad": 9,
    "اقتصادنیوز": 9,
    "اقتصاد نیوز": 9,
    "Eghtesad News": 9,
    "خبرگزاری اقتصاد ایران": 8,

    # فناوری
    "The Verge": 9,
    "TechCrunch": 9,
    "Ars Technica": 8,
    "Engadget": 8,
    "WIRED": 8,
    "دیجیاتو": 9,
    "Digiato": 9,
    "ویجیاتو": 7,
    "Vigiato": 7,
    "زومیت": 9,
    "Zoomit": 9,

    # اطلاعیه‌های رسمی
    "CENTCOM": 8,
    "Tesla Newsroom": 7,
}

DEFAULT_SOURCE_SCORE = 5
