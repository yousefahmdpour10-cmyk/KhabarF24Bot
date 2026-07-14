"""
category_engine.py

KhabarF24 Smart Category Engine

تشخیص دسته خبر بر اساس:
- عنوان
- خلاصه
- منبع

اولویت:
ورزش > فناوری > اقتصاد > سلامت > علم > هواشناسی > جهان > ایران
"""



CATEGORIES = {


    "sport": [

        # Football
        "football",
        "soccer",
        "fifa",
        "uefa",
        "afc",
        "premier league",
        "champions league",
        "laliga",
        "serie a",
        "bundesliga",
        "barcelona",
        "real madrid",
        "manchester",
        "liverpool",
        "arsenal",
        "chelsea",
        "messi",
        "mbappe",
        "ronaldo",
        "yamal",

        # Basketball
        "nba",
        "wnba",
        "basketball",
        "lebron",

        # Volleyball
        "volleyball",
        "fivb",

        # Wrestling
        "wrestling",
        "fila",
        "united world wrestling",

        # Tennis
        "tennis",
        "atp",
        "wta",

        # Motorsport
        "formula 1",
        "f1",

    ],



    "technology": [

        "technology",
        "tech",
        "ai",
        "artificial intelligence",
        "openai",
        "google",
        "apple",
        "microsoft",
        "tesla",
        "robot",
        "chip",
        "software",
        "cyber",

    ],



    "economy": [

        "economy",
        "market",
        "stock",
        "finance",
        "inflation",
        "bitcoin",
        "currency",
        "bank",

    ],



    "health": [

        "health",
        "medical",
        "medicine",
        "hospital",
        "virus",
        "who",

    ],



    "science": [

        "science",
        "space",
        "nasa",
        "research",
        "discovery",

    ],



    "weather": [

        "weather",
        "storm",
        "rain",
        "temperature",
        "climate",

    ],



    "iran": [

        "iran",
        "tehran",
        "islamic republic",

    ]

}




def detect_smart_category(title="", summary="", source=""):


    text = f"""
    {title}
    {summary}
    {source}
    """.lower()



    scores = {}


    for category, keywords in CATEGORIES.items():

        score = 0

        for word in keywords:

            if word.lower() in text:

                score += 1


        scores[category] = score



    best_category = max(
        scores,
        key=scores.get
    )



    # اگر هیچ چیزی پیدا نشد
    if scores[best_category] == 0:

        return "world"



    return best_category
