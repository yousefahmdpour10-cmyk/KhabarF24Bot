"""
Match Prompt

پرامپت Gemini برای پست‌های بازی (نتیجه و ترکیب). یک درخواست، چند خروجی:
تیتر، ترجمه‌ی همه‌ی اسم‌ها، کشور هر تیم (برای پرچم) و، برای نتیجه، یک
جمله‌ی خلاصه.
"""

import json

from app.formatter.sports.football.match_post import LEAGUE_FA, collect_names


def build_match_prompt(news) -> str:
    info = getattr(news, "match_info", None) or {}
    phase = getattr(news, "match_phase", None)
    league = str(getattr(news, "league", "") or "")
    is_lineup = phase == "lineup"

    teams = [t for t in (info.get("home"), info.get("away")) if t]

    if is_lineup:
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

        cards = list(getattr(news, "yellow_cards", None) or []) + list(
            getattr(news, "red_cards", None) or []
        )

        if cards:
            facts += ". Cards: " + "; ".join(cards)

        stats = list(getattr(news, "stats", None) or [])

        if stats:
            facts += ". Stats: " + "; ".join(stats)

    names = collect_names(news)

    lines = [
        "You are a Persian football news editor writing for a Persian "
        "Telegram channel.",
        f"Topic: {kind}.",
        f"Competition: {league} ({LEAGUE_FA.get(league, league)}).",
        f"Match: {facts}",
        "",
        "Return ONLY a JSON object with these keys:",
        '1. "headline": one short, natural Persian headline '
        "(at most 12 words, no emoji, no quotation marks). For a result, "
        "state who won and the score; for lineups, say the lineups are "
        "announced.",
        '2. "names": an object that maps EVERY string in NAMES below, '
        "using the exact English string as the key, to its Persian form as "
        "used in Persian sports media (team names, player names, stadium, "
        "referee). Transliterate if there is no common Persian form.",
        '3. "countries": an object that maps each TEAM in TEAMS below, '
        "using the exact English string as the key, to the ISO 3166-1 "
        'alpha-2 code of the team\'s country (for example "IT", "NL", "DE"). '
        'Use "GB" for England, Scotland, Wales and Northern Ireland.',
    ]

    if not is_lineup:
        lines.append(
            '4. "summary": ONE Persian sentence (at most 30 words) saying '
            "how the match went, using ONLY the facts given above (score, "
            "goals, minutes, cards, stats). Do not invent anything that is "
            "not in the facts."
        )

    lines += [
        "",
        "TEAMS = " + json.dumps(teams, ensure_ascii=False),
        "NAMES = " + json.dumps(names, ensure_ascii=False),
    ]

    return "\n".join(lines)
