"""
KhabarF24 Brand Dictionary v5.1

Rules:
- Companies / Brands / Organizations / Teams:
  Persian + English in parentheses

- Countries:
  Persian only

- People:
  Persian only

- Media sources:
  Keep original
"""


import re


BRAND_DICTIONARY = {


    # =====================
    # 💻 Technology
    # =====================

    "OpenAI": "اوپن‌ای‌آی (OpenAI)",
    "openai": "اوپن‌ای‌آی (OpenAI)",

    "ChatGPT": "چت‌جی‌پی‌تی (ChatGPT)",
    "chatgpt": "چت‌جی‌پی‌تی (ChatGPT)",

    "Artificial Intelligence": "هوش مصنوعی (Artificial Intelligence)",
    "AI": "هوش مصنوعی (AI)",

    "Google DeepMind": "گوگل دیپ‌مایند (Google DeepMind)",
    "DeepMind": "دیپ‌مایند (DeepMind)",

    "Microsoft": "مایکروسافت (Microsoft)",
    "Apple": "اپل (Apple)",
    "Google": "گوگل (Google)",

    "Meta": "متا (Meta)",
    "Amazon": "آمازون (Amazon)",

    "Tesla": "تسلا (Tesla)",
    "Tesla Inc.": "شرکت تسلا (Tesla Inc.)",

    "NVIDIA": "انویدیا (NVIDIA)",
    "Nvidia": "انویدیا (NVIDIA)",

    "Samsung": "سامسونگ (Samsung)",
    "Huawei": "هواوی (Huawei)",

    "SpaceX": "اسپیس‌ایکس (SpaceX)",

    "Boston Dynamics": "بوستون داینامیکس (Boston Dynamics)",

    "xAI": "xAI",
    "Grok": "گروک (Grok)",



    # =====================
    # 🎮 Gaming
    # =====================

    "PlayStation": "پلی‌استیشن (PlayStation)",
    "Xbox": "ایکس‌باکس (Xbox)",
    "Nintendo": "نینتندو (Nintendo)",

    "Steam": "استیم (Steam)",

    "Ubisoft": "یوبی‌سافت (Ubisoft)",

    "Electronic Arts": "الکترونیک آرتس (Electronic Arts)",

    "Call of Duty": "کال آف دیوتی (Call of Duty)",

    "Warzone": "وارزون (Warzone)",

    "Minecraft": "ماینکرفت (Minecraft)",

    "Fortnite": "فورتنایت (Fortnite)",



    # =====================
    # ⚽ Sport Organizations
    # =====================

    "FIFA": "فیفا (FIFA)",

    "UEFA": "یوفا (UEFA)",

    "World Cup": "جام جهانی (World Cup)",

    "Champions League": "لیگ قهرمانان اروپا (Champions League)",

    "Premier League": "لیگ برتر انگلیس (Premier League)",

    "Serie A": "سری آ (Serie A)",

    "La Liga": "لالیگا (La Liga)",

    "Bundesliga": "بوندسلیگا (Bundesliga)",

    "NBA": "ان‌بی‌ای (NBA)",

    "Formula 1": "فرمول یک (Formula 1)",

    "MotoGP": "موتوجی‌پی (MotoGP)",

    "UFC": "یو‌اف‌سی (UFC)",



    # =====================
    # ⚽ Teams
    # =====================

    "Manchester United":
        "منچستر یونایتد (Manchester United)",

    "Manchester City":
        "منچستر سیتی (Manchester City)",

    "Real Madrid":
        "رئال مادرید (Real Madrid)",

    "Barcelona":
        "بارسلونا (Barcelona)",

    "Liverpool":
        "لیورپول (Liverpool)",

    "Arsenal":
        "آرسنال (Arsenal)",

    "Chelsea":
        "چلسی (Chelsea)",

    "Bayern Munich":
        "بایرن مونیخ (Bayern Munich)",

    "Paris Saint-Germain":
        "پاری‌سن‌ژرمن (Paris Saint-Germain)",

    "PSG":
        "پاری‌سن‌ژرمن (PSG)",

    "Juventus":
        "یوونتوس (Juventus)",



    # =====================
    # 📰 Media / Sports Names
    # =====================

    "Fabrizio Romano":
        "فابریتزیو رومانو (Fabrizio Romano)",

    "Di Marzio":
        "دی‌مارزیو (Di Marzio)",



}



# =====================
# Countries
# =====================

COUNTRIES = {

    "United States": "آمریکا",
    "United Kingdom": "بریتانیا",

    "Iran": "ایران",
    "Israel": "اسرائیل",

    "Russia": "روسیه",
    "Ukraine": "اوکراین",

    "China": "چین",

    "France": "فرانسه",
    "Germany": "آلمان",

    "Spain": "اسپانیا",

    "Argentina": "آرژانتین",

    "England": "انگلیس",

}





# =====================
# People
# =====================

PEOPLE = {

    "Donald Trump": "دونالد ترامپ",

    "Joe Biden": "جو بایدن",

    "Elon Musk": "ایلان ماسک",

    "Sam Altman": "سم آلتمن",

    "Mark Zuckerberg": "مارک زاکربرگ",

    "Lionel Messi": "لیونل مسی",

    "Cristiano Ronaldo":
        "کریستیانو رونالدو",

    "Kylian Mbappe":
        "کیلیان امباپه",

    "Lamine Yamal":
        "لامین یامال",

}





def replace_case_insensitive(text, old, new):

    pattern = re.compile(

        re.escape(old),

        re.IGNORECASE

    )

    return pattern.sub(new, text)







