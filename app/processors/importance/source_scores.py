"""
Source Importance Scores
امتیاز اهمیت منابع خبری KhabarF24

امتیاز از 1 تا 10:
10 = بسیار مهم
8-9 = مهم
6-7 = متوسط
5 = مقدار پیش‌فرض
"""

# امتیاز بر اساس شناسه واقعی منبع در data/sources/
SOURCE_ID_SCORES = {
    # خبرگزاری‌های بین‌المللی
    "reuters_google_news": 10,
    "ap_google_news": 10,
    "bbc_world": 10,
    "bbc_top": 10,
    "aljazeera_all": 9,
    "guardian_world": 9,
    "nytimes_world": 9,
    "dw_world": 9,
    "france24_world": 9,
    "france24_middle_east": 9,
    "euronews": 9,
    "sky_news_world": 9,
    "sky_news_home": 8,
    "axios_top": 9,
    "cnn_google_news": 9,
    "fox_news_latest": 8,
    "fox_news_world": 8,
    "wsj_world": 9,
    "washington_post": 9,
    "npr_news": 8,
    "npr_world": 8,
    "nbc_news": 8,
    "cbs_news": 8,
    "abc_news": 8,
    "politico": 8,
    "politico_europe": 8,
    "la_times": 8,
    "independent": 8,
    "cbc_world": 8,
    "abc_australia": 8,
    "times_of_india": 8,
    "scmp_world": 8,
    "ndtv_world": 8,
    "spiegel": 8,
    "economist_world": 9,
    "google_news_world": 7,

    # خاورمیانه و اطلاعیه‌های رسمی
    "al_arabiya": 8,
    "i24news": 8,
    "israel_hayom": 7,
    "israel_14": 7,
    "kan_news": 8,
    "channel_12": 8,
    "times_of_israel": 8,
    "jpost": 8,
    "centcom": 9,

    # ایران
    "iranintl_fa": 9,
    "isna": 9,
    "mehr": 8,
    "khabaronline": 8,
    "tabnak": 8,
    "yjc": 8,
    "irib": 8,
    "fars": 8,
    "hengaw": 8,
    "khabarfouri": 8,

    # فناوری
    "bbc_technology": 9,
    "the_verge": 9,
    "techcrunch": 9,
    "arstechnica": 8,
    "engadget": 8,
    "wired": 8,
    "digiato": 9,
    "vigiato": 7,

    # فوتبال و ورزش
    "fabrizio_romano_telegram": 10,
    "di_marzio": 10,
    "sky_sports_football": 9,
    "bbc_football": 9,
    "bbc_sport": 9,
    "espn_soccer": 9,
    "transfermarkt": 9,
    "marca": 9,
    "manchester_evening_news": 9,
    "as_com_football": 8,
    "varzesh3": 9,
    "tasnim_sport": 8,
    "manutd_official": 8,
    "reuters_sports": 9,
    "uefa": 9,
    "fifa": 9,
    "premier_league": 9,
    "the_athletic_football": 9,
    "realmadrid_official": 8,
    "fcbarcelona_official": 8,

    # اقتصاد
    "cnbc": 9,
    "cnbc_top": 9,
    "wsj_markets": 9,
    "marketwatch": 8,
    "coindesk": 8,
    "cointelegraph": 7,
    "decrypt": 7,
    "investing_com": 8,
}

