"""
Source Importance Scores
امتیاز اهمیت منابع خبری KhabarF24

امتیاز از 1 تا 10:
10 = بسیار مهم
8-9 = مهم
6-7 = متوسط
5 = مقدار پیش‌فرض

منابع شناخته‌شده با SOURCE_ID_SCORES امتیاز دقیق می‌گیرند.
برای منابع جدیدی که هنوز در این جدول نیستند، priority منبع
در data/sources/*.json به امتیاز 1 تا 10 تبدیل می‌شود.
"""

# ============================================================
# امتیاز بر اساس شناسه واقعی منبع در data/sources/
# ============================================================

SOURCE_ID_SCORES = {

    # --------------------------------------------------------
    # خبرگزاری‌های بین‌المللی
    # --------------------------------------------------------
    "reuters_google_news": 10,
    "ap_google_news": 10,
    "afp_google_news": 10,

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

    "the_hill": 8,
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

    # --------------------------------------------------------
    # خاورمیانه و منابع رسمی
    # --------------------------------------------------------
    "al_arabiya": 8,
    "i24news": 8,

    "israel_hayom": 7,
    "israel_14": 7,

    "kan_news": 8,
    "channel_12": 8,

    "times_of_israel": 8,
    "jpost": 8,

    "centcom": 9,

    # --------------------------------------------------------
    # روسیه / چین / آسیا / اروپا
    # --------------------------------------------------------
    "tass": 7,
    "ria_novosti": 7,
    "interfax_russia": 7,
    "rbc_russia": 7,
    "kommersant": 7,

    "xinhua_world": 7,
    "china_daily": 7,
    "cctv_world": 7,

    "kyodo_world": 8,
    "jiji_news": 8,
    "nhk_world": 8,

    "yonhap_world": 8,
    "kbs_world": 8,

    "pti_india": 8,
    "ani_india": 8,
    "the_hindu": 8,

    "anadolu_world": 8,
    "trt_world": 8,

    "ansa_world": 8,
    "efe_world": 8,
    "dpa_world": 8,
    "pap_world": 7,

    "ukrinform": 8,

    "spa_saudi": 8,
    "arab_news": 8,
    "qna_world": 8,

    # --------------------------------------------------------
    # ایران
    # --------------------------------------------------------
    "irna": 9,
    "isna": 9,
    "tasnim": 8,
    "fars": 8,
    "mehr": 8,
    "ilna": 8,

    "yjc": 8,
    "irib": 8,

    "khabaronline": 8,
    "tabnak": 8,

    "asriran": 7,
    "iranintl_fa": 9,

    "hengaw": 8,
    "khabarfouri": 8,

    "mashregh": 7,
    "alef": 7,
    "entekhab": 8,

    "borna": 7,
    "mizan": 8,
    "snn": 7,

    "defapress": 8,
    "icana": 8,

    "fararu": 7,
    "hamshahrionline": 7,

    "nournews": 7,
    "iqna": 7,
    "shabestan": 7,

    # --------------------------------------------------------
    # فوتبال و ورزش
    # --------------------------------------------------------
    "fabrizio_romano_telegram": 10,
    "di_marzio": 10,

    "sky_sports_football": 9,
    "sky_sports": 9,

    "bbc_football": 9,
    "bbc_sport": 9,
    "bbc_premier_league": 9,

    "espn_soccer": 9,
    "espn_sports": 9,

    "the_athletic": 9,
    "the_athletic_football": 9,

    "guardian_football": 9,
    "guardian_sport": 8,

    "transfermarkt": 9,
    "marca": 9,
    "as_com_football": 8,

    "football_italia": 8,
    "goal_football": 8,
    "talksport": 8,

    "manchester_evening_news": 9,

    "cbs_sports": 8,
    "yahoo_sports": 8,

    "formula1": 8,
    "autosport": 8,
    "mlb": 8,
    "espncricinfo": 8,
    "ufc": 8,

    "uefa": 9,
    "fifa": 9,
    "premier_league": 9,

    "manutd_official": 8,
    "realmadrid_official": 8,
    "fcbarcelona_official": 8,

    "varzesh3": 9,
    "tasnim_sport": 8,

    # --------------------------------------------------------
    # فناوری
    # --------------------------------------------------------
    "bbc_technology": 9,
    "the_verge": 9,
    "techcrunch": 9,

    "arstechnica": 8,
    "engadget": 8,
    "wired": 8,

    "mit_technology_review": 9,
    "cnet": 8,
    "zdnet": 8,
    "techradar": 8,

    "android_authority": 8,
    "9to5google": 8,
    "9to5mac": 8,

    "toms_hardware": 8,
    "the_register": 8,

    "venturebeat": 8,
    "siliconangle": 7,

    "the_hacker_news": 8,
    "bleepingcomputer": 8,
    "hacker_news": 8,

    "google_ai": 9,
    "openai": 9,

    "digiato": 9,
    "zoomit": 9,
    "vigiato": 7,

    # --------------------------------------------------------
    # اقتصاد و بازار
    # --------------------------------------------------------
    "cnbc": 9,
    "cnbc_top": 9,

    "wsj_markets": 9,
    "marketwatch": 8,

    "coindesk": 8,
    "cointelegraph": 7,
    "decrypt": 7,

    "investing_com": 8,

    "tejaratnews": 9,
    "eghtesadonline": 9,
    "donya_eqtesad": 9,
    "eghtesadnews": 9,
    "eghtesad_iran": 8,

    # --------------------------------------------------------
    # آب‌وهوا
    # --------------------------------------------------------
    "open_meteo": 9,
    "irimo_fa": 9,
    "irimo_en": 9,

    "bbc_weather": 9,
    "noaa_weather": 9,
    "noaa_nws": 9,
    "metoffice": 9,
    "noaa_hurricane": 9,
}


