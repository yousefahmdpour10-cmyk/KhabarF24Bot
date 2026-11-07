"""
Match Post

قالب پست بازی:
- قبل از بازی: ترکیب اصلی
- بعد از بازی: نتیجه نهایی

اسم‌های فارسی از news.fa_names می‌آیند.
"""

import re
from typing import Dict, List, Optional, Tuple

_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


LEAGUE_FA = {
    "Premier League": "لیگ برتر انگلیس",
    "La Liga": "لالیگا",
    "Serie A": "سری‌آ",
    "Bundesliga": "بوندسلیگا",
    "Ligue 1": "لیگ ۱ فرانسه",
    "Champions League": "لیگ قهرمانان اروپا",
    "Europa League": "لیگ اروپا",
    "Conference League": "لیگ کنفرانس اروپا",
}


_EVENT_RE = re.compile(
    r"^(?P<player>.+?) \((?P<minute>[^)]*)\)"
    r"(?P<tag> \((?:pen\.|o\.g\.)\))?"
    r"(?: - (?P<team>.+))?$"
)

_STAT_RE = re.compile(
    r"^(?P<label>[^:]+): (?P<a>.+?) - (?P<b>.+)$"
)

_NUMBER_PREFIX_RE = re.compile(
    r"^\d+\s+"
)

_RESULT_EXTRA_RE = re.compile(
    r"(\(.+\))\s*$"
)


def digits(text) -> str:
    """تبدیل اعداد انگلیسی به فارسی."""
    return str(text).translate(_PERSIAN_DIGITS)


def clean_minute(minute: str) -> str:
    """
    «90'+4'» ← «90+4'»
    «54» ← «54'»
    """

    minute = str(minute or "").strip()

    minute = re.sub(
        r"'(?=\+)",
        "",
        minute,
    )

    if minute and not minute.endswith("'"):
        minute += "'"

    return minute


def parse_event(line: str) -> Optional[dict]:
    """تجزیه گل، پاس گل و کارت."""

    match = _EVENT_RE.match(
        str(line or "").strip()
    )

    if not match:
        return None

    tag = (
        match.group("tag") or ""
    ).strip()

    return {
        "player": match.group("player").strip(),
        "minute": clean_minute(
            match.group("minute")
        ),
        "team": (
            match.group("team") or ""
        ).strip(),
        "penalty": tag == "(pen.)",
        "own_goal": tag == "(o.g.)",
    }


def parse_stat(
    line: str,
) -> Optional[Tuple[str, str, str]]:
    """تجزیه آمار به شکل Label: A - B."""

    match = _STAT_RE.match(
        str(line or "").strip()
    )

    if not match:
        return None

    return (
        match.group("label").strip(),
        match.group("a").strip(),
        match.group("b").strip(),
    )


def _strip_number(player: str) -> str:
    """حذف شماره پیراهن از ابتدای نام بازیکن."""

    return _NUMBER_PREFIX_RE.sub(
        "",
        str(player or "").strip(),
    )


def _formation_of(
    team_label: str,
) -> Tuple[str, Optional[str]]:
    """
    «Fenerbahce (4-3-3)»
    ← («Fenerbahce»، «4-3-3»)
    """

    match = re.match(
        r"^(.*?)\s*\(([\d\-]+)\)\s*$",
        str(team_label or "").strip(),
    )

    if match:
        return (
            match.group(1).strip(),
            match.group(2),
        )

    return (
        str(team_label or "").strip(),
        None,
    )


