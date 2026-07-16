"""
KhabarF24 Sport Formatter v1.0

ویژه اخبار ورزشی:

- پرچم کشورها
- نتیجه بازی
- ترکیب تیم‌ها
- گل‌ها
- مصاحبه
- نوع خبر ورزشی
"""


import re



TEAM_FLAGS = {

    "eng": "🏴🇬🇧",
    "england": "🏴🇬🇧",
    "انگلیس": "🏴🇬🇧",

    "argentina": "🇦🇷",
    "آرژانتین": "🇦🇷",

    "brazil": "🇧🇷",
    "برزیل": "🇧🇷",

    "spain": "🇪🇸",
    "اسپانیا": "🇪🇸",

    "france": "🇫🇷",
    "فرانسه": "🇫🇷",

    "germany": "🇩🇪",
    "آلمان": "🇩🇪",

    "italy": "🇮🇹",
    "ایتالیا": "🇮🇹",

    "portugal": "🇵🇹",
    "پرتغال": "🇵🇹",

    "netherlands": "🇳🇱",
    "هلند": "🇳🇱",

    "iran": "🇮🇷",
    "ایران": "🇮🇷",

    "japan": "🇯🇵",
    "ژاپن": "🇯🇵",

    "south korea": "🇰🇷",
    "کره جنوبی": "🇰🇷",

}





def detect_sport_type(title, summary):


    text = f"{title} {summary}".lower()



    if any(word in text for word in [

        "lineup",
        "starting xi",
        "ترکیب",
        "بازیکنان اصلی"

    ]):

        return "📋 ترکیب رسمی"



    if any(word in text for word in [

        "goal",
        "گل",
        "scored"

    ]):

        return "⚽ گل"



    if any(word in text for word in [

        "interview",
        "مصاحبه",
        "said",
        "press conference"

    ]):

        return "🎙 مصاحبه"



    if re.search(
        r"\d+\s*[-–]\s*\d+",
        text
    ):

        return "🏁 نتیجه بازی"



    return "🏅 خبر ورزشی"








def add_flags(text):


    if not text:

        return ""



    for team, flag in TEAM_FLAGS.items():

        if team.lower() in text.lower():

            text = text.replace(

                team,

                f"{flag}{team}"

            )


    return text









def format_match_score(text):


    pattern = r"([A-Za-z]+|[\u0600-\u06FF]+)\s*(\d+)\s*[-–]\s*(\d+)\s*([A-Za-z]+|[\u0600-\u06FF]+)"



    def replace(match):


        team1 = match.group(1)

        score1 = match.group(2)

        score2 = match.group(3)

        team2 = match.group(4)



        flag1 = TEAM_FLAGS.get(

            team1.lower(),

            ""

        )


        flag2 = TEAM_FLAGS.get(

            team2.lower(),

            ""

        )



        return (

            f"{flag1}{team1} "

            f"{score1} - {score2} "

            f"{flag2}{team2}"

        )



    return re.sub(

        pattern,

        replace,

        text

    )









def format_sport_news(title, summary):


    sport_type = detect_sport_type(

        title,

        summary

    )



    title = format_match_score(

        title

    )


    summary = format_match_score(

        summary

    )



    title = add_flags(

        title

    )



    summary = add_flags(

        summary

    )



    return {


        "sport_type": sport_type,


        "title": title,


        "summary": summary

}
