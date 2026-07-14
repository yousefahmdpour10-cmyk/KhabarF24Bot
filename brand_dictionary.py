"""
brand_dictionary.py

KhabarF24 Official Names Dictionary

حفظ نام رسمی:
- باشگاه‌ها
- تیم‌ها
- بازیکنان
- لیگ‌ها
- برندها
"""


BRAND_DICTIONARY = {


    # =========================
    # ⚽ Football Clubs
    # =========================

    "Manchester United": "منچستر یونایتد",
    "Manchester City": "منچستر سیتی",
    "Real Madrid": "رئال مادرید",
    "Barcelona": "بارسلونا",
    "FC Barcelona": "بارسلونا",
    "Liverpool": "لیورپول",
    "Arsenal": "آرسنال",
    "Chelsea": "چلسی",
    "Bayern Munich": "بایرن مونیخ",
    "Paris Saint-Germain": "پاری‌سن‌ژرمن",
    "PSG": "پاری‌سن‌ژرمن",
    "Inter Milan": "اینتر میلان",
    "AC Milan": "آث میلان",
    "Juventus": "یوونتوس",
    "Borussia Dortmund": "بوروسیا دورتموند",
    "Atletico Madrid": "اتلتیکو مادرید",


    # =========================
    # ⚽ Players
    # =========================

    "Lionel Messi": "لیونل مسی",
    "Cristiano Ronaldo": "کریستیانو رونالدو",
    "Kylian Mbappe": "کیلیان امباپه",
    "Jude Bellingham": "جود بلینگهام",
    "Lamine Yamal": "لامین یامال",
    "Erling Haaland": "ارلینگ هالند",
    "Mohamed Salah": "محمد صلاح",
    "Vinicius Junior": "وینیسیوس جونیور",


    # =========================
    # 🏀 Basketball
    # =========================

    "NBA": "NBA",
    "WNBA": "WNBA",
    "Los Angeles Lakers": "لس‌آنجلس لیکرز",
    "Boston Celtics": "بوستون سلتیکس",
    "Minnesota Lynx": "مینه‌سوتا لینکس",
    "LeBron James": "لبران جیمز",


    # =========================
    # 🏐 Other Sports
    # =========================

    "FIFA": "فیفا",
    "UEFA": "یوفا",
    "AFC": "کنفدراسیون فوتبال آسیا",
    "FIVB": "فدراسیون جهانی والیبال",
    "United World Wrestling": "اتحادیه جهانی کشتی",
    "ATP": "ATP",
    "WTA": "WTA",
    "Formula 1": "فرمول یک",


    # =========================
    # 💻 Technology
    # =========================

    "Apple": "اپل",
    "Google": "گوگل",
    "Microsoft": "مایکروسافت",
    "OpenAI": "OpenAI",
    "Tesla": "تسلا",
    "NVIDIA": "انویدیا",


    # =========================
    # 🎮 Gaming
    # =========================

    "Assassin's Creed": "اساسینز کرید",
    "PlayStation": "پلی‌استیشن",
    "Xbox": "ایکس‌باکس",
    "Steam": "استیم",

}



def replace_official_names(text):

    if not text:
        return ""


    for english, persian in BRAND_DICTIONARY.items():

        text = text.replace(
            english,
            persian
        )


    return text