def collect_names(news) -> List[str]:
    """
    همه اسم‌های انگلیسی پست را بدون تکرار
    و به ترتیب جمع‌آوری می‌کند.
    """

    names: List[str] = []

    def add(value):
        value = str(
            value or ""
        ).strip()

        if value and value not in names:
            names.append(value)

    info = (
        getattr(news, "match_info", None)
        or {}
    )

    add(info.get("home"))
    add(info.get("away"))

    add(
        getattr(
            news,
            "stadium",
            None,
        )
    )

    add(
        getattr(
            news,
            "referee",
            None,
        )
    )

    for attr in (
        "goals",
        "assists",
        "yellow_cards",
        "red_cards",
    ):
        for line in (
            getattr(news, attr, None)
            or []
        ):
            event = parse_event(line)

            if event:
                add(event["player"])
                add(event["team"])

    lineup = (
        getattr(news, "lineup", None)
        or {}
    )

    for side in (
        "home",
        "away",
    ):
        for player in (
            (lineup.get(side) or {}).get(
                "starting"
            )
            or []
        ):
            add(
                _strip_number(player)
            )

    return names


def _fa(
    names: Dict[str, str],
    value: str,
) -> str:
    """برگرداندن نام فارسی."""

    value = str(
        value or ""
    ).strip()

    return (
        (names or {}).get(value)
        or value
    )


def _league_line(
    news,
    label: str,
) -> str:
    """نمایش لیگ."""

    league = str(
        getattr(
            news,
            "league",
            "",
        )
        or ""
    )

    return (
        f"🏆 "
        f"{LEAGUE_FA.get(league, league)}"
        f" · {label}"
    )


def render(news) -> str:
    """
    متن پست بازی.

    قبل از بازی:
        ترکیب اصلی

    بعد از بازی:
        نتیجه نهایی
    """

    phase = getattr(
        news,
        "match_phase",
        None,
    )

    if phase == "lineup":
        return _render_lineup(news)

    return _render_result(news)


def _stat_value(value: str) -> str:
    """فرمت مقدار آمار."""

    value = str(value).strip()

    if value.endswith("%"):
        try:
            return (
                digits(
                    f"{round(float(value[:-1]))}"
                )
                + "٪"
            )
        except ValueError:
            pass

    return digits(value)


# =========================================================
# RESULT
# =========================================================

def _render_result(news) -> str:
    """متن پست نتیجه نهایی."""

    names = (
        getattr(
            news,
            "fa_names",
            None,
        )
        or {}
    )

    info = (
        getattr(
            news,
            "match_info",
            None,
        )
        or {}
    )

    home = _fa(
        names,
        info.get("home"),
    )

    away = _fa(
        names,
        info.get("away"),
    )

    lines: List[str] = []

    headline = str(
        getattr(
            news,
            "title",
            "",
        )
        or ""
    ).strip()

    if headline:
        lines += [
            f"📰 {headline}",
            "",
        ]

    lines += [
        _league_line(
            news,
            "پایان بازی",
        ),
        "",
    ]

    score = (
        f"⚽ {home} "
        f"{digits(info.get('home_goals', ''))}"
        f" - "
        f"{digits(info.get('away_goals', ''))}"
        f" {away}"
    )

    lines.append(score)

    extra = _RESULT_EXTRA_RE.search(
        str(
            getattr(
                news,
                "result",
                "",
            )
            or ""
        )
    )

    if extra:
        lines.append(
            digits(
                extra.group(1)
            )
        )

    # -------------------------
    # Assists
    # -------------------------

    assists = [
        parse_event(a)
        for a in (
            getattr(
                news,
                "assists",
                None,
            )
            or []
        )
    ]

    assists = [
        a
        for a in assists
        if a
    ]

    # -------------------------
    # Goals
    # -------------------------

    goal_lines = []

    for raw in (
        getattr(
            news,
            "goals",
            None,
        )
        or []
    ):
        goal = parse_event(raw)

        if not goal:
            continue

        text = (
            f"{digits(goal['minute'])} "
            f"{_fa(names, goal['player'])}"
        )

        if goal["team"]:
            text += (
                f" "
                f"({_fa(names, goal['team'])})"
            )

        if goal["penalty"]:
            text += " · پنالتی"

        elif goal["own_goal"]:
            text += " · گل به خودی"

        assist = next(
            (
                a
                for a in assists
                if (
                    a["minute"]
                    == goal["minute"]
                    and a["team"]
                    == goal["team"]
                )
            ),
            None,
        )

        if assist and not goal["own_goal"]:
            assists.remove(assist)

            text += (
                f" · پاس: "
                f"{_fa(names, assist['player'])}"
            )

        goal_lines.append(text)

    if goal_lines:
        lines += [
            "",
            "🥅 گل‌ها",
        ]

        lines += goal_lines

    # -------------------------
    # Cards
    # -------------------------

    for attr, icon, title in (
        (
            "yellow_cards",
            "🟨",
            "کارت زرد",
        ),
        (
            "red_cards",
            "🟥",
            "کارت قرمز",
        ),
    ):
        cards = []

        for raw in (
            getattr(
                news,
                attr,
                None,
            )
            or []
        ):
            card = parse_event(raw)

            if card:
                who = _fa(
                    names,
                    card["player"],
                )

                team = (
                    f" ({_fa(names, card['team'])})"
                    if card["team"]
                    else ""
                )

                cards.append(
                    f"{who} "
                    f"{digits(card['minute'])}"
                    f"{team}"
                )

        if cards:
            lines += [
                "",
                f"{icon} {title}: "
                + " · ".join(cards),
            ]

    # -------------------------
    # Stats
    # -------------------------

    stat_lines = []

    for raw in (
        getattr(
            news,
            "stats",
            None,
        )
        or []
    ):
        stat = parse_stat(raw)

        if stat:
            label, a, b = stat

            stat_lines.append(
                f"{label}: "
                f"{_stat_value(a)} - "
                f"{_stat_value(b)}"
            )

    if stat_lines:
        lines += [
            "",
            "📊 آمار بازی",
        ]

        lines += stat_lines

    # -------------------------
    # Stadium
    # -------------------------

    stadium = getattr(
        news,
        "stadium",
        None,
    )

    if stadium:
        lines += [
            "",
            f"🏟️ "
            f"{_fa(names, stadium)}",
        ]

    return "\n".join(lines)


