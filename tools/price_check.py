"""
Price Check

آزمایش دستی (روی GitHub): کدام منبع قیمت از سرور GitHub (IP خارجی) باز می‌شود؟

برای پست روزانه‌ی قیمت (دلار، تتر، بیت‌کوین، طلا، سکه، خودرو). فقط می‌خواند.
هر منبع: کد HTTP، نوع، حجم، و اگر ساختارش را بشناسم عددهای مهم.
خط آخر: RESULT با فهرست منابع قابل‌دسترس.
"""

import json
import re
import sys
import urllib.error
import urllib.request

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def call(url, method="GET", body=None, timeout=25):
    """(status, content_type, text, error)."""

    data = json.dumps(body).encode() if body is not None else None
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/html;q=0.8, */*;q=0.5",
        "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    }

    if data is not None:
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, method=method, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read(2_000_000).decode("utf-8", "ignore")
            return response.status, response.headers.get("Content-Type", ""), text, ""

    except urllib.error.HTTPError as exc:
        try:
            text = exc.read(1500).decode("utf-8", "ignore")
        except Exception:
            text = ""

        ctype = exc.headers.get("Content-Type", "") if exc.headers else ""
        return exc.code, ctype, text, f"HTTP {exc.code}"

    except Exception as exc:
        return 0, "", "", f"{type(exc).__name__}: {exc}"


def find_keys(obj, wanted, found=None, path="", limit=14):
    """کلیدهایی که اسمشان یکی از wanted است (هر عمقی)."""

    found = [] if found is None else found

    if len(found) >= limit:
        return found

    if isinstance(obj, dict):
        for key, value in obj.items():
            name = str(key).lower()

            if any(w in name for w in wanted):
                short = json.dumps(value, ensure_ascii=False)[:110]
                found.append(f"{path}/{key} = {short}")

            if isinstance(value, (dict, list)):
                find_keys(value, wanted, found, f"{path}/{key}", limit)

    elif isinstance(obj, list):
        for index, value in enumerate(obj[:40]):
            if isinstance(value, (dict, list)):
                find_keys(value, wanted, found, f"{path}[{index}]", limit)

    return found


def flat(text, limit=150):
    return re.sub(r"\s+", " ", text or "").strip()[:limit]


def j(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


def x_nobitex(text):
    data = j(text) or {}
    stats = data.get("stats") or {}
    lines = [f"{k}: latest={v.get('latest')} (ریال)" for k, v in stats.items() if k in ("usdt-rls", "btc-rls", "btc-usdt")]
    return lines or [f"keys: {list(data)[:6]} stats: {list(stats)[:6]}"]


def x_wallex(text):
    data = j(text) or {}
    symbols = ((data.get("result") or {}).get("symbols")) or {}
    lines = []

    for name in ("USDTTMN", "BTCTMN", "BTCUSDT"):
        stats = (symbols.get(name) or {}).get("stats") or {}

        if stats:
            lines.append(f"{name}: lastPrice={stats.get('lastPrice')}")

    return lines or [f"keys: {list(data)[:6]} symbols: {len(symbols)}"]


def x_tgju(text):
    data = j(text)

    if data is None:
        return ["not JSON: " + re.sub(r"\s+", " ", text)[:120]]

    hits = find_keys(
        data,
        ("price_dollar", "geram18", "sekee", "sekeb", "bitcoin", "tether", "usdt", "mesghal"),
    )
    return hits or [f"top-level keys: {list(data)[:10]}"]


def x_coingecko(text):
    data = j(text) or {}
    return [f"{k}: {v}" for k, v in data.items()] or [text[:120]]


def x_goldapi(text):
    data = j(text) or {}
    return [f"XAU: {data.get('price')} {data.get('currency', '')}".strip()] if data else [text[:120]]


def x_html(text):
    title = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
    blocked = any(w in text.lower()[:6000] for w in ("captcha", "access denied", "cloudflare", "just a moment"))
    shown = re.sub(r"\s+", " ", title.group(1)).strip()[:70] if title else "-"
    return [f"title: {shown}" + ("  [captcha/blocked page?]" if blocked else "")]


# (شناسه، توضیح، روش، آدرس، بدنه، استخراج‌کننده)
CANDIDATES = [
    ("nobitex", "nobitex-stats (تتر و بیت‌کوین، ریال)", "GET", "https://api.nobitex.ir/market/stats?srcCurrency=btc,usdt&dstCurrency=rls", None, x_nobitex),
    ("wallex", "wallex (تتر و بیت‌کوین، تومان)", "GET", "https://api.wallex.ir/v1/markets", None, x_wallex),
    ("tgju-ajax", "tgju ajax.json (دلار، طلا، سکه...)", "GET", "https://call1.tgju.org/ajax.json", None, x_tgju),
    ("tgju-site", "tgju سایت", "GET", "https://www.tgju.org/", None, x_html),
    ("bonbast", "bonbast", "GET", "https://bonbast.com/", None, x_html),
    ("alanchand", "alanchand", "GET", "https://alanchand.com/", None, x_html),
    ("eghtesadonline", "اقتصادآنلاین", "GET", "https://www.eghtesadonline.com/", None, x_html),
    ("donya-eqtesad", "دنیای اقتصاد", "GET", "https://donya-e-eqtesad.com/", None, x_html),
    ("coingecko", "coingecko (بیت‌کوین و تتر، دلار)", "GET", "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,tether&vs_currencies=usd", None, x_coingecko),
    ("gold-api", "gold-api (انس جهانی طلا)", "GET", "https://api.gold-api.com/price/XAU", None, x_goldapi),
]


def main():
    print("Price check | از سرور GitHub\n")
    reachable, failed = [], []

    for ident, name, method, url, body, extractor in CANDIDATES:
        status, ctype, text, error = call(url, method, body)
        print(f"[{status or 'ERR'}] {name}\n      {url}")
        print(f"      {ctype or '-'} | {len(text)} chars | {error or 'ok'}")

        usable = status == 200

        if status == 200:
            try:
                lines = extractor(text)[:8]
            except Exception as exc:
                lines = [f"(extract failed: {type(exc).__name__}: {exc})"]

            for line in lines:
                print(f"      -> {line}")

            # صفحه‌ی captcha / Cloudflare با کد ۲۰۰ هم «باز نشد» حساب می‌شود
            if any("[captcha/blocked page?]" in line for line in lines):
                usable = False

        elif text:
            print(f"      body: {flat(text)}")

        (reachable if usable else failed).append(ident)
        print()

    print("=" * 60)
    print(
        "RESULT | reachable: " + (", ".join(reachable) or "none")
        + " | failed_or_blocked: " + (", ".join(failed) or "none")
    )


if __name__ == "__main__":
    main()
