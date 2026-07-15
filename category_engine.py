"""
category_engine.py

KhabarF24 Smart Category Engine v5
"""

# -----------------------------
# دسته پیش فرض هر منبع
# -----------------------------

SOURCE_CATEGORY = {

    # World
    "Al Jazeera": "world",
    "BBC": "world",
    "BBC News": "world",
    "Reuters": "world",
    "CNN": "world",
    "Associated Press": "world",
    "AP": "world",
    "New York Times": "world",
    "NYTimes": "world",
    "The Guardian": "world",
    "France24": "world",
    "DW": "world",
    "Arab News": "world",
    "العربية": "world",

    # Sport
    "ESPN": "sport",
    "Sky Sports": "sport",
    "FIFA": "sport",
    "UEFA": "sport",
    "The Athletic": "sport",
    "Fabrizio Romano": "sport",
    "Di Marzio": "sport",
    "Bundesliga": "sport",
    "Premier League": "sport",
    "LaLiga": "sport",
    "Serie A": "sport",

    # Technology
    "TechCrunch": "technology",
    "The Verge": "technology",
    "Ars Technica": "technology",
    "Wired": "technology",

    # Economy
    "Bloomberg": "economy",
    "CoinDesk": "economy",
    "Financial Times": "economy",

    # Iran
    "Tasnim": "iran",
    "Fars": "iran",
    "ISNA": "iran",
    "خبر فوری": "iran",

}


SPORT = [

    "football",
    "soccer",
    "fifa",
    "uefa",
    "afc",
    "premier league",
    "champions league",
    "laliga",
    "serie a",
    "bundesliga",

    "manchester united",
    "manchester city",
    "real madrid",
    "barcelona",
    "liverpool",
    "arsenal",
    "chelsea",

    "messi",
    "ronaldo",
    "mbappe",
    "yamal",

    "basketball",
    "nba",
    "wnba",

    "tennis",
    "atp",
    "wta",

    "والیبال",
    "بسکتبال",
    "فوتبال",
    "کشتی",
    "جام جهانی",
    "لیگ",
    "نیمه نهایی",
    "فینال",

]

TECH = [

    "technology",
    "tech",
    "artificial intelligence",
    "openai",
    "google",
    "apple",
    "microsoft",
    "tesla",
    "robot",
    "software",
    "chip",

    "هوش مصنوعی",
    "فناوری",
    "ربات",

]

ECONOMY = [

    "economy",
    "market",
    "stock",
    "bitcoin",
    "crypto",
    "bank",
    "finance",

    "اقتصاد",
    "بورس",
    "دلار",
    "طلا",

]

HEALTH = [

    "health",
    "medicine",
    "medical",
    "hospital",
    "virus",

    "سلامت",
    "پزشکی",
    "بیماری",
    "واکسن",

]

IRAN = [

    "iran",
    "tehran",

    "ایران",
    "تهران",

]

WORLD = [

    "war",
    "attack",
    "missile",
    "strike",
    "trump",
    "biden",
    "israel",
    "russia",
    "ukraine",
    "china",

    "جنگ",
    "حمله",
    "موشک",
    "سپاه",
    "تحریم",
    "ترامپ",
    "آمریکا",
    "اسرائیل",

]


def score(words, text):

    s = 0

    for w in words:

        if w.lower() in text:

            s += 1

    return s


def detect_smart_category(title="", summary="", source=""):

    text = f"{title} {summary}".lower()

    # -----------------------
    # دسته پیش فرض منبع
    # -----------------------

    default = "world"

    for name, cat in SOURCE_CATEGORY.items():

        if name.lower() in source.lower():

            default = cat

            break

    # -----------------------
    # امتیازها
    # -----------------------

    sport_score = score(SPORT, text)
    tech_score = score(TECH, text)
    eco_score = score(ECONOMY, text)
    health_score = score(HEALTH, text)
    iran_score = score(IRAN, text)
    world_score = score(WORLD, text)

    # -----------------------
    # قوانین
    # -----------------------

    # خبر جنگ همیشه جهان
    if world_score >= 2:
        return "world"

    # ورزش فقط اگر واقعا ورزشی باشد
    if sport_score >= 3:
        return "sport"

    if tech_score >= 2:
        return "technology"

    if eco_score >= 2:
        return "economy"

    if health_score >= 2:
        return "health"

    if iran_score >= 2 and default != "world":
        return "iran"

    return default
