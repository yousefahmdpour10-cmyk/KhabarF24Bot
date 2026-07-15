"""
KhabarF24 RTL Cleaner v1

Fix:
- English words at beginning of Persian sentences
- RTL/LTR mixing
- Hidden direction problems
"""


import re


# کلمات رایج انگلیسی که بهتر است فارسی شوند
ENGLISH_TO_PERSIAN = {

    "Apple": "اپل",
    "Google": "گوگل",
    "Microsoft": "مایکروسافت",
    "OpenAI": "OpenAI",
    "Tesla": "تسلا",
    "NVIDIA": "انویدیا",

    "Manchester United": "منچستر یونایتد",
    "Manchester City": "منچستر سیتی",

    "United States": "ایالات متحده",
    "US": "آمریکا",
    "USA": "آمریکا",

    "UK": "بریتانیا",
    "Iran": "ایران",
    "Iraq": "عراق",
    "Israel": "اسرائیل",

    "Google Maps": "گوگل مپس",
    "Apple Maps": "اپل مپس",

}



def replace_english_names(text):

    if not text:
        return ""


    # طولانی‌ها اول
    items = sorted(
        ENGLISH_TO_PERSIAN.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )


    for english, persian in items:

        text = text.replace(
            english,
            persian
        )


    return text




def fix_rtl_text(text):

    if not text:
        return ""


    # حذف فاصله‌های اضافی
    text = " ".join(
        text.split()
    )


    # اصلاح نام‌ها
    text = replace_english_names(
        text
    )


    # اگر جمله با حرف انگلیسی شروع شد
    if re.match(
        r"^[A-Za-z]",
        text
    ):

        parts = text.split(" ", 1)

        if len(parts) == 2:

            first = parts[0]

            rest = parts[1]

            text = f"{rest} ({first})"



    # فاصله قبل از علائم
    text = re.sub(
        r"\s+([،.!؟])",
        r"\1",
        text
    )


    # جدا کردن خط‌های مشکل‌دار
    text = text.replace(
        " - ",
        " – "
    )


    return text.strip()
