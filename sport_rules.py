"""
KhabarF24 Sport Rules v1.0

قوانین هوشمند اهمیت اخبار ورزشی

هدف:
- تشخیص بازی‌های مهم
- تشخیص رویدادهای مهم ورزشی
- کمک به Importance Engine
"""


# =========================
# ⭐ تیم‌های مهم
# =========================

BIG_TEAMS = [

    # باشگاه‌ها

    "manchester united",
    "manchester city",
    "liverpool",
    "arsenal",
    "chelsea",

    "real madrid",
    "barcelona",
    "bayern munich",

    "paris saint-germain",
    "psg",

    "juventus",
    "inter",
    "milan",

    # تیم‌های ملی

    "iran",
    "england",
    "argentina",
    "brazil",
    "france",
    "spain",
    "germany",
    "portugal",

]



# =========================
# 🏆 مسابقات مهم
# =========================

BIG_COMPETITIONS = [

    "world cup",
    "جام جهانی",

    "champions league",
    "لیگ قهرمانان",

    "premier league",
    "لیگ برتر",

    "la liga",
    "laliga",

    "serie a",

    "bundesliga",

    "europa league",

    "final",
    "فینال",

    "semi final",
    "نیمه نهایی",

    "quarter final",
    "یک چهارم نهایی",

]



# =========================
# ⚽ رویدادهای مهم بازی
# =========================

IMPORTANT_EVENTS = [

    # نتیجه

    "score",
    "result",
    "نتیجه",
    "پایان بازی",
    "برد",
    "باخت",
    "پیروز",


    # گل

    "goal",
    "گل",
    "گلزن",
    "hat trick",
    "هت تریک",


    # کارت

    "red card",
    "کارت قرمز",
    "اخراج",


    # داوری

    "var",
    "داوری",
    "اشتباه داوری",


    # نیمه

    "half time",
    "نیمه اول",
    "نیمه دوم",


]



# =========================
# 👥 ترکیب تیم‌ها
# =========================

LINEUP_WORDS = [

    "lineup",
    "starting xi",
    "starting eleven",

    "ترکیب رسمی",
    "ترکیب تیم",
    "یازده نفره",

]



# =========================
# 🔄 نقل و انتقالات
# =========================

TRANSFER_WORDS = [

    "transfer",
    "انتقال",
    "نقل و انتقالات",

    "contract",
    "قرارداد",

    "renew",
    "تمدید",

    "sacked",
    "اخراج مربی",

]



# =========================
# توابع کمکی
# =========================


def normalize(text):

    if not text:
        return ""

    return text.lower()



def contains_any(text, words):

    text = normalize(text)

    for word in words:

        if word.lower() in text:

            return True

    return False





# =========================
# تشخیص بازی بزرگ
# =========================


def is_big_match(title="", summary=""):


    text = f"""
    {title}
    {summary}
    """



    has_team = contains_any(
        text,
        BIG_TEAMS
    )


    has_competition = contains_any(
        text,
        BIG_COMPETITIONS
    )


    return (
        has_team
        or
        has_competition
    )






# =========================
# امتیاز ورزشی
# =========================


def calculate_sport_score(
        title="",
        summary=""
):


    text = f"""
    {title}
    {summary}
    """



    score = 0



    # بازی بزرگ

    if is_big_match(
        title,
        summary
    ):

        score += 3



    # مسابقات مهم

    if contains_any(
        text,
        BIG_COMPETITIONS
    ):

        score += 3



    # رویداد بازی

    if contains_any(
        text,
        IMPORTANT_EVENTS
    ):

        score += 2



    # ترکیب رسمی

    if contains_any(
        text,
        LINEUP_WORDS
    ):

        if is_big_match(
            title,
            summary
        ):

            score += 3



    # نقل و انتقال

    if contains_any(
        text,
        TRANSFER_WORDS
    ):

        score += 3



    # محدود کردن امتیاز

    if score > 10:

        score = 10



    return score
