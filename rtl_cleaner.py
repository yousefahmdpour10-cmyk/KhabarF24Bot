"""
KhabarF24 RTL Cleaner v2.0

Fix:
- English entities at beginning of Persian sentences
- RTL/LTR mixing
- Company names
- Sports clubs
- Countries
"""


import re



ENGLISH_TO_PERSIAN = {


    # Technology

    "Thinking Machines": "تینکینگ ماشینز",

    "Apple": "اپل",

    "Google": "گوگل",

    "Microsoft": "مایکروسافت",

    "OpenAI": "OpenAI",

    "Tesla": "تسلا",

    "NVIDIA": "انویدیا",

    "Anthropic": "آنتروپیک",

    "Claude": "کلود",

    "Gemini": "جمینای",

    "Grok": "گروک",

    "Boston Dynamics": "بوستون داینامیکس",



    # Sports

    "Manchester United": "منچستر یونایتد",

    "Manchester City": "منچستر سیتی",

    "Real Madrid": "رئال مادرید",

    "Barcelona": "بارسلونا",

    "Liverpool": "لیورپول",



    # Countries

    "United States": "آمریکا",

    "USA": "آمریکا",

    "US": "آمریکا",

    "UK": "بریتانیا",

    "Iran": "ایران",

    "Iraq": "عراق",

    "Israel": "اسرائیل",

}





COMPANY_NAMES = [

    "Thinking Machines",

    "Apple",

    "Google",

    "Microsoft",

    "OpenAI",

    "Anthropic",

    "Boston Dynamics",

    "Tesla",

    "NVIDIA",

]



CLUB_NAMES = [

    "Manchester United",

    "Manchester City",

    "Real Madrid",

    "Barcelona",

    "Liverpool",

    "Arsenal",

]





def replace_english_names(text):

    if not text:
        return ""


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


    text = " ".join(
        text.split()
    )


    # اول اسم‌های رسمی را تبدیل کن

    text = replace_english_names(
        text
    )



    # اگر هنوز جمله با انگلیسی شروع شد

    for company in COMPANY_NAMES:

        if text.startswith(company):

            text = text.replace(
                company,
                "شرکت " + company,
                1
            )

            return text



    for club in CLUB_NAMES:

        if text.startswith(club):

            text = text.replace(
                club,
                "باشگاه " + club,
                1
            )

            return text



    # علائم نگارشی

    text = re.sub(
        r"\s+([،.!؟])",
        r"\1",
        text
    )


    text = text.replace(
        " - ",
        " – "
    )


    return text.strip()
