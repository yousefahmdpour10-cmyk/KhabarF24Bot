"""
KhabarF24 Sport Formatter v2.0

Features:
- Sport event detection
- Match flags
- Score formatting
- Remove video-only posts
- Add sport labels to title
"""


import re



TEAM_FLAGS = {

    "انگلیس": "🏴🇬🇧",
    "england": "🏴🇬🇧",

    "آرژانتین": "🇦🇷",
    "argentina": "🇦🇷",

    "اسپانیا": "🇪🇸",
    "spain": "🇪🇸",

    "فرانسه": "🇫🇷",
    "france": "🇫🇷",

    "آلمان": "🇩🇪",
    "germany": "🇩🇪",

    "ایتالیا": "🇮🇹",
    "italy": "🇮🇹",

    "پرتغال": "🇵🇹",
    "portugal": "🇵🇹",

    "برزیل": "🇧🇷",
    "brazil": "🇧🇷",

    "هلند": "🇳🇱",
    "netherlands": "🇳🇱",

    "ایران": "🇮🇷",
    "iran": "🇮🇷",

}





# خبرهایی که ارزش انتشار ندارند

BLOCK_WORDS = [

    "تماشا کنید",

    "watch",

    "watch live",

    "live stream",

    "پخش زنده",

    "هایلایت",

    "highlights",

    "preview",

    "پیش نمایش",

    "ویدیو",

    "video",

]






def is_blocked_sport_news(title, summary):


    text = f"{title} {summary}".lower()


    for word in BLOCK_WORDS:

        if word.lower() in text:

            return True


    return False







def detect_event(title, summary):


    text = f"{title} {summary}".lower()



    if any(x in text for x in [

        "ترکیب",

        "lineup",

        "starting xi",

        "بازیکنان اصلی"

    ]):

        return "📋", "ترکیب رسمی"



    if any(x in text for x in [

        "مصاحبه",

        "گفت",

        "said",

        "interview"

    ]):

        return "🎙", "مصاحبه"



    if any(x in text for x in [

        "انتقال",

        "نقل و انتقالات",

        "transfer"

    ]):

        return "🔄", "انتقال"



    if any(x in text for x in [

        "مصدوم",

        "injury",

        "injured"

    ]):

        return "🏥", "مصدومیت"



    if any(x in text for x in [

        "اخراج",

        "red card",

        "کارت قرمز"

    ]):

        return "🟥", "اخراج"



    if any(x in text for x in [

        "قهرمان",

        "قهرمانی",

        "champion"

    ]):

        return "🏆", "قهرمانی"



    if re.search(

        r"\d+\s*[-–]\s*\d+",

        text

    ):

        return "🏁", "نتیجه"



    return "", ""









def add_flags(text):


    if not text:

        return ""



    items = sorted(

        TEAM_FLAGS.items(),

        key=lambda x: len(x[0]),

        reverse=True

    )



    for team, flag in items:


        pattern = re.compile(

            re.escape(team),

            re.IGNORECASE

        )


        text = pattern.sub(

            f"{flag}{team}",

            text

        )


    return text







def format_score(text):


    pattern = r"([آ-یA-Za-z]+)\s*(\d+)\s*[-–]\s*(\d+)\s*([آ-یA-Za-z]+)"



    def replace(match):


        t1 = match.group(1)

        s1 = match.group(2)

        s2 = match.group(3)

        t2 = match.group(4)



        f1 = TEAM_FLAGS.get(

            t1.lower(),

            ""

        )


        f2 = TEAM_FLAGS.get(

            t2.lower(),

            ""

        )



        return (

            f"{f1}{t1} "

            f"{s1}-{s2} "

            f"{f2}{t2}"

        )



    return re.sub(

        pattern,

        replace,

        text

    )









def format_sport_news(title, summary):



    if is_blocked_sport_news(

        title,

        summary

    ):


        return {

            "blocked": True,

            "title": title,

            "summary": summary

        }







    icon, event = detect_event(

        title,

        summary

    )



    title = format_score(

        title

    )


    summary = format_score(

        summary

    )



    title = add_flags(

        title

    )


    summary = add_flags(

        summary

    )



    if icon:


        title = f"{icon} {title}"







    return {


        "blocked": False,


        "event": event,


        "title": title,


        "summary": summary

    }
