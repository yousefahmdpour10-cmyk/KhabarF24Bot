"""
Match Post

قالب پست بازی (نتیجه بعد از بازی، ترکیب قبل از بازی): پرچم تیم‌ها، رقم‌های
ایموجی در نتیجه و ایموجی هر خط ترکیب (دروازه‌بان، دفاع، میانه، حمله).

اسم‌های فارسی (news.fa_names) و کد کشور تیم‌ها (news.fa_countries) را
Gemini در همان یک درخواستی که تیتر را می‌سازد می‌دهد. اگر چیزی نبود، اسم
انگلیسی ESPN چاپ می‌شود و پرچم (در صورت نبودن کشور) حذف می‌شود.
"""

import re
from typing import Dict, List, Optional, Tuple

# فاصله‌ی بین خط‌های پست: "\n\n" = یک خط خالی بین هر دو خط، "\n" = چسبیده
LINE_SEPARATOR = "\n\n"

_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

# حرف‌های عربی/کردی که Gemini گاهی در ترجمه‌ی اسم‌ها می‌گذارد ← فارسی
_FA_LETTERS = str.maketrans({
    "ي": "ی", "ى": "ی", "ې": "ی", "ێ": "ی",
    "ك": "ک", "ڪ": "ک",
    "ۆ": "و", "ۊ": "و",
    "ە": "ه", "ہ": "ه", "ھ": "ه",
    "ڕ": "ر", "ڵ": "ل",
}) 
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

# لیگ‌های داخلی: همه‌ی تیم‌ها از یک کشورند (اگر Gemini کشور نداد)
LEAGUE_DEFAULT_COUNTRY = {
    "Premier League": "GB",
    "La Liga": "ES",
    "Serie A": "IT",
    "Bundesliga": "DE",
    "Ligue 1": "FR",
}

MONTHS_FA = {
    1: "ژانویه", 2: "فوریه", 3: "مارس", 4: "آوریل", 5: "مه", 6: "ژوئن",
    7: "ژوئیه", 8: "اوت", 9: "سپتامبر", 10: "اکتبر", 11: "نوامبر",
    12: "دسامبر",
}

# برچسب کوتاه‌تر برای آمار (برچسب‌های خود fetcher ← نمایش)
STAT_LABELS = {
    "مالکیت توپ": "مالکیت",
    "شوت در چارچوب": "چارچوب",
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
_RESULT_EXTRA_RE = re.compile(r"\((.+)\)\s*$")


# ----------------------------------------------------------------------
# ابزارهای کوچک
# ----------------------------------------------------------------------

def digits(text) -> str:
    return str(text).translate(_PERSIAN_DIGITS)


def keycap(number) -> str:
    """۲ ← 2️⃣ ،  ۱۰ ← 1️⃣0️⃣"""

    try:
        value = str(int(number))
    except (TypeError, ValueError):
        return str(number)

    return "".join(f"{d}\uFE0F\u20E3" for d in value)


def country_flag(code) -> str:
    """کد دو حرفی کشور ← ایموجی پرچم (مثل IT ← 🇮🇹). نامعتبر ← رشته‌ی خالی."""

    code = str(code or "").strip().upper()

    if not re.fullmatch(r"[A-Z]{2}", code):
        return ""

    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code)


def _minute(minute: str) -> str:
    minute = str(minute or "").strip()

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
        "minute": _minute(match.group("minute")),
        "team": (match.group("team") or "").strip(),
        "penalty": tag == "(pen.)",
        "own_goal": tag == "(o.g.)",
    }


def parse_stat(line: str) -> Optional[Tuple[str, str, str]]:
    match = _STAT_RE.match(str(line or "").strip())

    if not match:
        return None

    return (
        match.group("label").strip(),
        match.group("a").strip(),
        match.group("b").strip(),
    )


def _strip_number(player: str) -> str:
    return _NUMBER_PREFIX_RE.sub("", str(player or "").strip())


def _formation_of(team_label: str) -> Tuple[str, Optional[str]]:
    """«Fenerbahce (4-3-3)» ← («Fenerbahce»، «4-3-3»)."""

    match = re.match(r"^(.*?)\s*\(([\d\-]+)\)\s*$", str(team_label or "").strip())

    if match:
        return match.group(1).strip(), match.group(2)

    return str(team_label or "").strip(), None


