"""
Match Post

قالب «جمع‌وجور» پست بازی: نتیجه (بعد از بازی) و ترکیب اصلی (قبل از بازی).

اسم‌های فارسی از news.fa_names می‌آیند (Gemini همان یک درخواستی که تیتر
را می‌سازد، اسم‌ها را هم ترجمه می‌کند). اگر اسمی در آن نبود، همان اسم
انگلیسی ESPN چاپ می‌شود.
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

# «Name (54') (pen.) - Team»  /  «Name (45') (o.g.)»
_EVENT_RE = re.compile(
    r"^(?P<player>.+?) \((?P<minute>[^)]*)\)"
    r"(?P<tag> \((?:pen\.|o\.g\.)\))?"
    r"(?: - (?P<team>.+))?$"
)

# «label: a - b»
_STAT_RE = re.compile(r"^(?P<label>[^:]+): (?P<a>.+?) - (?P<b>.+)$")

_NUMBER_PREFIX_RE = re.compile(r"^\d+\s+")
_RESULT_EXTRA_RE = re.compile(r"(\(.+\))\s*$")


def digits(text) -> str:
    return str(text).translate(_PERSIAN_DIGITS)


def clean_minute(minute: str) -> str:
    """«90'+4'» ← «90+4'»، «54» ← «54'»."""

    minute = str(minute or "").strip()
    minute = re.sub(r"'(?=\+)", "", minute)

    if minute and not minute.endswith("'"):
        minute += "'"

    return minute


def parse_event(line: str) -> Optional[dict]:
    match = _EVENT_RE.match(str(line or "").strip())

    if not match:
        return None

    tag = (match.group("tag") or "").strip()

    return {
        "player": match.group("player").strip(),
        "minute": clean_minute(match.group("minute")),
        "team": (match.group("team") or "").strip(),
        "penalty": tag == "(pen.)",
        "own_goal": tag == "(o.g.)",
    }


def parse_stat(line: str) -> Optional[Tuple[str, str, str]]:
    match = _STAT_RE.match(str(line or "").strip())

    if not match:
        return None

    return match.group("label").strip(), match.group("a").strip(), match.group("b").strip()


def _strip_number(player: str) -> str:
    return _NUMBER_PREFIX_RE.sub("", str(player or "").strip())


def _formation_of(team_label: str) -> Tuple[str, Optional[str]]:
    """«Fenerbahce (4-3-3)» ← («Fenerbahce»، «4-3-3»)."""

    match = re.match(r"^(.*?)\s*\(([\d\-]+)\)\s*$", str(team_label or "").strip())

    if match:
        return match.group(1).strip(), match.group(2)

    return str(team_label or "").strip(), None


# ----------------------------------------------------------------------
# اسم‌هایی که باید ترجمه شوند
# ----------------------------------------------------------------------

def collect_names(news) -> List[str]:
    """همه‌ی اسم‌های انگلیسی پست (بدون تکرار، به ترتیب)."""

    names: List[str] = []

    def add(value):
        value = str(value or "").strip()

        if value and value not in names:
            names.append(value)

    info = getattr(news, "match_info", None) or {}
    add(info.get("home"))
    add(info.get("away"))
    add(getattr(news, "stadium", None))
    add(getattr(news, "referee", None))

    for attr in ("goals", "assists", "yellow_cards", "red_cards"):
        for line in getattr(news, attr, None) or []:
            event = parse_event(line)

            if event:
                add(event["player"])
                add(event["team"])

    lineup = getattr(news, "lineup", None) or {}

    for side in ("home", "away"):
        for player in (lineup.get(side) or {}).get("starting") or []:
            add(_strip_number(player))

    return names


# ----------------------------------------------------------------------
# رندر
# ----------------------------------------------------------------------

def _fa(names: Dict[str, str], value: str) -> str:
    value = str(value or "").strip()
    return (names or {}).get(value) or value


def _league_line(news, label: str) -> str:
    league = str(getattr(news, "league", "") or "")
    return f"🏆 {LEAGUE_FA.get(league, league)} · {label}"


def render(news) -> str:
    """متن پست بازی (بدون سرتیتر و پاورقی)."""

    phase = getattr(news, "match_phase", None)

    if phase == "lineup":
        return _render_lineup(news)

    return _render_result(news)


def _stat_value(value: str) -> str:
    value = str(value).strip()

    if value.endswith("%"):
        try:
            return digits(f"{round(float(value[:-1]))}") + "٪"
        except ValueError:
            pass

    return digits(value)


def _render_result(news) -> str:
    names = getattr(news, "fa_names", None) or {}
    info = getattr(news, "match_info", None) or {}

    home = _fa(names, info.get("home"))
    away = _fa(names, info.get("away"))

    lines: List[str] = []

    headline = str(getattr(news, "title", "") or "").strip()

    if headline:
        lines += [f"📰 {headline}", ""]

    lines += [_league_line(news, "پایان بازی"), ""]

    score = f"⚽ {home} {digits(info.get('home_goals', ''))} - {digits(info.get('away_goals', ''))} {away}"
    lines.append(score)

    extra = _RESULT_EXTRA_RE.search(str(getattr(news, "result", "") or ""))
    if extra:
        lines.append(digits(extra.group(1)))

    # ---- گل‌ها (هر گل با پاس‌گلش در یک خط) ----
    assists = [parse_event(a) for a in getattr(news, "assists", None) or []]
    assists = [a for a in assists if a]
    goal_lines = []

    for raw in getattr(news, "goals", None) or []:
        goal = parse_event(raw)

        if not goal:
            continue

        text = f"{digits(goal['minute'])} {_fa(names, goal['player'])}"

        if goal["team"]:
            text += f" ({_fa(names, goal['team'])})"

        if goal["penalty"]:
            text += " · پنالتی"
        elif goal["own_goal"]:
            text += " · گل به خودی"

        assist = next(
            (
                a for a in assists
                if a["minute"] == goal["minute"] and a["team"] == goal["team"]
            ),
            None,
        )

        if assist and not goal["own_goal"]:
            assists.remove(assist)
            text += f" · پاس: {_fa(names, assist['player'])}"

        goal_lines.append(text)

    if goal_lines:
        lines += ["", "🥅 گل‌ها"] + goal_lines

    # ---- کارت‌ها ----
    for attr, icon, title in (
        ("yellow_cards", "🟨", "کارت زرد"),
        ("red_cards", "🟥", "کارت قرمز"),
    ):
        cards = []

        for raw in getattr(news, attr, None) or []:
            card = parse_event(raw)

            if card:
                who = _fa(names, card["player"])
                team = f" ({_fa(names, card['team'])})" if card["team"] else ""
                cards.append(f"{who} {digits(card['minute'])}{team}")

        if cards:
            lines += ["", f"{icon} {title}: " + " · ".join(cards)]

    # ---- آمار ----
    stat_lines = []

    for raw in getattr(news, "stats", None) or []:
        stat = parse_stat(raw)

        if stat:
            label, a, b = stat
            stat_lines.append(f"{label}: {_stat_value(a)} - {_stat_value(b)}")

    if stat_lines:
        lines += ["", "📊 آمار بازی"] + stat_lines

    # ---- ورزشگاه ----
    stadium = getattr(news, "stadium", None)

    if stadium:
        lines += ["", f"🏟 {_fa(names, stadium)}"]

    return "\n".join(lines)


def _render_lineup(news) -> str:
    names = getattr(news, "fa_names", None) or {}
    info = getattr(news, "match_info", None) or {}

    home = _fa(names, info.get("home"))
    away = _fa(names, info.get("away"))

    lines: List[str] = []

    headline = str(getattr(news, "title", "") or "").strip()

    if headline:
        lines += [f"📰 {headline}", ""]

    lines += [_league_line(news, "ترکیب اصلی"), "", f"⚽ {home} - {away}"]

    when = []

    if getattr(news, "match_time", None):
        when.append(f"🕒 ساعت {digits(news.match_time)} به وقت تهران")

    if getattr(news, "stadium", None):
        when.append(f"🏟 {_fa(names, news.stadium)}")

    if when:
        lines.append(" · ".join(when))

    if getattr(news, "referee", None):
        lines.append(f"👨‍⚖️ داور: {_fa(names, news.referee)}")

    lineup = getattr(news, "lineup", None) or {}

    for side in ("home", "away"):
        team = lineup.get(side) or {}
        starters = [
            _fa(names, _strip_number(p)) for p in team.get("starting") or []
        ]

        if not starters:
            continue

        team_name, formation = _formation_of(team.get("name"))
        title = _fa(names, team_name) or (home if side == "home" else away)

        header = f"📋 {title}"
        if formation:
            header += f" ({digits(formation)})"

        lines += ["", header]
        lines += _formation_rows(starters, formation)

    return "\n".join(lines)


def _formation_rows(players: List[str], formation: Optional[str]) -> List[str]:
    """
    ترکیب را به ردیف‌های «دروازه‌بان / دفاع / میانه / حمله» بر اساس سیستم
    (مثل ۴-۳-۳) می‌چیند. اگر سیستم با تعداد بازیکن نمی‌خواند، یک ردیف.
    """

    try:
        sizes = [int(x) for x in str(formation or "").split("-") if x]
    except ValueError:
        sizes = []

    if sizes and 1 + sum(sizes) == len(players):
        rows = [players[:1]]
        index = 1

        for size in sizes:
            rows.append(players[index:index + size])
            index += size

        return [" · ".join(row) for row in rows if row]

    return [" · ".join(players)]
