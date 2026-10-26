import re

def detect_league(text):
if not text:
return None

text = re.sub(r"\s+", " ", text).casefold()

leagues = {
    "champions_league": [
        "champions league",
        "لیگ قهرمانان اروپا",
    ],
    "europa_league": [
        "europa league",
        "لیگ اروپا",
    ],
    "premier_league": [
        "premier league",
        "لیگ برتر انگلیس",
    ],
    "la_liga": ["la liga", "لالیگا"],
    "serie_a": ["serie a", "سری آ ایتالیا"],
    "bundesliga": ["bundesliga", "بوندسلیگا"],
    "ligue_1": ["ligue 1", "لوشامپیونه"],
    "world_cup": ["world cup", "جام جهانی"],
    "asian_champions_league": [
        "afc champions league",
        "لیگ قهرمانان آسیا",
    ],
    "iran_premier_league": [
        "persian gulf pro league",
        "iran pro league",
        "لیگ برتر ایران",
    ],
}

for league, keywords in leagues.items():
    for keyword in keywords:
        if keyword.casefold() in text:
            return league

return None
