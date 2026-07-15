"""
KhabarF24 Brand Dictionary v4.7

حفظ نام‌های رسمی:
- کشورها
- مکان‌ها
- تیم‌ها
- بازیکنان
- برندها
- شرکت‌های فناوری
- رسانه‌ها
- سازمان‌های ورزشی
"""


BRAND_DICTIONARY = {


    # 🌍 Countries

    "Islamic Republic of Iran": "جمهوری اسلامی ایران",

    "United States": "آمریکا",

    "United Kingdom": "بریتانیا",

    "Iran": "ایران",

    "Israel": "اسرائیل",

    "Israeli": "اسرائیلی",

    "Lebanon": "لبنان",

    "Yemen": "یمن",

    "Gaza": "غزه",

    "Ukraine": "اوکراین",

    "Russia": "روسیه",

    "China": "چین",

    "France": "فرانسه",

    "Spain": "اسپانیا",

    "Argentina": "آرژانتین",

    "England": "انگلیس",



    # 👤 People

    "Donald Trump": "دونالد ترامپ",

    "Joe Biden": "جو بایدن",

    "Lionel Messi": "لیونل مسی",

    "Cristiano Ronaldo": "کریستیانو رونالدو",

    "Kylian Mbappe": "کیلیان امباپه",

    "Lamine Yamal": "لامین یامال",

    "Jude Bellingham": "جود بلینگهام",

    "Erling Haaland": "ارلینگ هالند",



    # ⚽ Football Clubs

    "Manchester United": "منچستر یونایتد",

    "Manchester City": "منچستر سیتی",

    "Real Madrid": "رئال مادرید",

    "FC Barcelona": "بارسلونا",

    "Barcelona": "بارسلونا",

    "Liverpool": "لیورپول",

    "Arsenal": "آرسنال",

    "Chelsea": "چلسی",

    "Bayern Munich": "بایرن مونیخ",

    "Paris Saint-Germain": "پاری‌سن‌ژرمن",

    "PSG": "پاری‌سن‌ژرمن",

    "Juventus": "یوونتوس",

    "Borussia Dortmund": "بوروسیا دورتموند",



    # 🏆 Sports Organizations

    "Premier League": "لیگ برتر انگلیس",

    "Champions League": "لیگ قهرمانان اروپا",

    "FIFA": "فیفا",

    "UEFA": "یوفا",

    "AFC": "کنفدراسیون فوتبال آسیا",

    "FIVB": "فدراسیون جهانی والیبال",

    "NBA": "NBA",

    "WNBA": "WNBA",

    "ATP": "ATP",

    "WTA": "WTA",

    "Formula 1": "فرمول یک",



    # 💻 Technology

    "Thinking Machines": "تینکینگ ماشینز",

    "Inkling": "اینکلینگ",

    "Anthropic": "آنتروپیک",

    "Claude": "کلود",

    "Google DeepMind": "گوگل دیپ‌مایند",

    "DeepMind": "دیپ‌مایند",

    "Gemini": "جمینای",

    "Grok": "گروک",

    "xAI": "xAI",

    "NVIDIA": "انویدیا",

    "Meta": "متا",

    "Tesla": "تسلا",

    "Samsung": "سامسونگ",

    "Amazon": "آمازون",

    "Apple": "اپل",

    "Google": "گوگل",

    "Microsoft": "مایکروسافت",

    "OpenAI": "OpenAI",

    "ChatGPT": "ChatGPT",

    "Boston Dynamics": "بوستون داینامیکس",

    "RingConn": "رینگ‌کان",

    "Siri": "سیری",

    "iPhone": "آیفون",

    "iOS": "iOS",



    # 🎮 Gaming

    "Assassin's Creed": "اساسینز کرید",

    "PlayStation": "پلی‌استیشن",

    "Xbox": "ایکس‌باکس",

    "Nintendo": "نینتندو",

    "Steam": "استیم",



    # 📰 Media

    "Al Jazeera": "الجزیره",

    "TechCrunch": "تک‌کرانچ",

    "The Verge": "د ورج",

    "BBC": "بی‌بی‌سی",

    "CNN": "سی‌ان‌ان",

    "Reuters": "رویترز",

    "ESPN": "ESPN",

    "New York Times": "نیویورک تایمز",

    "NYTimes": "نیویورک تایمز",

}





def replace_official_names(text):

    if not text:
        return ""


    # نام‌های طولانی اول پردازش شوند

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


    return text.strip()
