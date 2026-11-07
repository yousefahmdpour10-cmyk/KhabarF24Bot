"""
Match Post

قالب جمع‌وجور پست بازی:
- نتیجه با اعداد استیکری
- پرچم کشور کنار نام تیم
- گل‌ها به‌صورت تیمی
- کارت‌ها به‌صورت تیمی
- آمار فشرده
- ترکیب اصلی قبل از بازی

اسم‌های فارسی از news.fa_names می‌آیند.
"""

import re
from typing import Dict, List, Optional, Tuple


_PERSIAN_DIGITS = str.maketrans(
    "0123456789",
    "۰۱۲۳۴۵۶۷۸۹",
)


LEAGUE_FA = {
    "Premier League": "لیگ برتر انگلیس",
    "La Liga": "لالیگا",
    "Serie A": "سری‌آ",
    "Bundesliga": "بوندس‌لیگا",
    "Ligue 1": "لیگ ۱ فرانسه",
    "Champions League": "لیگ قهرمانان اروپا",
    "Europa League": "لیگ اروپا",
    "Conference League": "لیگ کنفرانس اروپا",
}


# ----------------------------------------------------------------------
# پرچم کشور تیم‌ها
# ----------------------------------------------------------------------

TEAM_COUNTRY_FLAGS = {
    # England
    "Manchester United": "🇬🇧",
    "Man Utd": "🇬🇧",
    "Manchester Utd": "🇬🇧",
    "Liverpool": "🇬🇧",
    "Arsenal": "🇬🇧",
    "Chelsea": "🇬🇧",
    "Manchester City": "🇬🇧",
    "Tottenham Hotspur": "🇬🇧",
    "Tottenham": "🇬🇧",
    "Newcastle United": "🇬🇧",
    "Aston Villa": "🇬🇧",
    "West Ham United": "🇬🇧",
    "Everton": "🇬🇧",

    # Italy
    "Roma": "🇮🇹",
    "AS Roma": "🇮🇹",
    "Juventus": "🇮🇹",
    "Inter Milan": "🇮🇹",
    "Inter": "🇮🇹",
    "AC Milan": "🇮🇹",
    "Napoli": "🇮🇹",
    "Atalanta": "🇮🇹",
    "Lazio": "🇮🇹",
    "Fiorentina": "🇮🇹",

    # Spain
    "Real Madrid": "🇪🇸",
    "Barcelona": "🇪🇸",
    "Atletico Madrid": "🇪🇸",
    "Atlético Madrid": "🇪🇸",
    "Sevilla": "🇪🇸",
    "Villarreal": "🇪🇸",
    "Athletic Club": "🇪🇸",
    "Real Sociedad": "🇪🇸",

    # Germany
    "Bayern Munich": "🇩🇪",
    "Bayern München": "🇩🇪",
    "Borussia Dortmund": "🇩🇪",
    "Bayer Leverkusen": "🇩🇪",
    "RB Leipzig": "🇩🇪",
    "Eintracht Frankfurt": "🇩🇪",

    # France
    "Paris Saint-Germain": "🇫🇷",
    "PSG": "🇫🇷",
    "Marseille": "🇫🇷",
    "Lyon": "🇫🇷",
    "Monaco": "🇫🇷",
    "Lille": "🇫🇷",

    # Netherlands
    "Ajax": "🇳🇱",
    "AZ Alkmaar": "🇳🇱",
    "Feyenoord": "🇳🇱",
    "PSV Eindhoven": "🇳🇱",
    "PSV": "🇳🇱",
    "Twente": "🇳🇱",

    # Portugal
    "Porto": "🇵🇹",
    "FC Porto": "🇵🇹",
    "Benfica": "🇵🇹",
    "Sporting CP": "🇵🇹",
    "Sporting": "🇵🇹",

    # Turkey
    "Galatasaray": "🇹🇷",
    "Fenerbahce": "🇹🇷",
    "Fenerbahçe": "🇹🇷",
    "Besiktas": "🇹🇷",
    "Beşiktaş": "🇹🇷",
    "Trabzonspor": "🇹🇷",

    # Belgium
    "Club Brugge": "🇧🇪",
    "Anderlecht": "🇧🇪",
    "Genk": "🇧🇪",

    # Scotland
    "Celtic": "🏴",
    "Rangers": "🏴",

    # Saudi Arabia
    "Al Hilal": "🇸🇦",
    "Al Nassr": "🇸🇦",
    "Al Ahli": "🇸🇦",
    "Al Ittihad": "🇸🇦",
}


