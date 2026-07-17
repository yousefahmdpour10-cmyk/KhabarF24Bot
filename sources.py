"""
KhabarF24 Sources v6.1

RSS Sources:

- Iran
- World
- Politics & Security
- Technology
- Gaming
- Economy
- Sport
- Weather

Update:
- Added Fabrizio Romano
- Improved sport sources
- Keep unstable sources for future scraper
"""


RSS_SOURCES = [


    # =========================
    # 🇮🇷 Iran News
    # =========================


    {
        "name": "ایسنا",
        "url": "https://www.isna.ir/rss",
        "category": "iran"
    },


    {
        "name": "تسنیم",
        "url": "https://www.tasnimnews.com/fa/rss",
        "category": "iran"
    },


    {
        "name": "فارس",
        "url": "https://www.farsnews.ir/rss",
        "category": "iran"
    },


    {
        "name": "خبر فوری",
        "url": "https://khabarfouri.com/feed",
        "category": "iran"
    },


    {
        "name": "ایران اینترنشنال",
        "url": "https://www.iranintl.com/feed",
        "category": "iran"
    },


    {
        "name": "هنگاو",
        "url": "https://hengaw.net/fa/feed",
        "category": "iran"
    },



    # =========================
    # 🌍 World News
    # =========================


    {
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "world"
    },


    {
        "name": "CNN World",
        "url": "http://rss.cnn.com/rss/edition_world.rss",
        "category": "world"
    },


    {
        "name": "Reuters",
        "url": "https://feeds.reuters.com/reuters/worldNews",
        "category": "world"
    },


    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "category": "world"
    },


    {
        "name": "العربیه",
        "url": "https://www.alarabiya.net/.mrss/ar.xml",
        "category": "world"
    },



    # =========================
    # 🇮🇱 Israel
    # =========================


    {
        "name": "کان اسرائیل",
        "url": "https://www.kan.org.il/rss/",
        "category": "world"
    },


    {
        "name": "Channel 12 Israel",
        "url": "https://www.mako.co.il/rss",
        "category": "world"
    },



    # =========================
    # 💻 Technology
    # =========================


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
        "name": "دیجیاتو",
        "url": "https://digiato.com/feed",
        "category": "technology"
    },


    {
        "name": "ویجیاتو",
        "url": "https://vigiato.net/feed",
        "category": "gaming"
    },
    # =========================
    # 🎮 Gaming
    # =========================


    {
        "name": "PlayStation Blog",
        "url": "https://blog.playstation.com/feed/",
        "category": "gaming"
    },


    {
        "name": "Xbox News",
        "url": "https://news.xbox.com/en-us/feed/",
        "category": "gaming"
    },


    {
        "name": "IGN Gaming",
        "url": "https://feeds.ign.com/ignfeeds",
        "category": "gaming"
    },


    {
        "name": "GameSpot",
        "url": "https://www.gamespot.com/feeds/mashup/",
        "category": "gaming"
    },




    # =========================
    # ⚽ Sport
    # =========================


    {
        "name": "Fabrizio Romano",
        "url": "https://www.fabrizioromano.com/feed/",
        "category": "sport"
    },


    {
        "name": "Di Marzio",
        "url": "https://gianlucadimarzio.com/feed",
        "category": "sport"
    },


    {
        "name": "ESPN",
        "url": "https://www.espn.com/espn/rss/news",
        "category": "sport"
    },


    {
        "name": "BBC Sport",
        "url": "https://feeds.bbci.co.uk/sport/rss.xml",
        "category": "sport"
    },


    {
        "name": "Sky Sports",
        "url": "https://www.skysports.com/rss/12040",
        "category": "sport"
    },


    {
        "name": "Mundo Deportivo",
        "url": "https://www.mundodeportivo.com/rss/home",
        "category": "sport"
    },


    {
        "name": "FIFA",
        "url": "https://www.fifa.com/rss-feeds",
        "category": "sport"
    },


    {
        "name": "UEFA",
        "url": "https://www.uefa.com/rssfeed/news/rss.xml",
        "category": "sport"
    },


    {
        "name": "Premier League",
        "url": "https://www.premierleague.com/rss/news",
        "category": "sport"
    },


    {
        "name": "La Liga",
        "url": "https://www.laliga.com/en-GB/rss",
        "category": "sport"
    },


    {
        "name": "Bundesliga",
        "url": "https://www.bundesliga.com/en/bundesliga/rss",
        "category": "sport"
    },


    {
        "name": "Serie A",
        "url": "https://www.legaseriea.it/en/rss",
        "category": "sport"
    },





    # =========================
    # 🌦 Weather
    # =========================


    {
        "name": "AccuWeather",
        "url": "https://www.accuweather.com/en/rss",
        "category": "weather"
    },


    {
        "name": "Weather.com",
        "url": "https://weather.com/rss",
        "category": "weather"
    },


]
