"""
app/formatter/formatter.py

Entry point used by the publishing layer for GENERAL (non-football)
news items:

    from app.formatter.formatter import format_news
    text = format_news(news)   # news is a processed News object

Routing note (per project decision):
  Football/sports live-match posts do NOT go through this file. The
  publisher itself checks `category == "sports"` BEFORE the item ever
  reaches here, and calls FootballBuilder directly on the RawNews object:

      # inside the publisher, e.g. app/publishers/telegram_publisher.py
      if raw_news.category == "sports":
          text = FootballBuilder().build(raw_news)
      else:
          news = <processed News from the pipeline>
          text = format_news(news)

  This file therefore only ever receives a processed `News` object for
  politics/world/economy/technology/health/weather/social/iran, and just
  delegates to the generic template.
"""

from app.formatter.templates.base import render_general_news


def format_news(news) -> str:
    """Render a processed (non-sports) News object into post text."""
    return render_general_news(news)
