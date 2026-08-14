"""
Smart Hashtag Engine
"""

CATEGORY_TAGS = {

    "world": "#جهان",

    "iran": "#ایران",

    "politics": "#سیاسی",

    "economy": "#اقتصاد",

    "technology": "#فناوری",

    "health": "#سلامت",

    "sport": "#ورزش",

}

SPORT_TAGS = {

    "football": "#فوتبال",

    "basketball": "#بسکتبال",

    "volleyball": "#والیبال",

    "tennis": "#تنیس",

    "wrestling": "#کشتی",

    "futsal": "#فوتسال",

    "handball": "#هندبال",

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

        # دسته خبر
        if getattr(news, "category", None):

            tag = CATEGORY_TAGS.get(
                news.category.lower()
            )

            if tag:
                hashtags.append(tag)

        # رشته ورزشی
        if getattr(news, "sport", None):

            tag = SPORT_TAGS.get(
                news.sport.lower()
            )

            if tag and tag not in hashtags:
                hashtags.append(tag)

        # لیگ یا تورنمنت
        if getattr(news, "league", None):

            tag = LEAGUE_TAGS.get(
                news.league.lower()
            )

            if tag and tag not in hashtags:
                hashtags.append(tag)

        # خبر فوری
        if getattr(news, "is_breaking", False):

            hashtags.append(BREAKING_TAG)

        return " ".join(hashtags)