# امتیاز بر اساس نام منبع؛ برای سازگاری با کدهای قبلی
SOURCE_SCORES = {
    # خبرگزاری‌های بین‌المللی
    "Reuters": 10,
    "Associated Press": 10,
    "AP News": 10,
    "AFP": 10,
    "BBC": 9,
    "BBC World": 10,
    "BBC News": 9,
    "BBC Sport": 9,
    "BBC Football": 9,
    "Al Jazeera": 9,
    "The Guardian": 9,
    "The New York Times": 9,
    "DW": 9,
    "Deutsche Welle": 9,
    "France 24": 9,
    "Euronews": 9,
    "Sky News": 8,
    "CNN": 9,
    "Fox News": 8,
    "The Wall Street Journal": 9,
    "Wall Street Journal": 9,
    "The Washington Post": 9,
    "NPR": 8,
    "NBC News": 8,
    "CBS News": 8,
    "ABC News": 8,
    "Axios": 9,
    "Politico": 8,
    "The Independent": 8,
    "Los Angeles Times": 8,
    "CBC News": 8,
    "South China Morning Post": 8,
    "The Economist": 9,

    # خاورمیانه و منابع رسمی
    "Al Arabiya": 8,
    "i24NEWS": 8,
    "Israel Hayom": 7,
    "Israel 14": 7,
    "KAN News": 8,
    "Channel 12": 8,
    "The Times of Israel": 8,
    "The Jerusalem Post": 8,
    "CENTCOM": 9,

    # ایران
    "Iran International": 9,
    "ISNA": 9,
    "Mehr News": 8,
    "Khabar Online": 8,
    "Tabnak": 8,
    "YJC": 8,
    "IRIB News": 8,
    "Fars News": 8,
    "Hengaw": 8,
    "Khabar Fouri": 8,

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

    # فوتبال و ورزش
    "Fabrizio Romano": 10,
    "Fabrizio Romano Telegram": 10,
    "Gianluca Di Marzio": 10,
    "Di Marzio": 10,
    "Sky Sports": 9,
    "ESPN": 9,
    "ESPN Soccer": 9,
    "Transfermarkt": 9,
    "Marca": 9,
    "Manchester Evening News": 9,
    "AS": 8,
    "Varzesh3": 9,
    "ورزش سه": 9,
    "Tasnim Sport": 8,
    "Manchester United": 8,
    "UEFA": 9,
    "FIFA": 9,
    "Premier League": 9,
    "The Athletic": 9,

    # اقتصاد و بازار جهانی
    "CNBC": 9,
    "CNBC Top News": 9,
    "WSJ Markets": 9,
    "MarketWatch": 8,
    "CoinDesk": 8,
    "Cointelegraph": 7,
    "Decrypt": 7,
    "Investing.com": 8,
    "Tesla Newsroom": 7,
}

DEFAULT_SOURCE_SCORE = 5


def _normalize(value):
    """یکسان‌سازی نام‌ها برای مقایسه."""
    if value is None:
        return ""

    return " ".join(
        str(value)
        .replace("\u200c", "")
        .replace("_", " ")
        .strip()
        .casefold()
        .split()
    )


def get_source_score(source=None, source_id=None, default=None):
    """
    دریافت امتیاز منبع بر اساس شناسه یا نام.

    source می‌تواند رشته، دیکشنری یا شیء NewsSource/RawNews باشد.
    شناسه منبع در اولویت است.
    """

    fallback = (
        DEFAULT_SOURCE_SCORE
        if default is None
        else default
    )

    if isinstance(source, dict):
        source_id = (
            source_id
            or source.get("source_id")
            or source.get("id")
        )
        source_name = (
            source.get("source")
            or source.get("name")
            or source.get("source_name")
            or ""
        )
    elif isinstance(source, str):
        source_name = source
    elif source is not None:
        source_id = (
            source_id
            or getattr(source, "source_id", None)
            or getattr(source, "id", None)
        )
        source_name = (
            getattr(source, "source", None)
            or getattr(source, "name", None)
            or getattr(source, "source_name", None)
            or ""
        )
    else:
        source_name = ""

    if source_id:
        score = SOURCE_ID_SCORES.get(
            _normalize(source_id).replace(" ", "_")
        )
        if score is not None:
            return score

    normalized_name = _normalize(source_name)

    for name, score in SOURCE_SCORES.items():
        if _normalize(name) == normalized_name:
            return score

    return max(1, min(10, int(fallback)))


def calculate_source_score(news=None, source_id=None, default=None):
    """نام جایگزین برای سازگاری با فراخوانی‌های قدیمی."""
    return get_source_score(
        source=news,
        source_id=source_id,
        default=default,
    )
