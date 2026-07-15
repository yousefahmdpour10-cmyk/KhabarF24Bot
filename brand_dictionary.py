"""
brand_dictionary.py

KhabarF24 Official Names Dictionary v4.5

حفظ نام رسمی:
- باشگاه‌ها
- بازیکنان
- لیگ‌ها
- برندها
- فناوری
- بازی‌ها
"""


BRAND_DICTIONARY = {


    # =========================
    # ⚽ Football Clubs
    # =========================

    "Manchester United":
        "منچستر یونایتد (Manchester United)",

    "Manchester City":
        "منچستر سیتی (Manchester City)",

    "Real Madrid":
        "رئال مادرید (Real Madrid)",

    "Barcelona":
        "بارسلونا (Barcelona)",

    "FC Barcelona":
        "بارسلونا (FC Barcelona)",

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

    "Inter Milan":
        "اینتر میلان (Inter Milan)",

    "AC Milan":
        "آث میلان (AC Milan)",

    "Juventus":
        "یوونتوس (Juventus)",

    "Borussia Dortmund":
        "بوروسیا دورتموند (Borussia Dortmund)",

    "Atletico Madrid":
        "اتلتیکو مادرید (Atletico Madrid)",



    # =========================
    # 👤 Football Players
    # =========================

    "Lionel Messi":
        "لیونل مسی (Lionel Messi)",

    "Cristiano Ronaldo":
        "کریستیانو رونالدو (Cristiano Ronaldo)",

    "Kylian Mbappe":
        "کیلیان امباپه (Kylian Mbappe)",

    "Jude Bellingham":
        "جود بلینگهام (Jude Bellingham)",

    "Lamine Yamal":
        "لامین یامال (Lamine Yamal)",

    "Erling Haaland":
        "ارلینگ هالند (Erling Haaland)",

    "Mohamed Salah":
        "محمد صلاح (Mohamed Salah)",

    "Vinicius Junior":
        "وینیسیوس جونیور (Vinicius Junior)",

    "Folarin Balogun":
        "فولارین بالوگون (Folarin Balogun)",



    # =========================
    # 🏀 Basketball
    # =========================

    "NBA":
        "NBA",

    "WNBA":
        "WNBA",

    "Los Angeles Lakers":
        "لس‌آنجلس لیکرز (Los Angeles Lakers)",

    "Boston Celtics":
        "بوستون سلتیکس (Boston Celtics)",

    "Minnesota Lynx":
        "مینه‌سوتا لینکس (Minnesota Lynx)",

    "Phoenix Mercury":
        "فینیکس مرکوری (Phoenix Mercury)",

    "LeBron James":
        "لبران جیمز (LeBron James)",



    # =========================
    # 🏆 Sports Organizations
    # =========================

    "FIFA":
        "فیفا (FIFA)",

    "UEFA":
        "یوفا (UEFA)",

    "AFC":
        "کنفدراسیون فوتبال آسیا (AFC)",

    "Premier League":
        "لیگ برتر انگلیس (Premier League)",

    "LaLiga":
        "لالیگا (LaLiga)",

    "Serie A":
        "سری آ (Serie A)",

    "Bundesliga":
        "بوندسلیگا (Bundesliga)",

    "Formula 1":
        "فرمول یک (Formula 1)",



    # =========================
    # 💻 Technology
    # =========================

    "Apple":
        "اپل (Apple)",

    "Google":
        "گوگل (Google)",

    "Microsoft":
        "مایکروسافت (Microsoft)",

    "OpenAI":
        "OpenAI (اوپن‌ای‌آی)",

    "ChatGPT":
        "ChatGPT",

    "Tesla":
        "تسلا (Tesla)",

    "NVIDIA":
        "انویدیا (NVIDIA)",

    "Samsung":
        "سامسونگ (Samsung)",

    "Meta":
        "متا (Meta)",

    "Netflix":
        "نتفلیکس (Netflix)",

    "Boston Dynamics":
        "بوستون داینامیکس (Boston Dynamics)",

    "RingConn":
        "رینگ‌کان (RingConn)",

    "Siri":
        "سیری (Siri)",

    "iPhone":
        "آیفون (iPhone)",

    "iPad":
        "آیپد (iPad)",

    "iOS":
        "iOS",



    # =========================
    # 🎮 Gaming
    # =========================

    "Assassin's Creed":
        "اساسینز کرید (Assassin's Creed)",

    "Ubisoft":
        "یوبی‌سافت (Ubisoft)",

    "PlayStation":
        "پلی‌استیشن (PlayStation)",

    "Xbox":
        "ایکس‌باکس (Xbox)",

    "Nintendo":
        "نینتندو (Nintendo)",

    "Steam":
        "استیم (Steam)",



    # =========================
    # 📰 Media
    # =========================

    "BBC":
        "بی‌بی‌سی (BBC)",

    "CNN":
        "سی‌ان‌ان (CNN)",

    "ESPN":
        "ESPN",

    "The Verge":
        "د ورج (The Verge)",

    "TechCrunch":
        "تک‌کرانچ (TechCrunch)",

    "New York Times":
        "نیویورک تایمز (New York Times)",

}



def replace_official_names(text):

    if not text:
        return ""


    # اول موارد طولانی‌تر جایگزین شوند
    # تا FC Barcelona قبل از Barcelona خراب نشود

    sorted_names = sorted(
        BRAND_DICTIONARY.keys(),
        key=len,
        reverse=True
    )


    for english in sorted_names:

        persian = BRAND_DICTIONARY[english]

        text = text.replace(
            english,
            persian
        )


    return text
