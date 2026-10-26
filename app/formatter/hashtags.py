"""
Smart Hashtag Engine
"""

CATEGORY_TAGS = {
    "world": "#جهان",
    "general": "#جهان",
    "iran": "#ایران",
    "politics": "#سیاسی",
    "economy": "#اقتصاد",
    "technology": "#فناوری",
    "health": "#سلامت",
    "weather": "#هواشناسی",
    "sport": "#ورزش",
}

# کلیدها حروف کوچکِ اسم مسابقه‌اند (همان اسم‌های league_detector.py)
LEAGUE_TAGS = {
    "champions league": "#لیگ_قهرمانان",
    "afc champions league": "#لیگ_قهرمانان_آسیا",
    "europa league": "#لیگ_اروپا",
    "conference league": "#کنفرانس_لیگ",
    "nations league": "#لیگ_ملتها",
    "world cup": "#جام_جهانی",
    "club world cup": "#جام_باشگاههای_جهان",
    "asian cup": "#جام_ملتهای_آسیا",
    "premier league": "#پریمیرلیگ",
    "la liga": "#لالیگا",
    "serie a": "#سری_آ",
    "bundesliga": "#بوندسلیگا",
    "ligue 1": "#لیگ_۱",
    "fa cup": "#جام_حذفی_انگلیس",
    "carabao cup": "#جام_اتحادیه_انگلیس",
    "copa del rey": "#کوپا_دل_ری",
    "persian gulf pro league": "#لیگ_برتر_ایران",
    "nba": "#NBA",
    "euroleague": "#یورولیگ",
    "wimbledon": "#ویمبلدون",
    "australian open": "#اوپن_استرالیا",
    "roland garros": "#رولان_گاروس",
    "us open": "#اوپن_آمریکا",
    "vnl": "#VNL",
    "fivb": "#والیبال",
}

TRANSFER_TAG = "#نقل_و_انتقالات"
INTERVIEW_TAG = "#مصاحبه"
BREAKING_TAG = "#خبرفوری"


class HashtagBuilder:

    def build(self, news):
        hashtags = []

        category = (getattr(news, "category", None) or "").lower()
        sport_hashtag = getattr(news, "sport_hashtag", None)

        if category == "sport" and sport_hashtag:
            hashtags.append(sport_hashtag)
        elif category:
            tag = CATEGORY_TAGS.get(category)
            if tag:
                hashtags.append(tag)

        if getattr(news, "league", None):
            tag = LEAGUE_TAGS.get(
                str(news.league).lower()
            )
            if tag and tag not in hashtags:
                hashtags.append(tag)

        if getattr(news, "is_breaking", False):
            hashtags.append(BREAKING_TAG)

        # هر هشتگ در یک خط جدا (نه کنار هم با فاصله)
        return "\n".join(hashtags)
