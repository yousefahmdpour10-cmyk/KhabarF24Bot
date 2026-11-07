"""
Source Importance Scores
امتیاز اهمیت منابع خبری KhabarF24

امتیاز از 1 تا 10:
10 = بسیار مهم
9  = بسیار معتبر / مهم
8  = معتبر
7  = متوسط رو به بالا
6  = متوسط
5  = مقدار پیش‌فرض

نکته:
این امتیاز با Credibility Score که معمولاً در بازه 70 تا 100
محاسبه می‌شود متفاوت است.

SOURCE_ID_SCORES:
    امتیاز بر اساس شناسه واقعی منبع در data/sources/

SOURCE_SCORES:
    امتیاز بر اساس نام منبع برای سازگاری با کدهای قدیمی
"""

# ============================================================
# امتیاز بر اساس شناسه واقعی منبع
# ============================================================

SOURCE_ID_SCORES = {

    # ========================================================
    # INTERNATIONAL / خبرگزاری‌های بین‌المللی
    # ========================================================

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

    # ========================================================
    # روسیه / چین / آسیا / اروپا
    # ========================================================

    "tass": 8,
    "ria_novosti": 8,
    "interfax_russia": 8,
    "rbc_russia": 7,
    "kommersant": 7,

    "xinhua_world": 9,
    "china_daily": 8,
    "cctv_world": 8,

    "kyodo_world": 9,
    "jiji_news": 8,
    "nhk_world": 9,
    "yonhap_world": 9,
    "kbs_world": 8,

    "pti_india": 9,
    "ani_india": 8,
    "the_hindu": 8,

    "anadolu_world": 9,
    "trt_world": 8,

    "ansa_world": 8,
    "efe_world": 8,
    "dpa_world": 9,
    "pap_world": 8,
    "ukrinform": 9,

    # ========================================================
    # خاورمیانه / منابع رسمی
    # ========================================================

    "al_arabiya": 8,
    "i24news": 8,

    "israel_hayom": 7,
    "israel_14": 7,
    "kan_news": 8,
    "channel_12": 8,

    "times_of_israel": 8,
    "jpost": 8,

    "centcom": 9,

    "spa_saudi": 9,
    "arab_news": 8,
    "qna_world": 9,

    # ========================================================
    # ایران
    # ========================================================

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
    "asriran": 8,

    "iranintl_fa": 9,
    "hengaw": 8,
    "khabarfouri": 7,

    "mashregh": 7,
    "alef": 7,
    "entekhab": 8,
    "borna": 7,
    "mizan": 7,
    "snn": 7,
    "defapress": 7,
    "icana": 8,

    "fararu": 8,
    "hamshahrionline": 8,
    "nournews": 8,
    "iqna": 7,
    "shabestan": 6,

    "ana": 7,
    "qudsonline": 7,
    "javanonline": 7,
    "aftabnews": 7,

    "ettelaat": 8,
    "jamejam": 7,
    "dana": 6,

    "kayhan": 7,
    "shargh": 8,
    "etemadonline": 7,

    "jomhouri_eslami": 7,
    "resalat": 7,
    "siasatrooz": 6,
    "khorasannews": 7,
    "vatanemrooz": 7,
    "ebtekar": 7,
    "farhikhtegan": 7,
    "jahannews": 7,
    "parsine": 7,
    "serat": 6,
    "mojnews": 7,
    "imna": 6,

    # ========================================================
    # ECONOMY / اقتصاد جهانی
    # ========================================================

    "bbc_business": 9,

    "wsj_markets": 9,
    "wsj_business": 9,

    "cnbc_top_news": 9,
    "cnbc_business": 9,

    "marketwatch_top": 8,

    "bloomberg_markets": 10,
    "bloomberg_economics": 10,

    "financial_times": 10,
    "economist_finance": 9,

    "fortune": 8,
    "business_insider": 8,
    "hbr": 8,

    "investing_com": 8,

    # ========================================================
    # CRYPTO
    # ========================================================

    "coindesk": 8,
    "cointelegraph": 7,
    "decrypt": 7,

    # ========================================================
    # ECONOMY / اقتصاد ایران
    # ========================================================

    "tejaratnews": 9,
    "eghtesadonline": 9,
    "donya_e_eqtesad": 9,
    "eghtesadnews": 8,
    "ecoiran": 8,
    "ibena": 8,
    "boursepress": 7,
    "tejarat_farda": 8,
    "eghtesad24": 7,
    "poolnews": 6,
    "gostaresh": 6,
    "iran_economy": 6,

    # ========================================================
    # شرکت‌ها / منابع رسمی اقتصادی
    # ========================================================

    "tesla_newsroom": 7,

    # ========================================================
    # HEALTH / سلامت
    # ========================================================

    "bbc_health": 9,
    "stat": 10,
    "kff_health": 9,
    "npr_health": 8,
    "guardian_health": 9,
    "nytimes_health": 9,

    "sciencedaily_health": 8,

    "who_news": 10,
    "who_disease_outbreaks": 10,

    "fda_medwatch": 10,
    "fda_news": 9,

    "cdc_mmwr": 10,
    "niehs": 9,

    "psychology_today": 7,

    # ========================================================
    # SPORTS / ورزش
    # ========================================================

    "bbc_sport": 9,
    "bbc_football": 9,
    "bbc_premier_league": 9,

    "espn_soccer": 9,
    "espn_sports": 9,

    "sky_sports_football": 9,
    "sky_sports": 9,

    "the_athletic": 9,
    "the_athletic_football": 9,

    "guardian_football": 9,
    "guardian_sport": 9,

    "marca": 9,
    "as_com_football": 8,

    "football_italia": 8,
    "goal_football": 8,
    "talksport": 8,

    # ========================================================
    # FOOTBALL TRANSFERS
    # ========================================================

    "di_marzio": 10,
    "fabrizio_romano_telegram": 10,
    "transfermarkt": 9,

    "manchester_evening_news": 9,

    "cbs_sports": 8,
    "yahoo_sports": 8,

    # ========================================================
    # MOTORSPORT
    # ========================================================

    "formula1": 9,
    "autosport": 9,

    # ========================================================
    # OTHER SPORTS
    # ========================================================

    "mlb": 8,
    "espncricinfo": 8,
    "ufc": 8,

    # ========================================================
    # OFFICIAL FOOTBALL ORGANIZATIONS
    # ========================================================

    "uefa": 10,
    "fifa": 10,
    "premier_league": 10,

    "manutd_official": 8,
    "realmadrid_official": 8,
    "fcbarcelona_official": 8,

    # ========================================================
    # IRAN FOOTBALL
    # ========================================================

    "varzesh3": 9,
    "tasnim_sport": 8,

    # ========================================================
    # TECHNOLOGY
    # ========================================================

    "bbc_technology": 9,
    "the_verge": 9,
    "techcrunch": 9,
    "arstechnica": 8,

    "engadget": 8,
    "wired": 9,

    "mit_technology_review": 10,

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

    # ========================================================
    # CYBERSECURITY
    # ========================================================

    "the_hacker_news": 9,
    "bleepingcomputer": 9,
    "hacker_news": 7,

    # ========================================================
    # AI
    # ========================================================

    "google_ai": 9,
    "openai": 9,

    # ========================================================
    # IRAN TECHNOLOGY
    # ========================================================

    "digiato": 9,
    "zoomit": 9,
    "vigiato": 7,

    # ========================================================
    # WEATHER
    # ========================================================

    "open_meteo": 9,

    "irimo_fa": 10,
    "irimo_en": 9,

    "bbc_weather": 9,

    "noaa_weather": 10,
    "noaa_nws": 10,
    "metoffice": 9,
    "noaa_hurricane": 10,
}


