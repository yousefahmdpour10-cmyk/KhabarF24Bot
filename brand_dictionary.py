"""
KhabarF24 Brand Dictionary v5.0

Official Name System

Rules:
- Companies => Persian + English
- Organizations => Persian + English
- People => Persian
- Teams => Persian
- Media => Persian + English
"""



# ==================================
# Names with English inside brackets
# ==================================


BRAND_WITH_ENGLISH = {


    # 💻 Technology Companies

    "OpenAI":
        "اوپن‌ای‌آی (OpenAI)",

    "ChatGPT":
        "چت‌جی‌پی‌تی (ChatGPT)",

    "Google":
        "گوگل (Google)",

    "Google DeepMind":
        "گوگل دیپ‌مایند (Google DeepMind)",

    "DeepMind":
        "دیپ‌مایند (DeepMind)",

    "Microsoft":
        "مایکروسافت (Microsoft)",

    "Apple":
        "اپل (Apple)",

    "Meta":
        "متا (Meta)",

    "NVIDIA":
        "انویدیا (NVIDIA)",

    "Tesla":
        "تسلا (Tesla)",

    "Amazon":
        "آمازون (Amazon)",

    "Samsung":
        "سامسونگ (Samsung)",

    "Anthropic":
        "آنتروپیک (Anthropic)",

    "Claude":
        "کلود (Claude)",

    "Gemini":
        "جمینای (Gemini)",

    "Grok":
        "گروک (Grok)",

    "xAI":
        "ایکس‌ای‌آی (xAI)",

    "Boston Dynamics":
        "بوستون داینامیکس (Boston Dynamics)",



    # 📰 Media

    "TechCrunch":
        "تک‌کرانچ (TechCrunch)",

    "The Verge":
        "د ورج (The Verge)",

    "BBC":
        "بی‌بی‌سی (BBC)",

    "CNN":
        "سی‌ان‌ان (CNN)",

    "Reuters":
        "رویترز (Reuters)",

    "Al Jazeera":
        "الجزیره (Al Jazeera)",

    "ESPN":
        "ESPN",



    # 🏆 Organizations

    "FIFA":
        "فیفا (FIFA)",

    "UEFA":
        "یوفا (UEFA)",

    "AFC":
        "کنفدراسیون فوتبال آسیا (AFC)",

    "NBA":
        "لیگ بسکتبال آمریکا (NBA)",

    "WNBA":
        "لیگ بسکتبال زنان آمریکا (WNBA)",

    "ATP":
        "تور جهانی تنیس مردان (ATP)",

    "WTA":
        "تور جهانی تنیس زنان (WTA)",

}





# ==================================
# Persian only names
# ==================================


BRAND_PERSIAN = {


    # 🌍 Countries

    "United States":
        "آمریکا",

    "United Kingdom":
        "بریتانیا",

    "Iran":
        "ایران",

    "Islamic Republic of Iran":
        "جمهوری اسلامی ایران",

    "Israel":
        "اسرائیل",

    "Israeli":
        "اسرائیلی",

    "Lebanon":
        "لبنان",

    "Yemen":
        "یمن",

    "Gaza":
        "غزه",

    "Ukraine":
        "اوکراین",

    "Russia":
        "روسیه",

    "China":
        "چین",

    "France":
        "فرانسه",

    "Spain":
        "اسپانیا",

    "Argentina":
        "آرژانتین",

    "England":
        "انگلیس",




    # 👤 People

    "Donald Trump":
        "دونالد ترامپ",

    "Joe Biden":
        "جو بایدن",

    "Lionel Messi":
        "لیونل مسی",

    "Cristiano Ronaldo":
        "کریستیانو رونالدو",

    "Kylian Mbappe":
        "کیلیان امباپه",

    "Lamine Yamal":
        "لامین یامال",

    "Jude Bellingham":
        "جود بلینگهام",

    "Erling Haaland":
        "ارلینگ هالند",




    # ⚽ Teams

    "Manchester United":
        "منچستر یونایتد",

    "Manchester City":
        "منچستر سیتی",

    "Real Madrid":
        "رئال مادرید",

    "FC Barcelona":
        "بارسلونا",

    "Barcelona":
        "بارسلونا",

    "Liverpool":
        "لیورپول",

    "Arsenal":
        "آرسنال",

    "Chelsea":
        "چلسی",

    "Bayern Munich":
        "بایرن مونیخ",

    "Paris Saint-Germain":
        "پاری‌سن‌ژرمن",

    "PSG":
        "پاری‌سن‌ژرمن",

    "Juventus":
        "یوونتوس",

    "Borussia Dortmund":
        "بوروسیا دورتموند",



    # 🎮 Games

    "Assassin's Creed":
        "اساسینز کرید",

    "PlayStation":
        "پلی‌استیشن",

    "Xbox":
        "ایکس‌باکس",

    "Nintendo":
        "نینتندو",

}





# ==================================
# Replace Engine
# ==================================


def replace_official_names(text):


    if not text:

        return ""



    # اگر قبلاً فارسی + انگلیسی شده، دوباره تغییر نده

    for english, persian in BRAND_WITH_ENGLISH.items():


        if english in text:


            text = text.replace(

                english,

                persian

            )



    for english, persian in BRAND_PERSIAN.items():


        if english in text:


            text = text.replace(

                english,

                persian

            )



    return text.strip()
