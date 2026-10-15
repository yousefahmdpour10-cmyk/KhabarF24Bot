"""
Shared Header Builder

تمام تمپلیت‌ها (world, iran, politics, ... و هر رشته‌ی ورزشی) هدر پست
را از همین تابع می‌سازند، تا منطق «خبر فوری» فقط در یک‌جا نگه‌داری شود.
"""

from app.formatter.footer import DIVIDER

BREAKING_LABEL = "🚨 خبر فوری 🚨"


def build_header(normal_line: str, is_breaking: bool = False) -> str:
    """
    normal_line: مثلاً "🌍 جهان" یا "سیاست 🔴" یا "⚽ فوتبال"
    is_breaking: اگر True باشد، به‌جای normal_line همیشه "🚨 خبر فوری 🚨"
                 نمایش داده می‌شود (دسته‌بندی موضوعی در هدر دیده نمی‌شود،
                 ولی هشتگ پایین پست همچنان موضوع واقعی خبر را نشان می‌دهد).
    """

    line = BREAKING_LABEL if is_breaking else normal_line

    return (
        f"{DIVIDER}\n"
        f"🔴 KhabarF24 | {line}\n"
        f"{DIVIDER}"
    )
