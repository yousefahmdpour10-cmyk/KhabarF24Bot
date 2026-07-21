"""
KhabarF24 Configuration v8.0
تمام تنظیمات پروژه
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# Telegram
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@KhabarF24")

# ==========================
# Scheduler
# ==========================
CHECK_INTERVAL = 300                    # ۵ دقیقه
MAX_NEWS_PER_CYCLE = 3                  # حداکثر خبر در هر چرخه

# ==========================
# Quality & Filters
# ==========================
MIN_QUALITY_SCORE = 55
MIN_IMPORTANCE_SCORE = 5

# ==========================
# Categories
# ==========================
ENABLED_CATEGORIES = {
    "politics": True,
    "iran": True,
    "world": True,
    "sport": True,
    "economy": True,
    "technology": True,
    "gaming": True,
}

# ==========================
# AI & Processing
# ==========================
ENABLE_TRANSLATION = True
ENABLE_REWRITER = True

# ==========================
# Images
# ==========================
ENABLE_NEWS_IMAGE = True
WATERMARK_TEXT = "KhabarF24"

# ==========================
# Debug
# ==========================
DEBUG_MODE = False
LOG_LEVEL = "INFO"
