"""
KhabarF24 Configuration v8.0
تمام تنظیمات پروژه در یک فایل
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# Telegram Settings
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@KhabarF24")

# ==========================
# Scheduler
# ==========================
CHECK_INTERVAL = 300          # ۵ دقیقه (پیشنهاد: برای تست می‌تونی ۶۰ کنی)
MAX_NEWS_PER_CYCLE = 3        # حداکثر خبر در هر چرخه

# ==========================
# Network & Timeout
# ==========================
RSS_TIMEOUT = 20
REQUEST_TIMEOUT = 20
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

# ==========================
# Categories Control
# ==========================
ENABLED_CATEGORIES = {
    "politics": True,
    "iran": True,
    "world": True,
    "sport": True,
    "economy": True,
    "technology": True,
    "gaming": True,
    "health": True,
}

# ==========================
# Limits
# ==========================
MAX_POSTS_PER_HOUR = 30
MIN_QUALITY_SCORE = 55
MIN_IMPORTANCE_SCORE = 5

# ==========================
# AI & Processing
# ==========================
ENABLE_TRANSLATION = True
ENABLE_REWRITER = True        # طبیعی‌سازی فارسی
ENABLE_SUMMARY = True

# ==========================
# Images
# ==========================
ENABLE_NEWS_IMAGE = True
WATERMARK_TEXT = "KhabarF24"

# ==========================
# Logging
# ==========================
LOG_LEVEL = "INFO"            # DEBUG / INFO / WARNING

# ==========================
# Development
# ==========================
DEBUG_MODE = False            # اگر True باشد، فقط لاگ می‌زنه و پست نمی‌کنه