# ----------------------------------------------------------------------
# اسم‌هایی که باید ترجمه شوند (برای پرامپت Gemini)
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
# نام، پرچم، تاریخ
# ----------------------------------------------------------------------

def _fa(names: Dict[str, str], value) -> str:
    value = str(value or "").strip()
    return ((names or {}).get(value) or value).translate(_FA_LETTERS)


def _flags(news) -> Dict[str, str]:
    """نام انگلیسی تیم ← پرچم (برای دو تیم بازی)."""

    info = getattr(news, "match_info", None) or {}
    codes = getattr(news, "fa_countries", None) or {}
    default = LEAGUE_DEFAULT_COUNTRY.get(str(getattr(news, "league", "") or ""))

    flags = {}

    for team in (info.get("home"), info.get("away")):
        if team:
            flags[team] = country_flag(codes.get(team) or default)

    return flags


def _with_flag(flag: str, text: str) -> str:
    return f"{flag} {text}".strip()


def _date_fa(match_date: Optional[str]) -> str:
    """«2026-11-05» ← «۵ نوامبر ۲۰۲۶»."""

    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(match_date or ""))

    if not match:
        return ""

    year, month, day = (int(g) for g in match.groups())
    name = MONTHS_FA.get(month)

    if not name:
        return ""

    return digits(f"{day} {name} {year}")


def _league_fa(news) -> str:
    league = str(getattr(news, "league", "") or "")
    return LEAGUE_FA.get(league, league)


# ----------------------------------------------------------------------
# رندر
# ----------------------------------------------------------------------

def render(news) -> str:
    """بدنه‌ی پست بازی (بدون سرتیتر، منبع و پاورقی)؛ بدون خط خالی."""

    if getattr(news, "match_phase", None) == "lineup":
        return _render_lineup(news)

    return _render_result(news)


def _stat_value(value: str) -> str:
    value = str(value).strip()

    if value.endswith("%"):
        try:
            return f"{round(float(value[:-1]))}٪"
        except ValueError:
            pass

    return value


def _render_result(news) -> str:
    names = getattr(news, "fa_names", None) or {}
    info = getattr(news, "match_info", None) or {}
    flags = _flags(news)

    home_en, away_en = info.get("home"), info.get("away")
    home, away = _fa(names, home_en), _fa(names, away_en)

    lines: List[str] = [f"🔥 پایان بازی در {_league_fa(news)}"]

    score_parts = [
        flags.get(home_en, ""),
        home,
        keycap(info.get("home_goals", "")),
        "─",
        keycap(info.get("away_goals", "")),
        away,
        flags.get(away_en, ""),
    ]
    lines.append(" ".join(p for p in score_parts if p))

    extra = _RESULT_EXTRA_RE.search(str(getattr(news, "result", "") or ""))

    if extra:
        lines.append(f"🔸 {extra.group(1)}")

    # ---- گل‌ها (پاس‌گل کنار هر گل) ----
    assists = [parse_event(a) for a in getattr(news, "assists", None) or []]
    assists = [a for a in assists if a]

    for raw in getattr(news, "goals", None) or []:
        goal = parse_event(raw)

        if not goal:
            continue

        text = f"⚽ {goal['minute']} {_fa(names, goal['player'])}"

        if goal["team"] and flags.get(goal["team"]):
            text += f" {flags[goal['team']]}"

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

        lines.append(text)

    # ---- خلاصه‌ی یک‌جمله‌ای ----
    summary = str(getattr(news, "match_summary", "") or "").strip()

    if summary:
        lines.append(f"💥 {summary}")

    # ---- آمار ----
    stat_lines = []

    for raw in getattr(news, "stats", None) or []:
        stat = parse_stat(raw)

        if stat:
            label, a, b = stat
            label = STAT_LABELS.get(label, label)
            stat_lines.append(f"{label}: {_stat_value(a)} ─ {_stat_value(b)}")

    if stat_lines:
        lines.append("📊 آمار")
        lines += stat_lines

    # ---- کارت‌ها: به تفکیک تیم ----
    for attr, icon, title in (
        ("yellow_cards", "🟨", "کارت‌ها"),
        ("red_cards", "🟥", "کارت قرمز"),
    ):
        by_team: Dict[str, List[str]] = {}

        for raw in getattr(news, attr, None) or []:
            card = parse_event(raw)

            if card:
                by_team.setdefault(card["team"], []).append(
                    f"{_fa(names, card['player'])} {card['minute']}"
                )

        if by_team:
            groups = []

            for team in [t for t in (home_en, away_en) if t in by_team] + [
                t for t in by_team if t not in (home_en, away_en)
            ]:
                groups.append(
                    _with_flag(flags.get(team, ""), " · ".join(by_team[team]))
                )

            lines.append(f"{icon} {title}")
            lines.append(" | ".join(groups))

    # ---- اطلاعات بازی ----
    lines.append(f"🏆 {_league_fa(news)}")

    if getattr(news, "stadium", None):
        lines.append(f"🏟️ {_fa(names, news.stadium)}")

    date = _date_fa(getattr(news, "match_date", None))

    if date:
        lines.append(f"📅 {date}")

    return LINE_SEPARATOR.join(lines)


