"""
Match Prompt

پرامپت Gemini برای پست‌های بازی.

یک درخواست، دو خروجی:
1. تیتر فارسی
2. ترجمه همه اسم‌ها
"""

import json

from app.formatter.sports.football.match_post import (
    LEAGUE_FA,
    collect_names,
)


def build_match_prompt(news) -> str:

    info = (
        getattr(
            news,
            "match_info",
            None,
        )
        or {}
    )

    phase = getattr(
        news,
        "match_phase",
        None,
    )

    league = str(
        getattr(
            news,
            "league",
            "",
        )
        or ""
    )

    # --------------------------------------------------------------
    # اطلاعات مسابقه
    # --------------------------------------------------------------

    if phase == "lineup":

        kind = (
            "confirmed starting lineups "
            "announced before the match"
        )

        facts = (
            f"{info.get('home')} "
            f"vs "
            f"{info.get('away')}"
        )

    else:

        kind = (
            "final result of the match"
        )

        facts = (
            f"{info.get('home')} "
            f"{info.get('home_goals')} - "
            f"{info.get('away_goals')} "
            f"{info.get('away')}"
        )

        goals = list(
            getattr(
                news,
                "goals",
                None,
            )
            or []
        )

        if goals:
            facts += (
                ". Goals: "
                + "; ".join(goals)
            )

    names = collect_names(news)

    # --------------------------------------------------------------
    # Prompt
    # --------------------------------------------------------------

    return (
        "You are a Persian football news editor "
        "writing for a Persian Telegram channel.\n"

        f"Topic: {kind}.\n"

        f"Competition: "
        f"{league} "
        f"({LEAGUE_FA.get(league, league)}).\n"

        f"Match: {facts}\n\n"

        "HEADLINE RULES:\n"

        "- Return ONE short, exciting and natural "
        "Persian football headline.\n"

        "- Maximum 12 Persian words.\n"

        "- Do NOT use emoji in the headline.\n"

        "- Do NOT use quotation marks.\n"

        "- Do NOT write a dry headline such as "
        "'X defeated Y' or 'X beat Y'.\n"

        "- Make the headline feel like a real "
        "Persian sports news headline.\n"

        "- Highlight drama, comeback, late winner, "
        "dominance or surprise when appropriate.\n"

        "- If the match was a comeback, use words "
        "such as 'کامبک', 'بازگشت', "
        "'بازگشت تماشایی' or similar natural wording.\n"

        "- If a famous club has a well-known Persian "
        "football nickname, you may naturally use it.\n"

        "- For Manchester United, the natural Persian "
        "nickname is 'شیاطین سرخ'.\n"

        "- Do not force a nickname when it makes "
        "the headline unnatural.\n"

        "- The headline must match the actual result "
        "and events of the match.\n\n"

        "Return ONLY a JSON object with exactly "
        "two keys:\n"

        '1. "headline": one short, natural and '
        "exciting Persian football headline.\n"

        '2. "names": an object that maps EVERY '
        "string in NAMES below, using the exact "
        "English string as the key, to its Persian "
        "form as used in Persian sports media "
        "(team names, player names, stadium, referee). "
        "Transliterate if there is no common Persian form.\n\n"

        "NAMES = "
        + json.dumps(
            names,
            ensure_ascii=False,
        )
    ).replace(
        "\\n",
        "\n",
    )