_COUNTRY_FLAGS = {
    "GB": "🇬🇧",
    "UK": "🇬🇧",
    "ENG": "🇬🇧",
    "ENGLAND": "🇬🇧",

    "IT": "🇮🇹",
    "ITA": "🇮🇹",
    "ITALY": "🇮🇹",

    "ES": "🇪🇸",
    "ESP": "🇪🇸",
    "SPAIN": "🇪🇸",

    "DE": "🇩🇪",
    "GER": "🇩🇪",
    "GERMANY": "🇩🇪",

    "FR": "🇫🇷",
    "FRA": "🇫🇷",
    "FRANCE": "🇫🇷",

    "NL": "🇳🇱",
    "NED": "🇳🇱",
    "NETHERLANDS": "🇳🇱",

    "PT": "🇵🇹",
    "POR": "🇵🇹",
    "PORTUGAL": "🇵🇹",

    "TR": "🇹🇷",
    "TUR": "🇹🇷",
    "TURKEY": "🇹🇷",

    "BE": "🇧🇪",
    "BEL": "🇧🇪",
    "BELGIUM": "🇧🇪",

    "SA": "🇸🇦",
    "KSA": "🇸🇦",
    "SAUDI ARABIA": "🇸🇦",
}


# ----------------------------------------------------------------------
# Regex
# ----------------------------------------------------------------------

# «Name (54') (pen.) - Team»
# «Name (45') (o.g.)»
_EVENT_RE = re.compile(
    r"^(?P<player>.+?) \((?P<minute>[^)]*)\)"
    r"(?P<tag> \((?:pen\.|o\.g\.)\))?"
    r"(?: - (?P<team>.+))?$"
)


# «label: a - b»
_STAT_RE = re.compile(
    r"^(?P<label>[^:]+): (?P<a>.+?) - (?P<b>.+)$"
)


_NUMBER_PREFIX_RE = re.compile(
    r"^\d+\s+"
)


_RESULT_EXTRA_RE = re.compile(
    r"(\(.+\))\s*$"
)


# ----------------------------------------------------------------------
# عمومی
# ----------------------------------------------------------------------

def digits(text) -> str:
    return str(text).translate(_PERSIAN_DIGITS)


def score_digit(value) -> str:
    """
    3 -> 3️⃣
    2 -> 2️⃣
    """

    value = str(value or "").strip()

    mapping = {
        "0": "0️⃣",
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "8": "8️⃣",
        "9": "9️⃣",
    }

    return mapping.get(value, digits(value))


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
    return _NUMBER_PREFIX_RE.sub(
        "",
        str(player or "").strip(),
    )


