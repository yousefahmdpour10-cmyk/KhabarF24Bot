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

LEAGUE_TAGS = {
    "premier league": "#پریمیرلیگ",
    "la liga": "#لالیگا",
    "serie a": "#سری_آ",
    "bundesliga": "#بوندسلیگا",
    "ligue 1": "#لیگ_۱",
    "champions league": "#لیگ_قهرمانان",
    "europa league": "#لیگ_اروپا",
    "conference league": "#کنفرانس_لیگ",
    "nba": "#NBA",
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
                news.league.lower()
            )
            if tag and tag not in hashtags:
                hashtags.append(tag)

        if getattr(news, "is_breaking", False):
            hashtags.append(BREAKING_TAG)

        return " ".join(hashtags)
