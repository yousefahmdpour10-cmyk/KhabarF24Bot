import os
from dotenv import load_dotenv

# Load environment variables from .env (for local development)
load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@KhabarF24"

# News Check Interval (seconds)
CHECK_INTERVAL = 300

# Request Timeouts (seconds)
RSS_TIMEOUT = 20
REQUEST_TIMEOUT = 20

# Categories
ENABLE_WORLD = True
ENABLE_IRAN = True
ENABLE_POLITICS = True
ENABLE_SPORT = True
ENABLE_ECONOMY = True
ENABLE_TECH = True

# Limits
MAX_POSTS_PER_HOUR = 30
