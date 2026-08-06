"""
app/formatter/templates/base.py

The single generic template shared by every "regular" news category
(politics, world/international, economy, technology, health, weather,
social, iran). Live football/basketball/etc. match reports do NOT use
this — they have their own builder under app/formatter/sports/.

Output shape (matches the approved KhabarF24 sample):

    ━━━━━━━━━━━━━━━━
    🔴 KhabarF24 | {category_emoji} {category_label}
    ━━━━━━━━━━━━━━━━

    📰 {title}

    ✍️ {summary}

    🗞️ {flag} {source_name}

    ━━━━━━━━━━━━━━━━
    📢 @KhabarF24

    #hashtag1 #hashtag2 ...

Nothing platform- or brand-specific is hardcoded beyond the emoji rules
themselves — channel name comes from footer.py -> config.
"""

from app.formatter.footer import DIVIDER, build_footer
from app.formatter.hashtags import format_hashtag_line
from app.formatter.icons import get_category_icon
from app.formatter.source_flags import format_source_line


def render_general_news(news) -> str:
    """
    Render a News object using the generic template.

    Expects `news` to expose (attribute access, duck-typed on purpose so
    this file doesn't depend on the exact News dataclass shape):
        news.title        -> str
        news.summary       -> str
        news.category       -> str
        news.source         -> str (parser key, e.g. "irna", "bbc")
        news.hashtags       -> list[str] | None
    """
    icon = get_category_icon(getattr(news, "category", None))
    # News.emoji is set by the upstream AI/processing stage when it has
    # picked a more specific emoji than the category default (e.g. a
    # subcategory- or keyword-level choice). It always wins when present.
    emoji = (getattr(news, "emoji", None) or "").strip() or icon.emoji

    header = (
        f"{DIVIDER}\n"
        f"🔴 KhabarF24 | {emoji} {icon.label_fa}\n"
        f"{DIVIDER}"
    )

    title = getattr(news, "title", "").strip()
    summary = getattr(news, "summary", "").strip()
    source_line = format_source_line(getattr(news, "source", None))

    body_parts = [f"📰 {title}"]
    if summary:
        body_parts.append(f"✍️ {summary}")
    body_parts.append(source_line)
    body = "\n\n".join(body_parts)

    footer = build_footer()

    hashtag_line = format_hashtag_line(
        getattr(news, "category", None),
        getattr(news, "hashtags", None),
    )

    sections = [header, body, footer]
    if hashtag_line:
        sections.append(hashtag_line)

    return "\n\n".join(sections)