def _formation_of(
    team_label: str,
) -> Tuple[str, Optional[str]]:
    """
    «Fenerbahce (4-3-3)»
    ->
    («Fenerbahce», «4-3-3»)
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


# ----------------------------------------------------------------------
# پرچم
# ----------------------------------------------------------------------

def _team_flag(
    news,
    side: str,
) -> str:
    """
    ابتدا از country ذخیره‌شده روی news استفاده می‌کند.
    اگر موجود نبود، از نام تیم استفاده می‌کند.
    """

    country = getattr(
        news,
        f"{side}_country",
        None,
    )

    if country:
        country = str(country).strip().upper()

        if country in _COUNTRY_FLAGS:
            return _COUNTRY_FLAGS[country]

    info = (
        getattr(news, "match_info", None)
        or {}
    )

    team_name = str(
        info.get(side) or ""
    ).strip()

    return TEAM_COUNTRY_FLAGS.get(
        team_name,
        "🏳️",
    )


def _event_side(
    team: str,
    home: str,
    away: str,
) -> Optional[str]:
    """
    تشخیص می‌دهد رویداد مربوط به تیم میزبان
    است یا تیم مهمان.
    """

    team = str(team or "").strip()
    home = str(home or "").strip()
    away = str(away or "").strip()

    if team == home:
        return "home"

    if team == away:
        return "away"

    return None


# ----------------------------------------------------------------------
# اسم‌هایی که باید ترجمه شوند
# ----------------------------------------------------------------------

def collect_names(news) -> List[str]:
    """
    همه اسم‌های انگلیسی پست
    بدون تکرار و به ترتیب.
    """

    names: List[str] = []

    def add(value):
        value = str(value or "").strip()

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
            lineup.get(side) or {}
        ).get("starting") or []:

            add(
                _strip_number(player)
            )

    return names


# ----------------------------------------------------------------------
# فارسی
# ----------------------------------------------------------------------

def _fa(
    names: Dict[str, str],
    value: str,
) -> str:

    value = str(value or "").strip()

    return (
        (names or {}).get(value)
        or value
    )


def _league_line(
    news,
    label: str,
) -> str:

    league = str(
        getattr(
            news,
            "league",
            "",
        )
        or ""
    )

    return (
        f"🏆 {LEAGUE_FA.get(league, league)}"
        f" · {label}"
    )


def _stat_value(
    value: str,
) -> str:

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


# ----------------------------------------------------------------------
# رندر اصلی
# ----------------------------------------------------------------------

def render(news) -> str:
    """
    متن پست بازی
    بدون سرتیتر و پاورقی.
    """

    phase = getattr(
        news,
        "match_phase",
        None,
    )

    if phase == "lineup":
        return _render_lineup(news)

    return _render_result(news)


# ----------------------------------------------------------------------
# نتیجه بازی
# ----------------------------------------------------------------------

def _render_result(news) -> str:

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

    home_flag = _team_flag(
        news,
        "home",
    )

    away_flag = _team_flag(
        news,
        "away",
    )

    lines: List[str] = []

    # --------------------------------------------------------------
    # تیتر
    # --------------------------------------------------------------

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

    # --------------------------------------------------------------
    # لیگ
    # --------------------------------------------------------------

    lines += [
        _league_line(
            news,
            "پایان بازی",
        ),
        "",
    ]

    # --------------------------------------------------------------
    # نتیجه
    # --------------------------------------------------------------

    score = (
        f"{home_flag} {home} "
        f"{score_digit(info.get('home_goals', ''))} "
        f"─ "
        f"{score_digit(info.get('away_goals', ''))} "
        f"{away} {away_flag}"
    )

    lines.append(score)

    # --------------------------------------------------------------
    # گل‌ها
    # فقط استیکر 🥅
    # --------------------------------------------------------------

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
        a for a in assists
        if a
    ]

    goal_groups = {
        "home": [],
        "away": [],
    }

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
            f"{_fa(names, goal['player'])} "
            f"{digits(goal['minute'])}"
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
                    and
                    a["team"]
                    == goal["team"]
                )
            ),
            None,
        )

        if (
            assist
            and not goal["own_goal"]
        ):
            assists.remove(assist)

            text += (
                f" · پاس: "
                f"{_fa(names, assist['player'])}"
            )

        side = _event_side(
            goal.get("team"),
            info.get("home"),
            info.get("away"),
        )

        if side:
            goal_groups[side].append(
                text
            )

    if (
        goal_groups["home"]
        or goal_groups["away"]
    ):

        lines += [
            "",
            "🥅",
        ]

        if goal_groups["home"]:
            lines.append(
                f"{home_flag} {home}: "
                + " · ".join(
                    goal_groups["home"]
                )
            )

        if goal_groups["away"]:
            lines.append(
                f"{away_flag} {away}: "
                + " · ".join(
                    goal_groups["away"]
                )
            )

    # --------------------------------------------------------------
    # کارت زرد
    # فقط 🟨
    # --------------------------------------------------------------

    yellow_groups = {
        "home": [],
        "away": [],
    }

    for raw in (
        getattr(
            news,
            "yellow_cards",
            None,
        )
        or []
    ):

        card = parse_event(raw)

        if not card:
            continue

        text = (
            f"{_fa(names, card['player'])} "
            f"{digits(card['minute'])}"
        )

        side = _event_side(
            card.get("team"),
            info.get("home"),
            info.get("away"),
        )

        if side:
            yellow_groups[side].append(
                text
            )

    if (
        yellow_groups["home"]
        or yellow_groups["away"]
    ):

        lines += [
            "",
            "🟨",
        ]

        if yellow_groups["home"]:
            lines.append(
                f"{home_flag} {home}: "
                + " · ".join(
                    yellow_groups["home"]
                )
            )

        if yellow_groups["away"]:
            lines.append(
                f"{away_flag} {away}: "
                + " · ".join(
                    yellow_groups["away"]
                )
            )

    # --------------------------------------------------------------
    # کارت قرمز
    # فقط 🟥
    # --------------------------------------------------------------

    red_groups = {
        "home": [],
        "away": [],
    }

    for raw in (
        getattr(
            news,
            "red_cards",
            None,
        )
        or []
    ):

        card = parse_event(raw)

        if not card:
            continue

        text = (
            f"{_fa(names, card['player'])} "
            f"{digits(card['minute'])}"
        )

        side = _event_side(
            card.get("team"),
            info.get("home"),
            info.get("away"),
        )

        if side:
            red_groups[side].append(
                text
            )

    if (
        red_groups["home"]
        or red_groups["away"]
    ):

        lines += [
            "",
            "🟥",
        ]

        if red_groups["home"]:
            lines.append(
                f"{home_flag} {home}: "
                + " · ".join(
                    red_groups["home"]
                )
            )

        if red_groups["away"]:
            lines.append(
                f"{away_flag} {away}: "
                + " · ".join(
                    red_groups["away"]
                )
            )

    # --------------------------------------------------------------
    # آمار
    # --------------------------------------------------------------

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
                f"{_stat_value(a)} ─ "
                f"{_stat_value(b)}"
            )

    if stat_lines:
        lines += [
            "",
            "📊 آمار",
        ]

        lines += stat_lines

    # --------------------------------------------------------------
    # ورزشگاه
    # --------------------------------------------------------------

    stadium = getattr(
        news,
        "stadium",
        None,
    )

    if stadium:
        lines += [
            "",
            f"🏟️ {_fa(names, stadium)}",
        ]

    # --------------------------------------------------------------
    # تاریخ
    # --------------------------------------------------------------

    match_date = getattr(
        news,
        "match_date",
        None,
    )

    if match_date:
        lines.append(
            f"📅 {match_date}"
        )

    return "\n".join(lines)


# ----------------------------------------------------------------------
# ترکیب اصلی
# ----------------------------------------------------------------------

def _render_lineup(news) -> str:

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

    home_flag = _team_flag(
        news,
        "home",
    )

    away_flag = _team_flag(
        news,
        "away",
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
            "ترکیب اصلی",
        ),
        "",
        (
            f"{home_flag} {home} "
            f"─ "
            f"{away} {away_flag}"
        ),
    ]

    when = []

    if getattr(
        news,
        "match_time",
        None,
    ):
        when.append(
            "🕒 ساعت "
            + digits(news.match_time)
            + " به وقت تهران"
        )

    if getattr(
        news,
        "stadium",
        None,
    ):
        when.append(
            "🏟️ "
            + _fa(
                names,
                news.stadium,
            )
        )

    if when:
        lines.append(
            " · ".join(when)
        )

    if getattr(
        news,
        "referee",
        None,
    ):
        lines.append(
            "👨‍⚖️ داور: "
            + _fa(
                names,
                news.referee,
            )
        )

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

        team = lineup.get(side) or {}

        starters = [
            _fa(
                names,
                _strip_number(p),
            )
            for p in (
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

        title = (
            _fa(
                names,
                team_name,
            )
            or (
                home
                if side == "home"
                else away
            )
        )

        flag = (
            home_flag
            if side == "home"
            else away_flag
        )

        header = (
            f"📋 {flag} {title}"
        )

        if formation:
            header += (
                f" ({digits(formation)})"
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
    ترکیب را بر اساس سیستم بازی
    به ردیف‌های دروازه‌بان، دفاع،
    میانه و حمله تقسیم می‌کند.
    """

    try:
        sizes = [
            int(x)
            for x in str(
                formation or ""
            ).split("-")
            if x
        ]

    except ValueError:
        sizes = []

    if (
        sizes
        and 1 + sum(sizes)
        == len(players)
    ):

        rows = [
            players[:1]
        ]

        index = 1

        for size in sizes:
            rows.append(
                players[
                    index:index + size
                ]
            )

            index += size

        return [
            " · ".join(row)
            for row in rows
            if row
        ]

    return [
        " · ".join(players)
    ]
