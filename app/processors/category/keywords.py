"""
Category Keywords

کلمات کلیدی تشخیص دسته‌بندی خبر
"""

CATEGORY_KEYWORDS = {

    "politics": [
        "رئیس جمهور",
        "وزیر",
        "دولت",
        "پارلمان",
        "مجلس",
        "انتخابات",
        "دیپلماسی",
        "تحریم",
        "سیاست",
        "سفیر",
        "نخست وزیر",
        "کاخ سفید",
        "کرملین",
        "وزارت خارجه",
        "NATO",
        "UN",
        "Pentagon",
        "White House",
        "President",
        "Prime Minister",
        "Government",
        "Election",
        "Parliament",
        "Diplomacy",
        "Sanctions"
    ],

    "war": [
        "جنگ",
        "حمله",
        "موشک",
        "پهپاد",
        "انفجار",
        "ارتش",
        "نیروی هوایی",
        "پدافند",
        "درگیری",
        "حماس",
        "اسرائیل",
        "اوکراین",
        "روسیه",
        "Israel",
        "Missile",
        "Drone",
        "Airstrike",
        "Army",
        "Military"
    ],

    # هر خبری که به ایران مربوط باشد (فارغ از موضوع)؛ اگر خبر هم‌زمان
    # کلیدواژه‌های سیاسی/جنگی قوی‌تری داشته باشد، بر اساس تعداد تطبیق
    # کلیدواژه‌ها به‌طور طبیعی همان دسته (politics/war) انتخاب می‌شود.
    "iran": [
        "ایران",
        "ایرانی",
        "تهران",
        "تهرانی",
        "اصفهان",
        "شیراز",
        "مشهد",
        "تبریز",
        "یزد",
        "کرمان",
        "اهواز",
        "قم",
        "Iran",
        "Iranian",
        "Tehran"
    ],

    "economy": [
        "دلار",
        "یورو",
        "بورس",
        "اقتصاد",
        "بانک",
        "تورم",
        "طلا",
        "نفت",
        "گاز",
        "بازار",
        "Bitcoin",
        "Oil",
        "Gold",
        "Inflation",
        "Economy",
        "Stock",
        "Bank"
    ],

    "technology": [
        "هوش مصنوعی",
        "ربات",
        "فناوری",
        "اپل",
        "گوگل",
        "مایکروسافت",
        "OpenAI",
        "AI",
        "Artificial Intelligence",
        "Google",
        "Apple",
        "Microsoft",
        "Tesla",
        "SpaceX"
    ],

    "health": [
        "سلامت",
        "بیمار",
        "پزشک",
        "دارو",
        "واکسن",
        "ویروس",
        "Hospital",
        "Health",
        "Medicine",
        "COVID"
    ],

    "weather": [
        "هواشناسی",
        "بارندگی",
        "بارش",
        "طوفان",
        "زلزله",
        "سیل",
        "گرما",
        "سرما",
        "Weather",
        "Storm",
        "Flood",
        "Earthquake"
    ],

    # مفرد، چون Formatter و SportDetector هر دو با کلید "sport" کار می‌کنند
    "sport": [
        "فوتبال",
        "بسکتبال",
        "والیبال",
        "تنیس",
        "کشتی",
        "فرمول یک",
        "المپیک",
        "ورزش",
        "Football",
        "Basketball",
        "Volleyball",
        "Tennis",
        "Olympics"
    ]

}
