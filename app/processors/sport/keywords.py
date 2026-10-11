
"""
Sport Keywords

اطلاعات رشته‌های ورزشی برای تشخیص خودکار خبر
"""

SPORTS = {
    "football": {
        "name": "فوتبال",
        "emoji": "⚽",
        "hashtag": "#فوتبال",
        "keywords": [
            # واژه‌های عمومی فوتبال
            "football", "footballer", "footballers", "soccer",
            "fifa", "uefa", "penalty",
            "winger", "midfielder", "striker", "defender",
            "goalkeeper", "national team", "call-up",
            "transfer news", "transfer window", "manager",
            "head coach", "premier league", "la liga",
            "serie a", "bundesliga", "ligue 1",
            "champions league", "europa league",
            "conference league", "world cup",
            "match of the day", "kick-off", "kickoff",
            "fixtures", "football match", "football club",
            "red card", "yellow card", "offside",
            "free kick", "corner kick", "own goal",
            "hat-trick", "clean sheet", "substitute",
            "starting lineup", "starting eleven",
            "transfer", "signing", "loan deal",

            # باشگاه‌های مطرح
            "manchester united", "man united", "man utd",
            "manchester city", "man city",
            "liverpool", "arsenal", "chelsea", "tottenham",
            "newcastle united", "aston villa", "west ham",
            "real madrid", "barcelona", "atletico madrid",
            "bayern munich", "borussia dortmund",
            "paris saint-germain", "paris saint germain",
            "psg", "juventus", "inter milan", "ac milan",
            "napoli", "roma", "ajax", "benfica", "porto",
            "celtic", "rangers",

            # نام‌های مطرح بازیکنان و مربیان
            "michael carrick", "sir alex ferguson",
            "pep guardiola", "jose mourinho",
            "carlo ancelotti", "mikel arteta",
            "arne slot", "jurgen klopp",
            "erik ten hag", "ruben amorim",
            "cristiano ronaldo", "lionel messi",
            "kylian mbappe", "mohamed salah",
            "erling haaland", "harry kane",
            "bruno fernandes", "marcus rashford",
            "bukayo saka", "cole palmer",
            "vinicius junior", "jude bellingham",

            # رقابت‌ها و سازمان‌ها
            "english premier league", "epl",
            "fa cup", "efl cup", "carabao cup",
            "uefa champions league", "uefa europa league",
            "fifa world cup", "euros", "euro 2024",
            "euro 2028", "copa america",
            "afcon", "african cup of nations",

            # فارسی
            "فوتبال", "فوتبالیست", "پنالتی",
            "لیگ برتر", "جام جهانی", "یوفا", "فیفا",
            "لیگ قهرمانان", "نقل و انتقالات",
            "منچستر یونایتد", "منچستریونایتد",
            "منچستر سیتی", "منچسترسیتی",
            "لیورپول", "آرسنال", "چلسی",
            "تاتنهام", "رئال مادرید", "بارسلونا",
            "بایرن مونیخ", "پاری سن ژرمن",
            "کریستیانو رونالدو", "لیونل مسی",
            "امباپه", "هالند", "برونو فرناندز",
            "مایکل کریک", "سر الکس فرگوسن",
        ],
    },

    "basketball": {
        "name": "بسکتبال",
        "emoji": "🏀",
        "hashtag": "#بسکتبال",
        "keywords": [
            "basketball", "nba", "wnba", "fiba",
            "euroleague", "slam dunk", "three-pointer",
            "بسکتبال", "ان بی ای",
        ],
    },

    "volleyball": {
        "name": "والیبال",
        "emoji": "🏐",
        "hashtag": "#والیبال",
        "keywords": ["volleyball", "fivb", "والیبال"],
    },

    "tennis": {
        "name": "تنیس",
        "emoji": "🎾",
        "hashtag": "#تنیس",
        "keywords": [
            "tennis", "atp", "wta", "grand slam",
            "wimbledon", "roland garros", "us open",
            "australian open", "تنیس",
        ],
    },

    "wrestling": {
        "name": "کشتی",
        "emoji": "🤼",
        "hashtag": "#کشتی",
        "keywords": ["wrestling", "uww", "کشتی"],
    },

    "boxing": {
        "name": "بوکس",
        "emoji": "🥊",
        "hashtag": "#بوکس",
        "keywords": ["boxing", "boxer", "بوکس"],
    },

    "mma": {
        "name": "هنرهای رزمی",
        "emoji": "🥋",
        "hashtag": "#MMA",
        "keywords": [
            "mma", "ufc", "bellator",
            "mixed martial arts", "یو اف سی",
        ],
    },

    "formula1": {
        "name": "فرمول یک",
        "emoji": "🏎️",
        "hashtag": "#فرمول_یک",
        "keywords": [
            "formula 1", "formula one", "f1",
            "fia", "grand prix", "فرمول یک",
        ],
    },

    "motogp": {
        "name": "موتورسواری",
        "emoji": "🏍️",
        "hashtag": "#MotoGP",
        "keywords": [
            "motogp", "motorcycle grand prix", "موتوجی پی",
        ],
    },

    "cycling": {
        "name": "دوچرخه‌سواری",
        "emoji": "🚴",
        "hashtag": "#دوچرخه_سواری",
        "keywords": [
            "cycling", "tour de france", "uci", "دوچرخه",
        ],
    },

    "swimming": {
        "name": "شنا",
        "emoji": "🏊",
        "hashtag": "#شنا",
        "keywords": ["swimming", "world aquatics", "شنا"],
    },

    "athletics": {
        "name": "دوومیدانی",
        "emoji": "🏃",
        "hashtag": "#دوومیدانی",
        "keywords": [
            "athletics", "track and field",
            "world athletics", "دوومیدانی",
        ],
    },

    "golf": {
        "name": "گلف",
        "emoji": "⛳",
        "hashtag": "#گلف",
        "keywords": ["golf", "pga", "گلف"],
    },

    "baseball": {
        "name": "بیسبال",
        "emoji": "⚾",
        "hashtag": "#بیسبال",
        "keywords": ["baseball", "mlb", "بیسبال"],
    },

    "american_football": {
        "name": "فوتبال آمریکایی",
        "emoji": "🏈",
        "hashtag": "#فوتبال_آمریکایی",
        "keywords": [
            "nfl", "super bowl", "american football",
            "فوتبال آمریکایی",
        ],
    },

    "rugby": {
        "name": "راگبی",
        "emoji": "🏉",
        "hashtag": "#راگبی",
        "keywords": ["rugby", "راگبی"],
    },

    "table_tennis": {
        "name": "تنیس روی میز",
        "emoji": "🏓",
        "hashtag": "#تنیس_روی_میز",
        "keywords": ["table tennis", "ping pong", "تنیس روی میز"],
    },

    "badminton": {
        "name": "بدمینتون",
        "emoji": "🏸",
        "hashtag": "#بدمینتون",
        "keywords": ["badminton", "بدمینتون"],
    },

    "handball": {
        "name": "هندبال",
        "emoji": "🤾",
        "hashtag": "#هندبال",
        "keywords": ["handball", "هندبال"],
    },

    "chess": {
        "name": "شطرنج",
        "emoji": "♟️",
        "hashtag": "#شطرنج",
        "keywords": ["chess", "fide", "شطرنج"],
    },

    "esports": {
        "name": "ورزش‌های الکترونیکی",
        "emoji": "🎮",
        "hashtag": "#Esports",
        "keywords": [
            "esports", "e-sports", "counter strike",
            "dota", "league of legends", "valorant",
        ],
    },
}
