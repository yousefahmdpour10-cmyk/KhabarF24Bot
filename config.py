import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# Telegram
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@KhabarF24"

# ==========================
# Scheduler
# ==========================
CHECK_INTERVAL = 300

# ==========================
# Network
# ==========================
RSS_TIMEOUT = 20
REQUEST_TIMEOUT = 20

# ==========================
# Categories
# ==========================
ENABLE_WORLD = True
ENABLE_IRAN = True
ENABLE_POLITICS = True
ENABLE_SPORT = True
ENABLE_ECONOMY = True
ENABLE_TECH = True

# ==========================
# Limits
# ==========================
MAX_POSTS_PER_HOUR = 30

# ==========================
# Translation
# ==========================
ENABLE_TRANSLATION = True
TRANSLATION_TARGET = "fa"

# ==========================
# AI Summary
# ==========================
ENABLE_SUMMARY = False

# ==========================
# Images
# ==========================
ENABLE_NEWS_IMAGE = True

# ==========================
# Urgent News
# ==========================
ENABLE_BREAKING_NEWS = True
