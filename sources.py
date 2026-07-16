"""
KhabarF24 Sources v6.0

News Sources:

World
Iran
Technology
Gaming
Sport
Economy
Weather
"""



RSS_SOURCES = [


    # ==========================
    # 🌍 World News
    # ==========================


    {
        "name": "BBC",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "world"
    },


    {
        "name": "CNN",
        "url": "http://rss.cnn.com/rss/edition.rss",
        "category": "world"
    },


    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "category": "world"
    },


    {
        "name": "Arab News",
        "url": "https://www.arabnews.com/rss.xml",
        "category": "world"
    },


    {
        "name": "Sky News",
        "url": "https://feeds.skynews.com/feeds/rss/world.xml",
        "category": "world"
    },




    # ==========================
    # 🇮🇷 Iran News
    # ==========================


    {
        "name": "ISNA",
        "url": "https://www.isna.ir/rss",
        "category": "iran"
    },


    {
        "name": "Tasnim",
        "url": "https://www.tasnimnews.com/fa/rss",
        "category": "iran"
    },


    {
        "name": "Fars",
        "url": "https://www.farsnews.ir/rss",
        "category": "iran"
    },


    {
        "name": "Iran International",
        "url": "https://www.iranintl.com/rss",
        "category": "iran"
    },




    # ==========================
    # 🇮🇱 Israel Sources
    # ==========================


    {
        "name": "Kan Israel",
        "url": "https://www.kan.org.il/rss/",
        "category": "world"
    },


    {
        "name": "Channel 12 Israel",
        "url": "https://www.mako.co.il/rss",
        "category": "world"
    },




    # ==========================
    # 💻 Technology
    # ==========================


    {
        "name": "TechCrunch",
        "url": "https://techcrunch.com/feed/",
        "category": "technology"
    },


    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "category": "technology"
    },


    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "category": "technology"
    },


    {
        "name": "Digikala Mag",
        "url": "https://www.digikala.com/mag/feed/",
        "category": "technology"
    },


    {
        "name": "Digiato",
        "url": "https://digiato.com/feed",
        "category": "technology"
    },


    {
        "name": "Vigiato",
        "url": "https://vigiato.net/feed",
        "category": "gaming"
    },




    # ==========================
    # 🎮 Gaming
    # ==========================


    {
        "name": "PlayStation Blog",
        "url": "https://blog.playstation.com/feed/",
        "category": "gaming"
    },


    {
        "name": "Xbox",
        "url": "https://news.xbox.com/en-us/feed/",
        "category": "gaming"
    },




    # ==========================
    # ⚽ Sport
    # ==========================


    {
        "name": "ESPN",
        "url": "https://www.espn.com/espn/rss/news",
        "category": "sport"
    },


    {
        "name": "Sky Sports",
        "url": "https://www.skysports.com/rss/12040",
        "category": "sport"
    },


    {
        "name": "FIFA",
        "url": "https://www.fifa.com/rss-feeds",
        "category": "sport"
    },


    {
        "name": "UEFA",
        "url": "https://www.uefa.com/rssfeed/news",
        "category": "sport"
    },


    {
        "name": "Premier League",
        "url": "https://www.premierleague.com/rss/news",
        "category": "sport"
    },


    {
        "name": "Bundesliga",
        "url": "https://www.bundesliga.com/en/bundesliga/rss",
        "category": "sport"
    },


    {
        "name": "LaLiga",
        "url": "https://www.laliga.com/en-GB/rss",
        "category": "sport"
    },


    {
        "name": "Serie A",
        "url": "https://www.legaseriea.it/en/rss",
        "category": "sport"
    },


    {
        "name": "Di Marzio",
        "url": "https://gianlucadimarzio.com/en/feed",
        "category": "sport"
    },


    {
        "name": "Mundo Deportivo",
        "url": "https://www.mundodeportivo.com/rss/home.xml",
        "category": "sport"
    },




    # ==========================
    # 🌦 Weather
    # ==========================


    {
        "name": "Weather",
        "url": "https://weather.com/rss/",
        "category": "weather"
    },


]
