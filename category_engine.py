"""
KhabarF24 Category Engine v6

Hybrid Category System:

1- Source Rules
2- Special Exceptions
3- Keyword Scoring
4- Final Category
"""


from category_rules import SOURCE_RULES



# =====================================
# کلمات کلیدی عمومی
# =====================================


KEYWORDS = {


    "sport": [

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

        "manchester united",
        "manchester city",
        "real madrid",
        "barcelona",
        "liverpool",
        "arsenal",
        "chelsea",

        "messi",
        "ronaldo",
        "mbappe",
        "yamal",

        "nba",
        "basketball",
        "tennis",
        "wrestling",

        "فوتبال",
        "بسکتبال",
        "کشتی",
        "والیبال",
        "جام جهانی",
        "لیگ",
        "فینال",
        "نیمه نهایی",

    ],



    "technology": [

        "technology",
        "tech",
        "ai",
        "artificial intelligence",

        "openai",
        "apple",
        "google",
        "microsoft",
        "tesla",
        "nvidia",

        "robot",
        "software",
        "chip",

        "هوش مصنوعی",
        "فناوری",
        "ربات",

    ],



    "economy": [

        "economy",
        "market",
        "stock",
        "finance",
        "bitcoin",
        "crypto",
        "bank",

        "اقتصاد",
        "بورس",
        "دلار",
        "طلا",

    ],



    "health": [

        "health",
        "medical",
        "medicine",
        "hospital",
        "virus",

        "سلامت",
        "پزشکی",
        "بیماری",

    ],



    "iran": [

        "iran",
        "iranian",
        "tehran",

        "ایران",
        "تهران",

    ],



    "world": [

        "war",
        "attack",
        "strike",
        "missile",

        "trump",
        "biden",
        "israel",
        "russia",
        "ukraine",

        "جنگ",
        "حمله",
        "موشک",
        "ترامپ",
        "اسرائیل",
        "آمریکا",
        "سپاه",
        "تحریم",

    ]

}




# =====================================
# امتیازدهی
# =====================================


def calculate_score(text, words):

    score = 0


    for word in words:

        if word.lower() in text:

            score += 1


    return score





# =====================================
# تشخیص دسته
# =====================================


def detect_smart_category(
        title="",
        summary="",
        source=""
):


    text = (
        f"{title} {summary}"
        .lower()
    )



    # -----------------------------
    # 1) بررسی قانون منبع
    # -----------------------------


    source_category = None

    source_rule = None



    for name, rule in SOURCE_RULES.items():

        if name.lower() in source.lower():

            source_category = rule.get(
                "default"
            )

            source_rule = rule

            break



    # -----------------------------
    # 2) قوانین اجباری
    # -----------------------------


    if source_rule:


        force_world = source_rule.get(
            "force_world",
            []
        )


        for word in force_world:

            if word.lower() in text:

                return "world"




        # اگر منبع تخصصی است

        if source_category:

            return source_category




    # -----------------------------
    # 3) امتیاز کلمات
    # -----------------------------


    scores = {}



    for category, words in KEYWORDS.items():

        scores[category] = calculate_score(
            text,
            words
        )



    # -----------------------------
    # 4) استثناهای مهم
    # -----------------------------


    # جنگ همیشه جهان

    if scores["world"] >= 2:

        return "world"



    # ورزش نیاز به چند نشانه دارد

    if scores["sport"] >= 2:

        return "sport"



    if scores["technology"] >= 2:

        return "technology"



    if scores["economy"] >= 2:

        return "economy"



    if scores["health"] >= 2:

        return "health"



    if scores["iran"] >= 2:

        return "iran"



    # -----------------------------
    # 5) آخرین انتخاب
    # -----------------------------


    if source_category:

        return source_category



    return "world"
