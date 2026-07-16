"""
KhabarF24 Brand Dictionary v5.0

Rules:
- Companies: Persian + English in parentheses
- People/Countries/Teams: Persian only
- Media sources remain original
"""


BRAND_DICTIONARY = {


    # =====================
    # 💻 Technology Companies
    # =====================


    "OpenAI": "اوپن‌ای‌آی (OpenAI)",

    "ChatGPT": "چت‌جی‌پی‌تی (ChatGPT)",

    "Google DeepMind": "گوگل دیپ‌مایند (Google DeepMind)",

    "DeepMind": "دیپ‌مایند (DeepMind)",

    "Anthropic": "آنتروپیک (Anthropic)",

    "Claude": "کلود (Claude)",

    "Gemini": "جمینای (Gemini)",

    "Microsoft": "مایکروسافت (Microsoft)",

    "Apple": "اپل (Apple)",

    "Google": "گوگل (Google)",

    "Meta": "متا (Meta)",

    "Facebook": "فیس‌بوک (Facebook)",

    "Instagram": "اینستاگرام (Instagram)",

    "Amazon": "آمازون (Amazon)",

    "Tesla": "تسلا (Tesla)",

    "NVIDIA": "انویدیا (NVIDIA)",

    "Samsung": "سامسونگ (Samsung)",

    "Huawei": "هواوی (Huawei)",

    "TikTok": "تیک‌تاک (TikTok)",

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



    # =====================
    # 🏢 Companies
    # =====================


    "Tesla Inc.": "شرکت تسلا (Tesla Inc.)",

    "SpaceX": "اسپیس‌ایکس (SpaceX)",

    "Boston Dynamics": "بوستون داینامیکس (Boston Dynamics)",



    # =====================
    # 🌍 Countries
    # =====================


    "United States": "آمریکا",

    "United Kingdom": "بریتانیا",

    "Iran": "ایران",

    "Israel": "اسرائیل",

    "Ukraine": "اوکراین",

    "Russia": "روسیه",

    "China": "چین",

    "France": "فرانسه",

    "Germany": "آلمان",

    "Spain": "اسپانیا",

    "Argentina": "آرژانتین",

    "England": "انگلیس",



    # =====================
    # 👤 People
    # =====================


    "Donald Trump": "دونالد ترامپ",

    "Joe Biden": "جو بایدن",

    "Elon Musk": "ایلان ماسک",

    "Sam Altman": "سم آلتمن",

    "Mark Zuckerberg": "مارک زاکربرگ",

    "Lionel Messi": "لیونل مسی",

    "Cristiano Ronaldo": "کریستیانو رونالدو",

    "Kylian Mbappe": "کیلیان امباپه",

    "Lamine Yamal": "لامین یامال",



    # =====================
    # ⚽ Teams
    # =====================


    "Manchester United": "منچستر یونایتد",

    "Manchester City": "منچستر سیتی",

    "Real Madrid": "رئال مادرید",

    "Barcelona": "بارسلونا",

    "Liverpool": "لیورپول",

    "Arsenal": "آرسنال",

    "Chelsea": "چلسی",

    "Bayern Munich": "بایرن مونیخ",

    "Paris Saint-Germain": "پاری‌سن‌ژرمن",

    "PSG": "پاری‌سن‌ژرمن",

    "Juventus": "یوونتوس",


}





def replace_official_names(text):


    if not text:

        return ""



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