# ============================================================
# امتیاز بر اساس نام منبع
# برای سازگاری با کدهای قدیمی
# ============================================================

SOURCE_SCORES = {

    # --------------------------------------------------------
    # خبرگزاری‌های بین‌المللی
    # --------------------------------------------------------
    "Reuters": 10,
    "Associated Press": 10,
    "AP": 10,
    "AP News": 10,
    "AFP": 10,

    "BBC": 10,
    "BBC World": 10,
    "BBC News": 9,
    "BBC Top Stories": 10,
    "BBC Sport": 9,
    "BBC Football": 9,
    "BBC Business": 9,
    "BBC Technology": 9,
    "BBC Weather": 9,

    "Al Jazeera": 9,
    "The Guardian": 9,
    "The Guardian World": 9,
    "The Guardian Football": 9,
    "The New York Times": 9,
    "DW": 9,
    "Deutsche Welle": 9,
    "France 24": 9,
    "Euronews": 9,

    "Sky News": 8,
    "Sky News World": 9,
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
    "The Hill": 8,
    "The Independent": 8,
    "Los Angeles Times": 8,
    "CBC News": 8,

    "South China Morning Post": 8,
    "The Economist": 9,

    # --------------------------------------------------------
    # خاورمیانه و منابع رسمی
    # --------------------------------------------------------
    "Al Arabiya": 8,
    "i24NEWS": 8,
    "Israel Hayom": 7,
    "Israel 14": 7,
    "KAN News": 8,
    "Channel 12": 8,
    "The Times of Israel": 8,
    "The Jerusalem Post": 8,
    "CENTCOM": 9,

    # --------------------------------------------------------
    # ایران
    # --------------------------------------------------------
    "IRNA": 9,
    "ISNA": 9,
    "Tasnim": 8,
    "Tasnim News": 8,
    "Mehr News": 8,
    "Fars": 8,
    "Fars News": 8,

    "ILNA": 8,
    "Khabar Online": 8,
    "Tabnak": 8,
    "YJC": 8,
    "IRIB": 8,
    "IRIB News": 8,

    "Asr Iran": 7,
    "Iran International": 9,
    "IranIntl": 9,

    "Hengaw": 8,
    "Hengaw News": 8,
    "Khabar Fouri": 8,
    "Khabar Fouri": 8,

    "Mashregh": 7,
    "Alef": 7,
    "Entekhab": 8,
    "Borna": 7,
    "Mizan": 8,
    "SNN": 7,
    "Defa Press": 8,
    "ICANA": 8,
    "Fararu": 7,
    "Hamshahrionline": 7,
    "Nour News": 7,
    "IQNA": 7,
    "Shabestan": 7,

    # --------------------------------------------------------
    # اقتصاد ایران
    # --------------------------------------------------------
    "تجارت‌نیوز": 9,
    "تجارت نیوز": 9,
    "Tejarat News": 9,
    "Tejaratnews": 9,

    "اقتصاد آنلاین": 9,
    "اقتصادآنلاین": 9,
    "Eghtesad Online": 9,
    "Eghtesadonline": 9,

    "دنیای اقتصاد": 9,
    "Donya-e-Eqtesad": 9,
    "Donya Eqtesad": 9,

    "اقتصادنیوز": 9,
    "اقتصاد نیوز": 9,
    "Eghtesad News": 9,
    "Eghtesadnews": 9,

    "خبرگزاری اقتصاد ایران": 8,
    "Eghtesad Iran": 8,

    # --------------------------------------------------------
    # فناوری
    # --------------------------------------------------------
    "The Verge": 9,
    "TechCrunch": 9,
    "Ars Technica": 8,
    "Engadget": 8,
    "WIRED": 8,
    "MIT Technology Review": 9,
    "CNET": 8,
    "ZDNET": 8,
    "TechRadar": 8,

    "Android Authority": 8,
    "9to5Google": 8,
    "9to5Mac": 8,
    "Tom's Hardware": 8,
    "The Register": 8,

    "VentureBeat": 8,
    "SiliconANGLE": 7,
    "The Hacker News": 8,
    "BleepingComputer": 8,
    "Hacker News": 8,

    "Google AI": 9,
    "OpenAI": 9,

    "دیجیاتو": 9,
    "Digiato": 9,
    "زومیت": 9,
    "Zoomit": 9,
    "ویجیاتو": 7,
    "Vigiato": 7,

    # --------------------------------------------------------
    # فوتبال و ورزش
    # --------------------------------------------------------
    "Fabrizio Romano": 10,
    "Fabrizio Romano Telegram": 10,

    "Gianluca Di Marzio": 10,
    "Di Marzio": 10,

    "Sky Sports": 9,
    "Sky Sports Football": 9,

    "ESPN": 9,
    "ESPN Soccer": 9,

    "Transfermarkt": 9,
    "Marca": 9,
    "AS": 8,

    "Manchester Evening News": 9,

    "Varzesh3": 9,
    "ورزش سه": 9,
    "Tasnim Sport": 8,

    "Manchester United": 8,
    "UEFA": 9,
    "FIFA": 9,
    "Premier League": 9,

    "The Athletic": 9,
    "The Athletic Football": 9,

    "Real Madrid": 8,
    "Real Madrid Official": 8,
    "FC Barcelona": 8,
    "FC Barcelona Official": 8,

    # --------------------------------------------------------
    # اقتصاد و بازار جهانی
    # --------------------------------------------------------
    "CNBC": 9,
    "CNBC Top News": 9,
    "WSJ Markets": 9,
    "MarketWatch": 8,

    "CoinDesk": 8,
    "Cointelegraph": 7,
    "Decrypt": 7,
    "Investing.com": 8,

    # --------------------------------------------------------
    # آب‌وهوا
    # --------------------------------------------------------
    "Open-Meteo": 9,
    "IRIMO": 9,
    "Iran Meteorological Organization": 9,
    "BBC Weather": 9,
    "NOAA": 9,
    "NOAA Weather": 9,
    "NOAA NWS": 9,
    "Met Office": 9,
}