# =========================================================
# LINEUP
# =========================================================

def _render_lineup(news) -> str:
    """
    پست ترکیب اصلی قبل از بازی.

    این بخش عمداً هیچ نتیجه، گل، کارت،
    پاس گل یا آمار بازی را نمایش نمی‌دهد.
    """

    names = (
        getattr(
            news,
            "fa_names",
            None,
        )
        or {}
    )

    info = (
        getattr(
            news,
            "match_info",
            None,
        )
        or {}
    )

    home = _fa(
        names,
        info.get("home"),
    )

    away = _fa(
        names,
        info.get("away"),
    )

    # -------------------------
    # Flags
    # -------------------------

    home_flag = str(
        info.get("home_flag")
        or info.get("home_country_flag")
        or getattr(
            news,
            "home_flag",
            "",
        )
        or ""
    ).strip()

    away_flag = str(
        info.get("away_flag")
        or info.get("away_country_flag")
        or getattr(
            news,
            "away_flag",
            "",
        )
        or ""
    ).strip()

    home_display = (
        f"{home_flag} {home}".strip()
    )

    away_display = (
        f"{away_flag} {away}".strip()
    )

    lines: List[str] = []

    # -------------------------
    # Headline
    # -------------------------

    headline = str(
        getattr(
            news,
            "title",
            "",
        )
        or ""
    ).strip()

    if headline:
        lines += [
            f"📰 {headline}",
            "",
        ]

    # -------------------------
    # Competition
    # -------------------------

    lines += [
        _league_line(
            news,
            "ترکیب اصلی",
        ),
        "",
        f"⚔️ "
        f"{home_display}"
        f"  🆚  "
        f"{away_display}",
    ]

    # -------------------------
    # Match info
    # -------------------------

    when = []

    if getattr(
        news,
        "match_time",
        None,
    ):
        when.append(
            f"🕒 "
            f"{digits(news.match_time)}"
            f" به وقت تهران"
        )

    if getattr(
        news,
        "stadium",
        None,
    ):
        when.append(
            f"🏟️ "
            f"{_fa(names, news.stadium)}"
        )

    if when:
        lines.append(
            " · ".join(when)
        )

    # -------------------------
    # Referee
    # -------------------------

    if getattr(
        news,
        "referee",
        None,
    ):
        lines.append(
            f"👨‍⚖️ "
            f"{_fa(names, news.referee)}"
        )

    # -------------------------
    # Lineups
    # -------------------------

    lineup = (
        getattr(
            news,
            "lineup",
            None,
        )
        or {}
    )

    for side in (
        "home",
        "away",
    ):
        team = (
            lineup.get(side)
            or {}
        )

        starters = [
            _fa(
                names,
                _strip_number(player),
            )
            for player in (
                team.get("starting")
                or []
            )
        ]

        if not starters:
            continue

        team_name, formation = (
            _formation_of(
                team.get("name")
            )
        )

        # اگر نام تیم از lineup نیامده باشد
        if team_name:
            team_title = _fa(
                names,
                team_name,
            )
        else:
            team_title = (
                home
                if side == "home"
                else away
            )

        # پرچم متناسب با تیم
        flag = (
            home_flag
            if side == "home"
            else away_flag
        )

        if flag:
            team_title = (
                f"{flag} {team_title}"
            )

        header = (
            f"📋 {team_title}"
        )

        if formation:
            header += (
                f" · "
                f"{digits(formation)}"
            )

        lines += [
            "",
            header,
        ]

        lines += _formation_rows(
            starters,
            formation,
        )

    return "\n".join(lines)


