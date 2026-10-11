"""
Keyword Importance Scores

امتیازدهی بر اساس اهمیت رویداد، نه صرفاً وجود یک کلمه.
"""

KEYWORD_SCORES = {
    # جنگ و امنیت
    "جنگ": 10,
    "اعلام جنگ": 12,
    "حمله": 9,
    "حمله نظامی": 12,
    "حمله هوایی": 11,
    "موشک": 9,
    "حمله موشکی": 12,
    "پهپاد": 7,
    "انفجار": 9,
    "ترور": 10,
    "کشته شدن": 7,
    "کشته شدند": 7,
    "تلفات": 7,
    "درگیری نظامی": 9,
    "آتش بس": 8,
    "وضعیت اضطراری": 8,

    "war": 10,
    "declares war": 12,
    "military attack": 11,
    "airstrike": 10,
    "missile strike": 11,
    "missile": 8,
    "drone attack": 10,
    "explosion": 8,
    "assassination": 10,
    "killed": 6,
    "casualties": 7,
    "ceasefire": 8,
    "state of emergency": 8,

    # حوادث و بلایای طبیعی
    "زلزله": 9,
    "زلزله شدید": 12,
    "سیل": 8,
    "سیل گسترده": 10,
    "طوفان": 7,
    "سونامی": 10,
    "آتش سوزی گسترده": 9,
    "فروپاشی ساختمان": 9,

    "earthquake": 9,
    "major earthquake": 12,
    "flooding": 7,
    "severe flooding": 10,
    "tsunami": 10,
    "wildfire": 8,
    "building collapse": 9,
    "natural disaster": 8,

    # سیاست و تصمیم‌های مهم
    "رئیس جمهور استعفا": 10,
    "استعفای رئیس جمهور": 10,
    "کودتا": 11,
    "انتخابات": 4,
    "نتایج انتخابات": 6,
    "تحریم": 5,
    "تحریم‌های جدید": 7,
    "توافق هسته‌ای": 7,

    "president resigns": 10,
    "presidential resignation": 10,
    "coup": 11,
    "election results": 6,
    "new sanctions": 7,
    "nuclear deal": 7,

    # اقتصاد
    "سقوط بازار": 7,
    "بحران اقتصادی": 8,
    "ورشکستگی بانک": 9,
    "نرخ بهره": 4,
    "تورم": 4,

    "market crash": 7,
    "economic crisis": 8,
    "bank failure": 9,
    "interest rate": 3,
    "inflation": 4,

    # سلامت
    "همه گیری": 9,
    "شیوع بیماری": 7,
    "وضعیت اضطراری بهداشتی": 9,

    "pandemic": 9,
    "disease outbreak": 7,
    "public health emergency": 9,

    # ورزش: امتیاز محدود برای جلوگیری از فوری شدن
    # اخبار عادی مسابقات
    "قهرمانی": 3,
    "قهرمان شد": 4,
    "رکورد جهانی": 5,
    "قهرمانی جهان": 5,
    "گل": 1,
    "گلزنی": 2,
    "فینال": 2,
    "انتقال بازیکن": 2,

    "world record": 5,
    "wins the championship": 4,
    "wins the title": 4,
    "world champion": 4,
    "goal": 1,
    "scores": 1,
    "final": 1,
    "player transfer": 2,
}
