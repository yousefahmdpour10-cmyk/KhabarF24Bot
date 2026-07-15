"""
KhabarF24 Brand Dictionary v4.6

نام‌های رسمی:
- کشورها
- مکان‌ها
- تیم‌ها
- بازیکنان
- برندها
"""


BRAND_DICTIONARY = {


    # 🌍 Countries

    "Iran": "ایران",

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

    "United States":
    "آمریکا",

    "United Kingdom":
    "بریتانیا",



    # 👤 People

    "Donald Trump":
    "دونالد ترامپ",

    "Trump":
    "ترامپ",

    "Joe Biden":
    "جو بایدن",



    # ⚽ Clubs

    "Manchester United":
    "منچستر یونایتد",

    "Manchester City":
    "منچستر سیتی",

    "Real Madrid":
    "رئال مادرید",

    "Barcelona":
    "بارسلونا",

    "FC Barcelona":
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



    # ⚽ Players

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



    # 💻 Technology

    "Apple":
    "اپل",

    "Google":
    "گوگل",

    "Microsoft":
    "مایکروسافت",

    "OpenAI":
    "OpenAI",

    "ChatGPT":
    "ChatGPT",

    "Boston Dynamics":
    "بوستون داینامیکس",

    "RingConn":
    "رینگ‌کان",

    "Siri":
    "سیری",

    "iPhone":
    "آیفون",

    "iOS":
    "iOS",



    # 🎮 Gaming

    "Assassin's Creed":
    "اساسینز کرید",

    "PlayStation":
    "پلی‌استیشن",

    "Xbox":
    "ایکس‌باکس",



    # 📰 Media

    "BBC":
    "بی‌بی‌سی",

    "CNN":
    "سی‌ان‌ان",

    "Al Jazeera":
    "الجزیره",

    "ESPN":
    "ESPN",

    "The Verge":
    "د ورج",

    "TechCrunch":
    "تک‌کرانچ",

}



def replace_official_names(text):

    if not text:
        return ""


    # موارد طولانی‌تر اول جایگزین شوند

    names = sorted(
        BRAND_DICTIONARY.keys(),
        key=len,
        reverse=True
    )


    for name in names:

        text = text.replace(
            name,
            BRAND_DICTIONARY[name]
        )


    return text
