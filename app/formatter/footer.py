"""
app/formatter/footer.py

Builds the fixed closing block that appears at the bottom of every post,
right before the hashtag line:

    ━━━━━━━━━━━━━━━━
    📢 @KhabarF24

The channel username is NEVER hardcoded here — per project rules,
nothing platform-specific is hardcoded in code. It's read from config
(config/settings.py -> settings.CHANNEL_USERNAME), which itself reads
from .env.
"""

from app.config.settings import settings

DIVIDER = "━" * 16


def build_footer() -> str:
    """Return the '━━━... / 📢 @channel' block."""
    username = settings.CHANNEL_USERNAME.lstrip("@")
    return f"{DIVIDER}\n📢 @{username}"