# ============================================================
# مقدار پیش‌فرض
# ============================================================

DEFAULT_SOURCE_SCORE = 5


# ============================================================
# تبدیل priority به source score
# ============================================================

def _priority_to_score(priority):
    """
    تبدیل priority منبع به امتیاز اهمیت 1 تا 10.

    priority معمولاً در data/sources/*.json بین 0 تا 100 است.
    """

    try:
        priority = int(priority)
    except (TypeError, ValueError):
        return DEFAULT_SOURCE_SCORE

    if priority >= 95:
        return 10

    if priority >= 90:
        return 9

    if priority >= 85:
        return 8

    if priority >= 80:
        return 7

    if priority >= 75:
        return 6

    if priority >= 70:
        return 5

    if priority >= 60:
        return 4

    if priority >= 50:
        return 3

    if priority >= 40:
        return 2

    return 1


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


def _extract_source_values(source):
    """
    استخراج source_id، نام منبع و priority
    از dict یا شیء NewsSource/RawNews.
    """

    source_id = None
    source_name = ""
    priority = None

    if isinstance(source, dict):

        source_id = (
            source.get("source_id")
            or source.get("id")
        )

        source_name = (
            source.get("source")
            or source.get("name")
            or source.get("source_name")
            or ""
        )

        priority = source.get("priority")

    elif isinstance(source, str):

        source_name = source

    elif source is not None:

        source_id = (
            getattr(source, "source_id", None)
            or getattr(source, "id", None)
        )

        source_name = (
            getattr(source, "source", None)
            or getattr(source, "name", None)
            or getattr(source, "source_name", None)
            or ""
        )

        priority = getattr(source, "priority", None)

    return source_id, source_name, priority


