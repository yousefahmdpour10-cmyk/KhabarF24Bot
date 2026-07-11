def detect_category(source, title):

    text = f"{source} {title}".lower()

    # Football
    football = [
        "fifa",
        "uefa",
        "premier league",
        "laliga",
        "serie a",
        "bundesliga",
        "espn",
        "football",
    ]

    # Gaming
    gaming = [
        "rockstar",
        "ubisoft",
        "playstation",
        "xbox",
        "steam",
        "gaming",
        "game",
        "ign",
    ]

    # Technology
    technology = [
        "tech",
        "technology",
        "ars technica",
        "techcrunch",
        "the verge",
        "ai",
        "openai",
    ]

    # Economy
    economy = [
        "economy",
        "market",
        "stock",
        "bitcoin",
        "crypto",
        "gold",
    ]

    for word in football:
        if word in text:
            return "football"

    for word in gaming:
        if word in text:
            return "gaming"

    for word in technology:
        if word in text:
            return "technology"

    for word in economy:
        if word in text:
            return "economy"

    return "world"