def replace_official_names(text):


    if not text:

        return ""



    # جلوگیری از دوبار شدن
    for key, value in BRAND_DICTIONARY.items():

        if value not in text:

            text = replace_case_insensitive(

                text,

                key,

                value

            )




    for key, value in COUNTRIES.items():

        text = replace_case_insensitive(

            text,

            key,

            value

        )




    for key, value in PEOPLE.items():

        text = replace_case_insensitive(

            text,

            key,

            value

        )



    return text.strip()
  # =====================================================
# ⚽ Teams
# =====================================================


TEAMS = {


    "Manchester United":
        "منچستر یونایتد (Manchester United)",


    "Manchester City":
        "منچستر سیتی (Manchester City)",


    "Liverpool":
        "لیورپول (Liverpool)",


    "Arsenal":
        "آرسنال (Arsenal)",


    "Chelsea":
        "چلسی (Chelsea)",


    "Real Madrid":
        "رئال مادرید (Real Madrid)",


    "Barcelona":
        "بارسلونا (Barcelona)",


    "Bayern Munich":
        "بایرن مونیخ (Bayern Munich)",


    "Paris Saint-Germain":
        "پاری‌سن‌ژرمن (Paris Saint-Germain)",


    "PSG":
        "پاری‌سن‌ژرمن (PSG)",


    "Juventus":
        "یوونتوس (Juventus)",


    "Inter Milan":
        "اینتر میلان (Inter Milan)",


    "AC Milan":
        "آث میلان (AC Milan)",


    "Borussia Dortmund":
        "بوروسیا دورتموند (Borussia Dortmund)",


    "Ajax":
        "آژاکس (Ajax)",


}






# =====================================================
# 👤 People
# =====================================================


PEOPLE = {


    # Politics / Technology


    "Donald Trump":
        "دونالد ترامپ",


    "Joe Biden":
        "جو بایدن",


    "Elon Musk":
        "ایلان ماسک",


    "Sam Altman":
        "سم آلتمن",


    "Mark Zuckerberg":
        "مارک زاکربرگ",



    # Football Players


    "Lionel Messi":
        "لیونل مسی",


    "Cristiano Ronaldo":
        "کریستیانو رونالدو",


    "Kylian Mbappe":
        "کیلیان امباپه",


    "Erling Haaland":
        "ارلینگ هالند",


    "Lamine Yamal":
        "لامین یامال",


    "Neymar":
        "نیمار",


    "Mohamed Salah":
        "محمد صلاح",


}






# =====================================================
# 🌍 Countries
# =====================================================


COUNTRIES = {


    "United States":
        "آمریکا",


    "United Kingdom":
        "بریتانیا",


    "England":
        "انگلیس",


    "Iran":
        "ایران",


    "Israel":
        "اسرائیل",


    "Russia":
        "روسیه",


    "Ukraine":
        "اوکراین",


    "China":
        "چین",


    "France":
        "فرانسه",


    "Germany":
        "آلمان",


    "Spain":
        "اسپانیا",


    "Italy":
        "ایتالیا",


    "Portugal":
        "پرتغال",


    "Argentina":
        "آرژانتین",


    "Brazil":
        "برزیل",


    "Japan":
        "ژاپن",


    "South Korea":
        "کره جنوبی",


}






# =====================================================
# 🏳️ Country Flags
# =====================================================


COUNTRY_FLAGS = {


    "آمریکا":
        "🇺🇸",


    "بریتانیا":
        "🇬🇧",


    "انگلیس":
        "🏴",


    "ایران":
        "🇮🇷",


    "اسرائیل":
        "🇮🇱",


    "روسیه":
        "🇷🇺",


    "اوکراین":
        "🇺🇦",


    "چین":
        "🇨🇳",


    "فرانسه":
        "🇫🇷",


    "آلمان":
        "🇩🇪",


    "اسپانیا":
        "🇪🇸",


    "ایتالیا":
        "🇮🇹",


    "پرتغال":
        "🇵🇹",


    "آرژانتین":
        "🇦🇷",


    "برزیل":
        "🇧🇷",


    "ژاپن":
        "🇯🇵",


    "کره جنوبی":
        "🇰🇷",


}






# =====================================================
# 📰 Media Sources
# =====================================================


MEDIA_FLAGS = {


    "Reuters":
        "🇬🇧",


    "BBC":
        "🇬🇧",


    "CNN":
        "🇺🇸",


    "New York Times":
        "🇺🇸",


    "The Guardian":
        "🇬🇧",


    "Al Jazeera":
        "🇶🇦",


    "Iran International":
        "🇬🇧",


    "Tasnim":
        "🇮🇷",


    "Fars":
        "🇮🇷",


    "Khabar Fori":
        "🇮🇷",


    "ESPN":
        "🇺🇸",


    "FIBA":
        "🌍",


    "NBA":
        "🇺🇸",


    "FIFA":
        "🌍",


}






# =====================================================
# Replace Engine
# =====================================================


def replace_case_insensitive(text, old, new):


    pattern = re.compile(

        re.escape(old),

        re.IGNORECASE

    )


    return pattern.sub(

        new,

        text

    )






def replace_official_names(text):


    if not text:

        return ""



    dictionaries = [


        BRANDS,

        TEAMS,

        COUNTRIES,

        PEOPLE,

    ]



    for dictionary in dictionaries:


        for key, value in dictionary.items():


            text = replace_case_insensitive(

                text,

                key,

                value

            )



    return text.strip()






def add_country_flags(text):


    if not text:

        return ""



    for country, flag in COUNTRY_FLAGS.items():


        if country in text and not flag in text:


            text = text.replace(

                country,

                f"{flag} {country}"

            )



    return text






def format_media_source(source):


    if not source:

        return "🌐 Unknown"



    flag = MEDIA_FLAGS.get(

        source,

        "🌐"

    )


    return f"{flag} {source}"
