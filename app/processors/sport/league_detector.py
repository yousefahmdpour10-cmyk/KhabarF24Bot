"""تشخیص لیگ و رقابت ورزشی از متن خبر."""

import re
from typing import Optional

LEAGUES = {
"premier_league": [
"premier league",
"لیگ برتر انگلیس",
],
"champions_league": [
"champions league",
"uefa champions league",
"لیگ قهرمانان اروپا",
],
"europa_league": [
"europa league",
"لیگ اروپا",
],
"la_liga": [
"la liga",
"لالیگا",
],
"serie_a": [
"serie a",
"سری آ ایتالیا",
],
"bundesliga": [
"bundesliga",
"بوندسلیگا",
],
"ligue_1": [
"ligue 1",
"لوشامپیونه",
],
"world_cup": [
"world cup",
"جام جهانی",
],
"asian_champions_league": [
"afc champions league",
"لیگ قهرمانان آسیا",
],
"iran_premier_league": [
"persian gulf pro league",
"iran pro league",
"لیگ برتر ایران",
"لیگ برتر فوتبال ایران",
],
}

def detect_league(text: str) -> Optional[str]:
"""نام رقابت را از متن پیدا می‌کند؛ در صورت نبود، None برمی‌گرداند."""
if not text:
return None

normalized = re.sub(r"\s+", " ", text).casefold()

for league, keywords in LEAGUES.items():
    for keyword in keywords:
        if keyword.casefold() in normalized:
            return league

return None
