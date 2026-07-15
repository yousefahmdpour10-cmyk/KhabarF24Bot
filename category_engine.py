"""
KhabarF24 Smart Category Engine v4

تشخیص دسته:
- sport
- technology
- economy
- health
- science
- weather
- iran
- world
"""


CATEGORIES = {


"sport": [

"fifa",
"uefa",
"afc",
"football",
"soccer",
"premier league",
"champions league",
"laliga",
"serie a",
"bundesliga",

"barcelona",
"real madrid",
"manchester united",
"manchester city",
"liverpool",
"arsenal",
"chelsea",

"messi",
"ronaldo",
"mbappe",
"yamal",

"nba",
"wnba",
"basketball",

"tennis",
"atp",
"wta",

"wrestling",
"fila",
"fivb",

"formula 1",
"f1",

"فوتبال",
"بسکتبال",
"کشتی",
"والیبال",
"جام جهانی",
"لیگ"

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
"cyber",

"هوش مصنوعی",
"فناوری",
"ربات",
"تکنولوژی"

],



"economy": [

"economy",
"market",
"stock",
"finance",
"bitcoin",
"crypto",
"inflation",
"bank",

"اقتصاد",
"بورس",
"دلار",
"ارز",
"طلا"

],



"health": [

"health",
"medical",
"medicine",
"hospital",
"virus",
"disease",

"سلامت",
"پزشکی",
"بیماری",
"واکسن"

],



"science": [

"science",
"space",
"nasa",
"research",

"علم",
"فضا",
"تحقیق"

],



"weather": [

"weather",
"storm",
"rain",
"climate",

"هوا",
"طوفان",
"باران"

],



"iran": [

"iran",
"iranian",
"tehran",

"ایران",
"ایرانی",
"تهران"

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
"china",
"america",

"جنگ",
"حمله",
"موشک",
"ترامپ",
"اسرائیل",
"آمریکا",
"روسیه",
"چین",
"تحریم",
"سپاه"

]

}




def detect_smart_category(title="", summary="", source=""):


    text = (
        f"{title} {summary} {source}"
    ).lower()



    scores = {}


    for category, words in CATEGORIES.items():

        score = 0

        for word in words:

            if word.lower() in text:

                score += 1


        scores[category] = score



    # -------------------------
    # اولویت‌های مهم
    # -------------------------


    # جنگ و سیاست
    if scores["world"] >= 2:

        return "world"



    # ورزش واقعی
    if scores["sport"] >= 2:

        return "sport"



    # فناوری
    if scores["technology"] >= 1:

        return "technology"



    # اقتصاد
    if scores["economy"] >= 1:

        return "economy"



    # سلامت
    if scores["health"] >= 1:

        return "health"



    # علم
    if scores["science"] >= 1:

        return "science"



    # هوا
    if scores["weather"] >= 1:

        return "weather"



    # ایران
    if scores["iran"] >= 1:

        return "iran"



    return "world"