def _formation_rows(
    players: List[str],
    formation: Optional[str],
) -> List[str]:
    """
    تقسیم بازیکنان بر اساس سیستم بازی.

    نمونه 4-2-3-1:

    🧤 دروازه‌بان
    🛡️ مدافعان
    ⚙️ هافبک‌ها
    🎯 هافبک‌های هجومی
    ⚡ مهاجم
    """

    try:
        sizes = [
            int(value)
            for value in str(
                formation or ""
            ).split("-")
            if value
        ]

    except ValueError:
        sizes = []

    # اگر سیستم با تعداد بازیکنان جور نبود
    if (
        not sizes
        or 1 + sum(sizes)
        != len(players)
    ):
        return [
            "👤 "
            + " · ".join(players)
        ]

    rows: List[str] = []

    # دروازه‌بان
    rows.append(
        f"🧤 {players[0]}"
    )

    index = 1

    # -------------------------
    # برچسب خطوط
    # -------------------------

    if sizes == [4, 2, 3, 1]:
        labels = [
            "🛡️",
            "⚙️",
            "🎯",
            "⚡",
        ]

    elif sizes == [4, 3, 3]:
        labels = [
            "🛡️",
            "⚙️",
            "⚡",
        ]

    elif sizes == [4, 3, 2, 1]:
        labels = [
            "🛡️",
            "⚙️",
            "🎯",
            "⚡",
        ]

    elif sizes == [3, 4, 2, 1]:
        labels = [
            "🛡️",
            "⚙️",
            "🎯",
            "⚡",
        ]

    elif sizes == [3, 5, 2]:
        labels = [
            "🛡️",
            "⚙️",
            "⚡",
        ]

    elif sizes == [4, 4, 2]:
        labels = [
            "🛡️",
            "⚙️",
            "⚡",
        ]

    else:
        # سیستم‌های کمتر رایج
        # خط اول دفاع، خطوط میانی هافبک،
        # و خط آخر مهاجم
        if len(sizes) == 1:
            labels = ["⚡"]

        elif len(sizes) == 2:
            labels = [
                "🛡️",
                "⚡",
            ]

        else:
            labels = (
                ["🛡️"]
                + ["⚙️"]
                * (len(sizes) - 2)
                + ["⚡"]
            )

    # -------------------------
    # ساخت خطوط
    # -------------------------

    for size, emoji in zip(
        sizes,
        labels,
    ):
        row = players[
            index:index + size
        ]

        if row:
            rows.append(
                f"{emoji} "
                + " · ".join(row)
            )

        index += size

    return rows
