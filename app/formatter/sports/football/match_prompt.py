"""
Match Prompt

پرامپت Gemini برای پست‌های بازی (نتیجه و ترکیب). یک درخواست، دو خروجی:
تیتر فارسی و ترجمه‌ی همه‌ی اسم‌ها (تیم، بازیکن، ورزشگاه، داور).
"""

import json

from app.formatter.sports.football.match_post import LEAGUE_FA, collect_names


def build_match_prompt(news) -> str:
    info = getattr(news, "match_info", None) or {}
    phase = getattr(news, "match_phase", None)
    league = str(getattr(news, "league", "") or "")

    if phase == "lineup":
        kind = "confirmed starting lineups announced before the match"
        facts = f"{info.get('home')} vs {info.get('away')}"
    else:
        kind = "final result of the match"
        facts = (
            f"{info.get('home')} {info.get('home_goals')} - "
            f"{info.get('away_goals')} {info.get('away')}"
        )
        goals = list(getattr(news, "goals", None) or [])

        if goals:
            facts += ". Goals: " + "; ".join(goals)

    names = collect_names(news)

    return (
        "You are a Persian football news editor writing for a Persian "
        "Telegram channel.\\n"
        f"Topic: {kind}.\\n"
        f"Competition: {league} ({LEAGUE_FA.get(league, league)}).\\n"
        f"Match: {facts}\\n\\n"
        "Return ONLY a JSON object with exactly two keys:\\n"
        '1. "headline": one short, natural Persian headline '
        "(at most 12 words, no emoji, no quotation marks). For a result, "
        "state who won and the score in words or digits; for lineups, say "
        "the lineups are announced.\\n"
        '2. "names": an object that maps EVERY string in NAMES below, '
        "using the exact English string as the key, to its Persian form as "
        "used in Persian sports media (team names, player names, stadium, "
        "referee). Transliterate if there is no common Persian form.\\n\\n"
        "NAMES = " + json.dumps(names, ensure_ascii=False)
    ).replace("\\n", "\n")