def _render_lineup(news) -> str:
    names = getattr(news, "fa_names", None) or {}
    info = getattr(news, "match_info", None) or {}
    flags = _flags(news)

    home_en, away_en = info.get("home"), info.get("away")
    home, away = _fa(names, home_en), _fa(names, away_en)

    lines: List[str] = [
        f"🔥 ترکیب اصلی {home} و {away} اعلام شد",
        f"🏆 {_league_fa(news)} · ترکیب اصلی",
        f"{_with_flag(flags.get(home_en, ''), home)} 🆚 "
        f"{_with_flag(flags.get(away_en, ''), away)}",
    ]

    if getattr(news, "match_time", None):
        lines.append(f"🕒 {digits(news.match_time)} به وقت تهران")

    if getattr(news, "stadium", None):
        lines.append(f"🏟️ {_fa(names, news.stadium)}")

    if getattr(news, "referee", None):
        lines.append(f"👨‍⚖️ داور: {_fa(names, news.referee)}")

    lineup = getattr(news, "lineup", None) or {}

    for side, team_en in (("home", home_en), ("away", away_en)):
        team = lineup.get(side) or {}
        starters = [
            _fa(names, _strip_number(p)) for p in team.get("starting") or []
        ]

        if not starters:
            continue

        label_name, formation = _formation_of(team.get("name"))
        title = _fa(names, label_name or team_en)

        header = f"📋 {_with_flag(flags.get(team_en, ''), title)}"

        if formation:
            header += f" · {digits(formation)}"

        lines.append(header)
        lines += _lineup_rows(starters, formation)

    return LINE_SEPARATOR.join(lines)


def _lineup_rows(players: List[str], formation: Optional[str]) -> List[str]:
    """
    ترکیب را به خط‌های «🧤 دروازه‌بان / 🛡️ دفاع / ⚙️ میانه / 🎯 هافبک‌های
    حمله‌ای / ⚡ مهاجم» بر اساس سیستم (مثل ۴-۲-۳-۱) می‌چیند.

    اگر سیستم با تعداد بازیکن نخواند، همه در یک خط می‌آیند.
    """

    try:
        sizes = [int(x) for x in str(formation or "").split("-") if x]
    except ValueError:
        sizes = []

    if not sizes or 1 + sum(sizes) != len(players):
        return ["⚙️ " + " · ".join(players)]

    rows, index = [], 1

    for size in sizes:
        rows.append(players[index:index + size])
        index += size

    # rows: [دفاع، (میانه‌ها...)، حمله]
    out = [("🧤", players[:1])]

    if len(rows) == 1:
        out.append(("🛡️", rows[0]))
    else:
        defense, attack, middle = rows[0], rows[-1], rows[1:-1]

        out.append(("🛡️", defense))

        if len(middle) == 1:
            middle_icons = ["⚙️"]
        elif len(middle) == 2:
            middle_icons = ["⚙️", "🎯"]
        else:
            middle_icons = ["⚙️"] * (len(middle) - 1) + ["🎯"]

        out += list(zip(middle_icons, middle))

        # سه مهاجم (۴-۳-۳): ESPN ترتیب «مهاجم میانی» را مشخص نمی‌کند،
        # پس هر سه در یک خط می‌آیند، نه این‌که یکی اشتباه «مهاجم» شود.
        out.append(("🎯" if len(attack) >= 3 else "⚡", attack))

    return [f"{icon} " + " · ".join(row) for icon, row in out if row]