# ============================================================
# امتیاز بر اساس نام منبع
# برای سازگاری با کدهای قدیمی
# ============================================================

SOURCE_SCORES = {

    # ========================================================
    # International
    # ========================================================

    "Reuters": 10,
    "Associated Press": 10,
    "AP News": 10,
    "AFP": 10,

    "BBC": 9,
    "BBC World": 10,
    "BBC News": 9,
    "BBC Top Stories": 10,

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
    "The Hill": 8,

    "The Independent": 8,
    "Los Angeles Times": 8,
    "CBC News": 8,
    "ABC News Australia": 8,

    "Times of India": 8,
    "South China Morning Post": 8,
    "NDTV": 8,

    "Der Spiegel": 8,
    "The Economist": 9,

    "Google News": 7,

    # ========================================================
    # International / Regional
    # ========================================================

    "TASS": 8,
    "RIA Novosti": 8,
    "Interfax": 8,
    "RBC": 7,
    "Kommersant": 7,

    "Xinhua": 9,
    "China Daily": 8,
    "CCTV": 8,

    "Kyodo News": 9,
    "Jiji Press": 8,
    "NHK World": 9,
    "Yonhap": 9,
    "KBS News": 8,

    "Press Trust of India": 9,
    "ANI": 8,
    "The Hindu": 8,

    "Anadolu Agency": 9,
    "TRT World": 8,

    "ANSA": 8,
    "EFE": 8,
    "dpa": 9,
    "Polish Press Agency": 8,
    "Ukrinform": 9,

    # ========================================================
    # Middle East
    # ========================================================

    "Al Arabiya": 8,
    "i24NEWS": 8,
    "Israel Hayom": 7,
    "Israel 14": 7,
    "KAN News": 8,
    "Channel 12": 8,
    "The Times of Israel": 8,
    "The Jerusalem Post": 8,
    "CENTCOM": 9,

    "Saudi Press Agency": 9,
    "Arab News": 8,
    "Qatar News Agency": 9,

    # ========================================================
    # Iran
    # ========================================================

    "IRNA": 9,
    "ISNA": 9,
    "Tasnim": 8,
    "Fars News": 8,
    "Mehr News": 8,
    "ILNA": 8,
    "YJC": 8,
    "IRIB News": 8,
    "Khabar Online": 8,
    "Tabnak": 8,
    "Asriran": 8,

    "Iran International": 9,
    "Hengaw": 8,
    "Khabar Fouri": 7,

    "Mashregh News": 7,
    "Alef": 7,
    "Entekhab": 8,
    "Borna News": 7,
    "Mizan Online": 7,
    "SNN": 7,
    "Defa Press": 7,
    "ICANA": 8,

    "Fararu": 8,
    "Hamshahri Online": 8,
    "Nour News": 8,
    "IQNA": 7,
    "Shabestan": 6,

    "ANA": 7,
    "Quds Online": 7,
    "Javan Online": 7,
    "Aftab News": 7,

    "Ettelaat": 8,
    "Jame Jam": 7,
    "Dana": 6,

    "Kayhan": 7,
    "Shargh": 8,
    "Etemad Online": 7,

    "Jomhouri Eslami": 7,
    "Resalat": 7,
    "Siasat Rooz": 6,
    "Khorasan News": 7,
    "Vatan Emrooz": 7,
    "Ebtekar": 7,
    "Farhikhtegan": 7,
    "Jahan News": 7,
    "Parsine": 7,
    "Serat News": 6,
    "Moj News": 7,
    "IMNA": 6,

    # ========================================================
    # Economy
    # ========================================================

    "BBC Business": 9,
    "WSJ Markets": 9,
    "WSJ Business": 9,

    "CNBC": 9,
    "CNBC Top News": 9,
    "CNBC Business": 9,

    "MarketWatch": 8,

    "Bloomberg": 10,
    "Bloomberg Markets": 10,
    "Bloomberg Economics": 10,

    "Financial Times": 10,
    "The Economist Finance": 9,

    "Fortune": 8,
    "Business Insider": 8,
    "Harvard Business Review": 8,

    "Investing.com": 8,

    "CoinDesk": 8,
    "Cointelegraph": 7,
    "Decrypt": 7,

    # ========================================================
    # Iran Economy
    # ========================================================

    "تجارت‌نیوز": 9,
    "تجارت نیوز": 9,
    "Tejarat News": 9,

    "اقتصاد آنلاین": 9,
    "اقتصادآنلاین": 9,
    "Eghtesad Online": 9,

    "دنیای اقتصاد": 9,
    "Donya-e-Eqtesad": 9,

    "اقتصادنیوز": 8,
    "اقتصاد نیوز": 8,
    "Eghtesad News": 8,

    "اکوایران": 8,
    "EcoIran": 8,

    "ایبِنا": 8,
    "IBENA": 8,

    "بورس پرس": 7,
    "تجارت فردا": 8,
    "اقتصاد24": 7,
    "پول نیوز": 6,
    "گسترش نیوز": 6,
    "ایران اکونومیست": 6,

    # ========================================================
    # Technology
    # ========================================================

    "The Verge": 9,
    "TechCrunch": 9,
    "Ars Technica": 8,
    "Engadget": 8,
    "WIRED": 9,

    "MIT Technology Review": 10,

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

    "The Hacker News": 9,
    "BleepingComputer": 9,
    "Hacker News": 7,

    "Google AI": 9,
    "OpenAI": 9,

    "دیجیاتو": 9,
    "Digiato": 9,
    "زومیت": 9,
    "Zoomit": 9,
    "ویجیاتو": 7,
    "Vigiato": 7,

    # ========================================================
    # Health
    # ========================================================

    "BBC Health": 9,
    "STAT": 10,
    "KFF Health News": 9,
    "NPR Health": 8,

    "The Guardian Health": 9,
    "The New York Times Health": 9,

    "ScienceDaily Health": 8,

    "World Health Organization": 10,
    "WHO": 10,
    "WHO Disease Outbreak News": 10,

    "FDA MedWatch": 10,
    "FDA News": 9,

    "CDC MMWR": 10,
    "National Institute of Environmental Health Sciences": 9,

    "Psychology Today": 7,

    # ========================================================
    # Sports
    # ========================================================

    "Fabrizio Romano": 10,
    "Fabrizio Romano Telegram": 10,

    "Gianluca Di Marzio": 10,
    "Di Marzio": 10,

    "Sky Sports": 9,
    "Sky Sports Football": 9,

    "ESPN": 9,
    "ESPN Soccer": 9,

    "BBC Sport": 9,
    "BBC Football": 9,
    "BBC Premier League": 9,

    "Transfermarkt": 9,
    "Marca": 9,

    "Manchester Evening News": 9,

    "AS": 8,
    "AS.com Football": 8,

    "The Athletic": 9,
    "The Athletic Football": 9,

    "The Guardian Football": 9,
    "The Guardian Sport": 9,

    "Football Italia": 8,
    "GOAL": 8,
    "talkSPORT": 8,

    "CBS Sports": 8,
    "Yahoo Sports": 8,

    "Formula 1": 9,
    "Autosport": 9,

    "MLB": 8,
    "ESPNcricinfo": 8,
    "UFC": 8,

    "UEFA": 10,
    "FIFA": 10,
    "Premier League": 10,

    "Manchester United": 8,
    "Manchester United Official": 8,

    "Real Madrid Official": 8,
    "FC Barcelona Official": 8,

    "Varzesh3": 9,
    "ورزش سه": 9,

    "Tasnim Sport": 8,

    # ========================================================
    # Weather
    # ========================================================

    "Open-Meteo": 9,

    "Iran Meteorological Organization": 10,
    "IRIMO": 10,

    "BBC Weather": 9,

    "NOAA Weather": 10,
    "National Weather Service": 10,
    "NWS": 10,

    "Met Office": 9,
    "NOAA Hurricane Center": 10,

    # ========================================================
    # Misc / existing compatibility
    # ========================================================

    "Tesla Newsroom": 7,
}


