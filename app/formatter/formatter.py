"""
app/formatter/formatter.py

Single public entry point used by the publishing layer:

    from app.formatter.formatter import format_news
    text = format_news(news)

This file only decides WHICH template renders a given News object. It
never builds post text itself — that responsibility stays inside the
template files so this file can stay small forever.

Routing rule:
  - category == "sports" AND a specific sub-sport was detected
        -> delegate to the matching app/formatter/sports/<sport>/builder.py
           (live match report format: lineups, referee, stadium, etc.)
  - everything else (politics, world, economy, technology, health,
    weather, social, iran, and "sports" with no sub-sport detected yet)
        -> app/formatter/templates/base.py (generic template)
"""

from app.formatter.templates.base import render_general_news

# Sub-sport builders are registered here as they get implemented.
# Each entry: sport key -> callable(news) -> str
# Example once football is built:
#   from app.formatter.sports.football.builder import render_football_match
#   SPORT_BUILDERS = {"football": render_football_match}
SPORT_BUILDERS: dict[str, callable] = {}


def format_news(news) -> str:
    """
    Render a News object into the final Telegram-ready post text.

    Expects `news` to expose `category` (str) and, for sports items,
    `sport` (str | None) identifying the detected sub-sport.
    """
    category = (getattr(news, "category", None) or "").strip().lower()

    if category == "sports":
        sport = (getattr(news, "sport", None) or "").strip().lower()
        builder = SPORT_BUILDERS.get(sport)
        if builder:
            return builder(news)
        # No sub-sport builder registered yet (or sport not detected):
        # fall back to the generic template so publishing never breaks.
        return render_general_news(news)

    return render_general_news(news)
