"""
KhabarF24 Sources v8.0
RSS + Scraper Sources - Coordinated with all modules
"""

# =========================
# RSS SOURCES
# =========================

RSS_SOURCES = [

    # 🇮🇷 Iran
    {"name": "ISNA", "url": "https://www.isna.ir/rss", "category": "iran"},
    {"name": "Iran International", "url": "https://www.iranintl.com/feed", "category": "iran"},
    {"name": "Vahid Online", "url": "https://www.vahidonline.com/feed/", "category": "iran"},

    # 🌍 World
    {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "category": "world"},
    {"name": "CNN World", "url": "http://rss.cnn.com/rss/edition_world.rss", "category": "world"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "world"},

    # 💻 Technology
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "category": "technology"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "technology"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "category": "technology"},
    {"name": "Digiato", "url": "https://digiato.com/feed", "category": "technology"},
    {"name": "CITNA", "url": "https://www.citna.ir/rss", "category": "technology"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "category": "technology"},

    # 🎮 Gaming
    {"name": "PlayStation Blog", "url": "https://blog.playstation.com/feed/", "category": "gaming"},
    {"name": "Xbox News", "url": "https://news.xbox.com/en-us/feed/", "category": "gaming"},
    {"name": "Vigiato", "url": "https://vigiato.net/feed", "category": "gaming"},

    # ⚽ Sport
    {"name": "ESPN Sport", "url": "https://www.espn.com/espn/rss/news", "category": "sport"},
    {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml", "category": "sport"},
    {"name": "Sky Sports", "url": "https://www.skysports.com/rss/12040", "category": "sport"},
]

# =========================
# SCRAPER SOURCES
# =========================

SCRAPER_SOURCES = [

    # 🇮🇷 Iran
    {"name": "Tasnim", "url": "https://www.tasnimnews.com", "category": "iran", "type": "scraper"},
    {"name": "Fars News", "url": "https://www.farsnews.ir", "category": "iran", "type": "scraper"},
    {"name": "Khabar Fori", "url": "https://khabarfouri.com", "category": "iran", "type": "scraper"},
    {"name": "Hengaw", "url": "https://hengaw.net", "category": "iran", "type": "scraper"},

    # 🌍 World / Israel
    {"name": "Kan Israel", "url": "https://www.kan.org.il", "category": "world", "type": "scraper"},
    {"name": "Israel Channel 12", "url": "https://www.n12.co.il", "category": "world", "type": "scraper"},

    # Sports (with sub-category)
    {"name": "Fabrizio Romano", "url": "https://www.fabrizioromano.com", "category": "sport", "sport": "football", "type": "scraper"},
    {"name": "Di Marzio", "url": "https://gianlucadimarzio.com", "category": "sport", "sport": "football", "type": "scraper"},
    {"name": "NBA", "url": "https://www.nba.com", "category": "sport", "sport": "basketball", "type": "scraper"},
    {"name": "FIBA", "url": "https://www.fiba.basketball", "category": "sport", "sport": "basketball", "type": "scraper"},
    {"name": "FIVB", "url": "https://www.fivb.com", "category": "sport", "sport": "volleyball", "type": "scraper"},
    {"name": "UWW", "url": "https://uww.org", "category": "sport", "sport": "wrestling", "type": "scraper"},
    {"name": "ATP Tour", "url": "https://www.atptour.com", "category": "sport", "sport": "tennis", "type": "scraper"},
    {"name": "WTA Tennis", "url": "https://www.wtatennis.com", "category": "sport", "sport": "tennis", "type": "scraper"},
    {"name": "Formula1", "url": "https://www.formula1.com", "category": "sport", "sport": "formula1", "type": "scraper"},
]
