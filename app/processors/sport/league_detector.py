"""
League Detector

تشخیص مسابقه (لیگ یا جام) از متن خبر، برای هشتگ مسابقات.
اسم‌های این فایل باید با کلیدهای LEAGUE_TAGS در app/formatter/hashtags.py
(به‌صورت حروف کوچک) یکی باشد.
"""

from typing import Optional

from app.utils.text_matching import keyword_in_text

# ترتیب مهم است: اولین مسابقه‌ای که پیدا شود برنده است. پس مسابقه‌های
# خاص‌تر (مثل AFC Champions League) باید قبل از مسابقه‌ی عمومی‌تر
# (Champions League) بیایند، و جام‌های قاره‌ای قبل از لیگ‌های داخلی.
LEAGUE_KEYWORDS = {
    "AFC Champions League": [
        "afc champions league", "لیگ قهرمانان آسیا",
    ],
    "Club World Cup": [
        "club world cup", "جام باشگاه‌های جهان", "جام باشگاههای جهان",
    ],
    "Champions League": [
        "champions league", "لیگ قهرمانان",
    ],
    "Europa League": [
        "europa league", "لیگ اروپا",
    ],
    "Conference League": [
        "conference league", "کنفرانس لیگ",
    ],
    "Nations League": [
        "nations league", "لیگ ملت‌ها", "لیگ ملتها",
    ],
    "World Cup": [
        "world cup", "جام جهانی",
    ],
    "Asian Cup": [
        "asian cup", "جام ملت‌های آسیا", "جام ملتهای آسیا",
    ],
    "Premier League": [
        "premier league", "لیگ برتر انگلیس", "پریمیرلیگ",
    ],
    "La Liga": [
        "la liga", "laliga", "لالیگا",
    ],
    "Serie A": [
        "serie a", "سری آ",
    ],
    "Bundesliga": [
        "bundesliga", "بوندسلیگا",
    ],
    "Ligue 1": [
        "ligue 1", "لوشامپیونه",
    ],
    "FA Cup": [
        "fa cup", "جام حذفی انگلیس",
    ],
    "Carabao Cup": [
        "carabao cup", "efl cup",
    ],
    "Copa del Rey": [
        "copa del rey", "کوپا دل ری",
    ],
    "Persian Gulf Pro League": [
        "persian gulf pro league", "لیگ برتر خلیج فارس",
    ],
    "NBA": [
        "nba",
    ],
    "EuroLeague": [
        "euroleague",
    ],
    "Wimbledon": [
        "wimbledon", "ویمبلدون",
    ],
    "Australian Open": [
        "australian open", "اوپن استرالیا",
    ],
    "Roland Garros": [
        "roland garros", "french open", "رولان گاروس",
    ],
    "US Open": [
        "us open", "اوپن آمریکا",
    ],
}


def detect_league(text: str) -> Optional[str]:
    """اسم مسابقه‌ی اصلی که در متن آمده، یا None."""

    if not text:
        return None

    for league, keywords in LEAGUE_KEYWORDS.items():
        for keyword in keywords:
            if keyword_in_text(keyword, text):
                return league

    return None
