"""
brand_dictionary.py

KhabarF24 Official Names Dictionary v4.1

نام رسمی فارسی + نام اصلی
"""

BRAND_DICTIONARY = {


    # ⚽ Football Clubs

    "Manchester United": "منچستر یونایتد (Manchester United)",
    "Manchester City": "منچستر سیتی (Manchester City)",
    "Real Madrid": "رئال مادرید (Real Madrid)",
    "Barcelona": "بارسلونا (Barcelona)",
    "FC Barcelona": "بارسلونا (Barcelona)",
    "Liverpool": "لیورپول (Liverpool)",
    "Arsenal": "آرسنال (Arsenal)",
    "Chelsea": "چلسی (Chelsea)",
    "Bayern Munich": "بایرن مونیخ (Bayern Munich)",
    "Paris Saint-Germain": "پاری‌سن‌ژرمن (Paris Saint-Germain)",
    "PSG": "پاری‌سن‌ژرمن (PSG)",
    "Inter Milan": "اینتر میلان (Inter Milan)",
    "AC Milan": "آث میلان (AC Milan)",
    "Juventus": "یوونتوس (Juventus)",
    "Borussia Dortmund": "بوروسیا دورتموند (Borussia Dortmund)",
    "Atletico Madrid": "اتلتیکو مادرید (Atletico Madrid)",


    # 👤 Players

    "Lionel Messi": "لیونل مسی (Lionel Messi)",
    "Cristiano Ronaldo": "کریستیانو رونالدو (Cristiano Ronaldo)",
    "Kylian Mbappe": "کیلیان امباپه (Kylian Mbappe)",
    "Jude Bellingham": "جود بلینگهام (Jude Bellingham)",
    "Lamine Yamal": "لامین یامال (Lamine Yamal)",
    "Erling Haaland": "ارلینگ هالند (Erling Haaland)",
    "Mohamed Salah": "محمد صلاح (Mohamed Salah)",
    "Vinicius Junior": "وینیسیوس جونیور (Vinicius Junior)",


    # 🏀 Basketball

    "NBA": "NBA",
    "WNBA": "WNBA",
    "Los Angeles Lakers": "لس‌آنجلس لیکرز (Los Angeles Lakers)",
    "Boston Celtics": "بوستون سلتیکس (Boston Celtics)",
    "Minnesota Lynx": "مینه‌سوتا لینکس (Minnesota Lynx)",
    "LeBron James": "لبران جیمز (LeBron James)",


    # 🏆 Organizations

    "FIFA": "فیفا (FIFA)",
    "UEFA": "یوفا (UEFA)",
    "AFC": "کنفدراسیون فوتبال آسیا (AFC)",
    "FIVB": "فدراسیون جهانی والیبال (FIVB)",
    "United World Wrestling": "اتحادیه جهانی کشتی (UWW)",
    "ATP": "ATP",
    "WTA": "WTA",
    "Formula 1": "فرمول یک (Formula 1)",


    # 💻 Technology

    "Apple": "اپل (Apple)",
    "Google": "گوگل (Google)",
    "Microsoft": "مایکروسافت (Microsoft)",
    "OpenAI": "اوپن‌ای‌آی (OpenAI)",
    "Tesla": "تسلا (Tesla)",
    "NVIDIA": "انویدیا (NVIDIA)",


    # 🎮 Gaming

    "Assassin's Creed": "اساسینز کرید (Assassin's Creed)",
    "PlayStation": "پلی‌استیشن (PlayStation)",
    "Xbox": "ایکس‌باکس (Xbox)",
    "Steam": "استیم (Steam)",

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