# ============================================================
# مقدار پیش‌فرض
# ============================================================

DEFAULT_SOURCE_SCORE = 5


# ============================================================
# نرمال‌سازی
# ============================================================

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


# ============================================================
# دریافت امتیاز منبع
# ============================================================

def get_source_score(source=None, source_id=None, default=None):
    """
    دریافت امتیاز منبع بر اساس شناسه یا نام.

    source می‌تواند:
        - رشته
        - دیکشنری
        - NewsSource
        - RawNews

    باشد.

    اولویت تشخیص:

    1. source_id
    2. نام منبع
    3. مقدار پیش‌فرض
    """

    fallback = (
        DEFAULT_SOURCE_SCORE
        if default is None
        else default
    )

    source_name = ""

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # String
    # --------------------------------------------------------

    elif isinstance(source, str):

        source_name = source

    # --------------------------------------------------------
    # Object / NewsSource / RawNews
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Source ID
    # --------------------------------------------------------

    if source_id:

        normalized_source_id = (
            _normalize(source_id)
            .replace(" ", "_")
        )

        score = SOURCE_ID_SCORES.get(
            normalized_source_id
        )

        if score is not None:
            return score

    # --------------------------------------------------------
    # Source name
    # --------------------------------------------------------

    normalized_name = _normalize(source_name)

    if normalized_name:

        for name, score in SOURCE_SCORES.items():

            if _normalize(name) == normalized_name:
                return score

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return max(
        1,
        min(10, int(fallback))
    )


# ============================================================
# Compatibility wrapper
# ============================================================

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
