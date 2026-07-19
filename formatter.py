"""
KhabarF24 Formatter v7.0

Final Telegram Formatter

Compatible with:
- category_engine v7
- category_hashtags.py
- sport_formatter v5
- ai_processor v7
- news_fetcher v7

Features:
- Final KhabarF24 style
- Sport separated
- Real team flags
- English source names
- Source country flags
- Clean Telegram output
"""


print("📰 KhabarF24 Formatter v7.0 Loaded")



# =====================================
# Category Style
# =====================================


CATEGORY_STYLE = {


    "politics": {

        "name": "سیاست",

        "emoji": "🔴",

        "hashtag": "#سیاست"

    },


    "iran": {

        "name": "ایران",

        "emoji": "🇮🇷",

        "hashtag": "#ایران"

    },


    "world": {

        "name": "جهان",

        "emoji": "🌍",

        "hashtag": "#جهان"

    },


    "technology": {

        "name": "تکنولوژی",

        "emoji": "💻",

        "hashtag": "#تکنولوژی"

    },


    "gaming": {

        "name": "گیم",

        "emoji": "🎮",

        "hashtag": "#گیم"

    },


    "economy": {

        "name": "اقتصاد",

        "emoji": "💰",

        "hashtag": "#اقتصاد"

    },


    "health": {

        "name": "سلامت",

        "emoji": "🏥",

        "hashtag": "#سلامت"

    },


    "science": {

        "name": "علم",

        "emoji": "🔬",

        "hashtag": "#علم"

    },


    "weather": {

        "name": "آب‌وهوا",

        "emoji": "🌦",

        "hashtag": "#آب_وهوا"

    },


    # Sports

    "football": {

        "name": "فوتبال",

        "emoji": "⚽",

        "hashtag": "#فوتبال"

    },


    "basketball": {

        "name": "بسکتبال",

        "emoji": "🏀",

        "hashtag": "#بسکتبال"

    },


    "volleyball": {

        "name": "والیبال",

        "emoji": "🏐",

        "hashtag": "#والیبال"

    },


    "tennis": {

        "name": "تنیس",

        "emoji": "🎾",

        "hashtag": "#تنیس"

    },


    "wrestling": {

        "name": "کشتی",

        "emoji": "🤼",

        "hashtag": "#کشتی"

    },


    "formula1": {

        "name": "فرمول یک",

        "emoji": "🏎️",

        "hashtag": "#فرمول_یک"

    },


    "combat": {

        "name": "ورزش رزمی",

        "emoji": "🥊",

        "hashtag": "#ورزش_رزمی"

    },


}







# =====================================
# Source Dictionary
# نام منابع انگلیسی + پرچم
# =====================================


SOURCE_FLAGS = {


    "BBC Sport": "🇬🇧",

    "BBC": "🇬🇧",


    "Reuters": "🇺🇸",


    "CNN": "🇺🇸",


    "ESPN": "🇺🇸",


    "Sky Sports": "🇬🇧",


    "FIFA": "🌐",


    "UEFA": "🇪🇺",


    "Premier League": "🇬🇧",


    "La Liga": "🇪🇸",


    "Bundesliga": "🇩🇪",


    "Serie A": "🇮🇹",


    "Di Marzio": "🇮🇹",


    "Al Jazeera": "🇶🇦",


    "Al Arabiya": "🇸🇦",


    "Kan Israel": "🇮🇱",


    "Israel Channel 12": "🇮🇱",


    "Iran International": "🇬🇧",


    "Tasnim": "🇮🇷",


    "Fars News": "🇮🇷",


    "ISNA": "🇮🇷",


    "Khabar Fori": "🇮🇷",


    "Digiato": "🇮🇷",


    "Digikala": "🇮🇷",


}





def get_source_flag(source):


    if not source:

        return "🌐"



    for name, flag in SOURCE_FLAGS.items():


        if name.lower() in source.lower():

            return flag



    return "🌐"