def _get_score_from_source_files(source_id):
    """
    در صورت ناشناخته بودن source_id، priority منبع را
    مستقیماً از data/sources/*.json دریافت می‌کند.

    این بخش باعث می‌شود منابع جدید بدون ثبت دستی هم
    امتیاز مناسب بگیرند.
    """

    if not source_id:
        return None

    try:
        from config.sources import load_sources

        normalized_id = _normalize(source_id).replace(" ", "_")

        for source in load_sources():

            current_id = getattr(source, "id", None)

            if not current_id:
                continue

            current_id = _normalize(current_id).replace(
                " ",
                "_",
            )

            if current_id == normalized_id:

                priority = getattr(
                    source,
                    "priority",
                    None,
                )

                if priority is not None:
                    return _priority_to_score(priority)

    except Exception:
        pass

    return None


def get_source_score(
    source=None,
    source_id=None,
    default=None,
):
    """
    دریافت امتیاز اهمیت منبع.

    ترتیب اولویت:

    1. SOURCE_ID_SCORES
    2. SOURCE_SCORES بر اساس نام
    3. priority منبع در data/sources/*.json
    4. مقدار پیش‌فرض
    """

    fallback = (
        DEFAULT_SOURCE_SCORE
        if default is None
        else default
    )

    extracted_id, source_name, priority = (
        _extract_source_values(source)
    )

    source_id = source_id or extracted_id

    # --------------------------------------------------------
    # 1. شناسه منبع
    # --------------------------------------------------------

    if source_id:

        normalized_id = (
            _normalize(source_id)
            .replace(" ", "_")
        )

        score = SOURCE_ID_SCORES.get(
            normalized_id
        )

        if score is not None:
            return score

    # --------------------------------------------------------
    # 2. نام منبع
    # --------------------------------------------------------

    normalized_name = _normalize(
        source_name
    )

    if normalized_name:

        for name, score in SOURCE_SCORES.items():

            if _normalize(name) == normalized_name:
                return score

    # --------------------------------------------------------
    # 3. priority خود آبجکت
    # --------------------------------------------------------

    if priority is not None:
        return _priority_to_score(priority)

    # --------------------------------------------------------
    # 4. priority از فایل‌های source
    # --------------------------------------------------------

    score = _get_score_from_source_files(
        source_id
    )

    if score is not None:
        return score

    # --------------------------------------------------------
    # 5. fallback
    # --------------------------------------------------------

    return max(
        1,
        min(
            10,
            int(fallback),
        ),
    )


def calculate_source_score(
    news=None,
    source_id=None,
    default=None,
):
    """
    نام جایگزین برای سازگاری با فراخوانی‌های قدیمی.
    """

    return get_source_score(
        source=news,
        source_id=source_id,
        default=default,
    )
