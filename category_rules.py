"""
KhabarF24 Category Rules v1

قوانین اختصاصی منابع
"""


# =====================================
# قوانین منابع
# =====================================


SOURCE_RULES = {


    # =========================
    # 🌍 World News
    # =========================


    "Al Jazeera": {

        "default": "world",

        "force_world": [

            "iran",
            "iranian",
            "trump",
            "biden",
            "israel",
            "gaza",
            "war",
            "attack",
            "strike",
            "missile",

            "ایران",
            "ترامپ",
            "آمریکا",
            "اسرائیل",
            "غزه",
            "جنگ",
            "حمله",
            "سپاه",
            "تحریم",
            "دولت",
            "رئیس جمهور",

        ],

    },


    "BBC": {

        "default": "world",

    },


    "CNN": {

        "default": "world",

    },


    "Reuters": {

        "default": "world",

    },


    "Associated Press": {

        "default": "world",

    },


    "NYTimes": {

        "default": "world",

    },



    # =========================
    # 🏅 Sport
    # =========================


    "ESPN": {

        "default": "sport",

    },


    "Sky Sports": {

        "default": "sport",

    },


    "Fabrizio Romano": {

        "default": "sport",

    },


    "Di Marzio": {

        "default": "sport",

    },


    "FIFA": {

        "default": "sport",

    },


    "UEFA": {

        "default": "sport",

    },


    "Premier League": {

        "default": "sport",

    },


    "Bundesliga": {

        "default": "sport",

    },


    "LaLiga": {

        "default": "sport",

    },


    "Serie A": {

        "default": "sport",

    },



    # =========================
    # 💻 Technology
    # =========================


    "TechCrunch": {

        "default": "technology",

    },


    "The Verge": {

        "default": "technology",

    },


    "Ars Technica": {

        "default": "technology",

    },


    "Wired": {

        "default": "technology",

    },



    # =========================
    # 🇮🇷 Iran Sources
    # =========================


    "Tasnim": {

        "default": "iran",

    },


    "Fars": {

        "default": "iran",

    },


    "ISNA": {

        "default": "iran",

    },


    "خبر فوری": {

        "default": "iran",

    },

}