def clean_source_name(source):

    if not source:
        return "Unknown"


    SOURCE_NAMES = {

        # Iran
        "ایسنا": "ISNA",
        "ایرنا": "IRNA",
        "تسنیم": "Tasnim",
        "فارس": "Fars News",
        "خبر فوری": "Khabar Fori",
        "ایران اینترنشنال": "Iran International",


        # World
        "بی‌بی‌سی": "BBC",
        "بی بی سی": "BBC",
        "بی‌بی‌سی اسپورت": "BBC Sport",

        "رویترز": "Reuters",

        "سی‌ان‌ان": "CNN",

        "الجزیره": "Al Jazeera",

        "العربیه": "Al Arabiya",


        # Israel
        "کان اسرائیل": "Kan Israel",
        "کانال ۱۲ اسرائیل": "Israel Channel 12",


        # Technology
        "دیجیاتو": "Digiato",
        "دیجی‌کالا": "Digikala",

        "تک‌کرانچ": "TechCrunch",
        "د ورج": "The Verge",
        "آرس تکنیکا": "Ars Technica",


        # Sport
        "بی‌بی‌سی اسپورت": "BBC Sport",
        "اسکای اسپورت": "Sky Sports",
        "ای‌اس‌پی‌ان": "ESPN",

        "فیفا": "FIFA",
        "یوفا": "UEFA",

        "لیگ برتر انگلیس": "Premier League",
        "لالیگا": "La Liga",
        "بوندسلیگا": "Bundesliga",
        "سری آ": "Serie A",

        "دی‌مارزیو": "Di Marzio",

    }


    for old, new in SOURCE_NAMES.items():

        if old.lower() in source.lower():

            return new


    return source


    return source
    # =====================================
# Team Flags
# فقط تیم‌ها و کشور واقعی
# =====================================


TEAM_FLAGS = {


    "منچستر یونایتد":
        "🇬🇧 منچستر یونایتد (Manchester United)",


    "Manchester United":
        "🇬🇧 منچستر یونایتد (Manchester United)",



    "منچستر سیتی":
        "🇬🇧 منچستر سیتی (Manchester City)",



    "رئال مادرید":
        "🇪🇸 رئال مادرید (Real Madrid)",



    "Real Madrid":
        "🇪🇸 رئال مادرید (Real Madrid)",



    "بارسلونا":
        "🇪🇸 بارسلونا (Barcelona)",



    "Barcelona":
        "🇪🇸 بارسلونا (Barcelona)",



    "لیورپول":
        "🇬🇧 لیورپول (Liverpool)",



    "Liverpool":
        "🇬🇧 لیورپول (Liverpool)",



    "آرسنال":
        "🇬🇧 آرسنال (Arsenal)",



    "بایرن مونیخ":
        "🇩🇪 بایرن مونیخ (Bayern Munich)",



    "پاری سن ژرمن":
        "🇫🇷 پاری‌سن‌ژرمن (Paris Saint-Germain)",



    "یوونتوس":
        "🇮🇹 یوونتوس (Juventus)",


}








# =====================================
# Sport Style
# =====================================


def get_sport_style(category):


    return CATEGORY_STYLE.get(

        category,

        CATEGORY_STYLE["world"]

    )








# =====================================
# Add Team Flags
# =====================================


def add_team_flags(text):


    if not text:

        return ""



    for team, replacement in TEAM_FLAGS.items():


        if replacement not in text:

            text = text.replace(

                team,

                replacement

            )



    return text







# =====================================
# Clean Empty Lines
# =====================================


def clean_lines(text):


    lines = []


    for line in text.split("\n"):


        if line.strip():

            lines.append(

                line.rstrip()

            )



    return "\n".join(lines)









# =====================================
# Sport Extra Information
# =====================================


def format_sport_extra(sport):


    if not sport:

        return ""



    output = []



    if sport.get("score"):


        output.append(

            f"⚽ {sport['score']}"

        )



    if sport.get("yellow_cards"):


        output.append(

            f"🟨 {sport['yellow_cards']}"

        )



    if sport.get("red_cards"):


        output.append(

            f"🟥 {sport['red_cards']}"

        )



    return "\n".join(output)










# =====================================
# Main Telegram Formatter
# =====================================


def format_news(

        title,

        summary,

        source,

        category,

        sport=None,

        game=None,

        hashtag_data=None

):

    # دسته


    style = get_sport_style(

        category

    )



    category_name = style["name"]

    category_emoji = style["emoji"]

    hashtag = style["hashtag"]






    # اگر ورزش تخصصی باشد


    if sport:


        sport_type = sport.get(

            "type",

            ""

        )


        if sport_type in CATEGORY_STYLE:


            style = CATEGORY_STYLE[sport_type]


            category_name = style["name"]

            category_emoji = style["emoji"]

            hashtag = style["hashtag"]







    # تیم‌ها


    title = add_team_flags(

        title

    )


    summary = add_team_flags(

        summary

    )






    # منبع


    source = clean_source_name(

        source

    )


    source_flag = get_source_flag(

        source

    )






    # متن نهایی


        message = f"""━━━━━━━━━━━━━━━━
🔴 KhabarF24 | {category_emoji} {category_name}
━━━━━━━━━━━━━━━━


📰 {title}


✍️ {summary}



• 🗞️ {source_flag} {source}


━━━━━━━━━━━━━━━━
📢 @KhabarF24

{hashtag}
"""


    return clean_lines(

        message

    )
