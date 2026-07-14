"""
category_engine.py

KhabarF24 Smart Category Engine v3.1

تشخیص دسته خبر بر اساس:
- عنوان
- خلاصه
- منبع

اولویت:
ورزش > فناوری > اقتصاد > سلامت > علم > هواشناسی > ایران > جهان
"""


CATEGORIES = {


    "sport": [

        # ⚽ Football

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


        # 🏀 Basketball

        "nba",
        "wnba",
        "basketball",
        "lebron",
        "player",
        "athlete",


        # 🏐 Volleyball

        "volleyball",
        "fivb",


        # 🤼 Wrestling

        "wrestling",
        "fila",
        "united world wrestling",


        # 🎾 Tennis

        "tennis",
        "atp",
        "wta",


        # 🏎 Motorsport

        "formula 1",
        "formula one",
        "f1",


        # 🎲 Other sports

        "poker",
        "world series of poker",
        "olympic",
        "championship",
        "tournament",
        "coach",
        "match",
        "win",
        "loss",
        "score",

    ],



    "technology": [

        "technology",
        "artificial intelligence",
        "ai model",
        "openai",
        "google",
        "apple",
        "microsoft",
        "tesla",
        "robot",
        "chip",
        "software",
        "cybersecurity",
        "cyber attack",

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
        "investment",

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
        "isfahan",
        "shiraz",

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



    # اولویت ورزش
    if scores.get("sport", 0) > 0:

        return "sport"



    best_category = max(
        scores,
        key=scores.get
    )



    if scores[best_category] == 0:

        return "world"



    return best_category
