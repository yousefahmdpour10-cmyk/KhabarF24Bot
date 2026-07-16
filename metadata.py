"""
KhabarF24 Source Metadata v6.0

Source:
- Flag
- Country
- Original source name

Rule:
Media names remain original
"""



SOURCE_METADATA = {



    # ======================
    # 🌍 World
    # ======================


    "BBC": {

        "country": "🇬🇧"

    },


    "CNN": {

        "country": "🇺🇸"

    },


    "Al Jazeera": {

        "country": "🇶🇦"

    },


    "Arab News": {

        "country": "🇸🇦"

    },


    "Sky News": {

        "country": "🇬🇧"

    },





    # ======================
    # 🇮🇷 Iran
    # ======================


    "ISNA": {

        "country": "🇮🇷"

    },


    "Tasnim": {

        "country": "🇮🇷"

    },


    "Fars": {

        "country": "🇮🇷"

    },


    "Iran International": {

        "country": "🇬🇧"

    },





    # ======================
    # 🇮🇱 Israel
    # ======================


    "Kan Israel": {

        "country": "🇮🇱"

    },


    "Channel 12 Israel": {

        "country": "🇮🇱"

    },





    # ======================
    # 💻 Technology
    # ======================


    "TechCrunch": {

        "country": "🇺🇸"

    },


    "The Verge": {

        "country": "🇺🇸"

    },


    "Ars Technica": {

        "country": "🇺🇸"

    },


    "Digiato": {

        "country": "🇮🇷"

    },


    "Vigiato": {

        "country": "🇮🇷"

    },





    # ======================
    # 🎮 Gaming
    # ======================


    "PlayStation Blog": {

        "country": "🇯🇵"

    },


    "Xbox": {

        "country": "🇺🇸"

    },





    # ======================
    # ⚽ Sport
    # ======================


    "ESPN": {

        "country": "🇺🇸"

    },


    "Sky Sports": {

        "country": "🇬🇧"

    },


    "FIFA": {

        "country": "🇨🇭"

    },


    "UEFA": {

        "country": "🇨🇭"

    },


    "Premier League": {

        "country": "🇬🇧"

    },


    "Bundesliga": {

        "country": "🇩🇪"

    },


    "LaLiga": {

        "country": "🇪🇸"

    },


    "Serie A": {

        "country": "🇮🇹"

    },


    "Di Marzio": {

        "country": "🇮🇹"

    },


    "Mundo Deportivo": {

        "country": "🇪🇸"

    },





    # ======================
    # 🌦 Weather
    # ======================


    "Weather": {

        "country": "🌍"

    },


}





def get_source_flag(source):


    data = SOURCE_METADATA.get(

        source,

        {

            "country": "🌐"

        }

    )


    return data["country"]
