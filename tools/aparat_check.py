"""
Aparat Check

آزمایش دستی (روی GitHub): آپارات از سرور GitHub چه چیزی می‌دهد؟

- صفحه‌ی کانال و لینک ویدئوها
- صفحه‌ی هر ویدئو: og:video / JSON-LD / <video> (با همان media_extractor ربات)
- API قدیمی آپارات و صفحه‌ی embed
- آیا ffprobe آدرس پیداشده (mp4 یا m3u8) را می‌خواند و مدتش چقدر است

فقط می‌خواند و چیزی منتشر نمی‌کند. متغیرهای محیطی:
    APARAT_CHANNEL   (پیش‌فرض ft360_ir)
    APARAT_VIDEO_URL (اختیاری: آدرس یک صفحه‌ی ویدئو برای بررسی مستقیم)
    APARAT_BASE      (فقط برای آزمون محلی)
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.fetchers.media_extractor import extract_page_media  # noqa: E402

CHANNEL = os.getenv("APARAT_CHANNEL", "ft360_ir").strip() or "ft360_ir"
VIDEO_URL = os.getenv("APARAT_VIDEO_URL", "").strip()
BASE = os.getenv("APARAT_BASE", "https://www.aparat.com").rstrip("/")
MAX_VIDEOS = 3

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    "Referer": BASE + "/",
}

# آدرس mp4/m3u8، چه ساده و چه escape‌شده (http:\/\/cdn\/a.m3u8)
_URL_CHARS = r"""(?:[^\s"'<>\\]|\\/|\\u002[Ff]|\\u0026)"""
MEDIA_URL_RE = re.compile(
    r"https?:(?:\\?/|\\u002[Ff]){2}" + _URL_CHARS + r"+?\.(?:m3u8|mp4)(?:\?" + _URL_CHARS + r"*)?",
    re.IGNORECASE,
)
UID_RES = (
    re.compile(r"/v/([A-Za-z0-9]{3,14})"),
    re.compile(r'"uid"\s*:\s*"([A-Za-z0-9]{3,14})"'),
)

summary = {
    "channel_ok": False,
    "uids": 0,
    "videos_checked": 0,
    "videos_with_media": 0,
    "ffprobe_ok": 0,
    "blocked": False,
}


def fetch(url, accept="*/*", timeout=25):
    """(status, content_type, text, error)."""

    request = urllib.request.Request(url, headers={**HEADERS, "Accept": accept})

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(3_000_000)
            return (
                response.status,
                response.headers.get("Content-Type", ""),
                body.decode("utf-8", "ignore"),
                "",
            )

    except urllib.error.HTTPError as exc:
        try:
            body = exc.read(1500).decode("utf-8", "ignore")
        except Exception:
            body = ""

        return exc.code, (exc.headers.get("Content-Type", "") if exc.headers else ""), body, f"HTTP {exc.code}"

    except Exception as exc:
        return 0, "", "", f"{type(exc).__name__}: {exc}"


def show(label, url, result):
    status, ctype, text, error = result
    flat = re.sub(r"\s+", " ", text or "")[:170]
    print(f"[{status or 'ERR'}] {label}: {url}")
    print(f"      content-type={ctype or '-'} | {len(text or '')} chars | {error or 'ok'}")

    if status != 200 and flat:
        print(f"      body: {flat}")

    if status in (401, 403, 429) or (status == 200 and "captcha" in (text or "").lower()[:5000]):
        summary["blocked"] = True


def clean(url):
    return (
        url.replace("\\/", "/")
        .replace("\\u002F", "/")
        .replace("\\u002f", "/")
        .replace("\\u0026", "&")
        .rstrip("\\),;]}")
    )


def media_urls(text):
    found = []

    for match in MEDIA_URL_RE.findall(text or ""):
        url = clean(match)

        if url not in found:
            found.append(url)

    return found


def find_uids(text):
    uids = []

    for pattern in UID_RES:
        for uid in pattern.findall(text or ""):
            if uid not in uids and uid.lower() not in ("video", "embed", "list"):
                uids.append(uid)

    return uids


def ffprobe(url):
    """(مدت به ثانیه یا None، توضیح)."""

    command = [
        "ffprobe", "-v", "error",
        "-user_agent", USER_AGENT,
        "-headers", f"Referer: {BASE}/\r\n",
        "-show_entries", "format=duration:stream=width,height",
        "-of", "default=nw=1", url,
    ]

    try:
        out = subprocess.run(command, capture_output=True, text=True, timeout=45)

    except FileNotFoundError:
        return None, "ffprobe is not installed"

    except subprocess.TimeoutExpired:
        return None, "ffprobe timed out (45s)"

    info = dict(
        line.split("=", 1) for line in out.stdout.splitlines() if "=" in line
    )

    if out.returncode != 0 or "width" not in info:
        return None, (out.stderr.strip().splitlines() or ["no output"])[-1][:160]

    try:
        return float(info.get("duration", "")), f"{info.get('width')}x{info.get('height')}"
    except ValueError:
        return None, f"no duration (live stream?) {info.get('width')}x{info.get('height')}"


def check_video(page_url, uid=None):
    summary["videos_checked"] += 1
    print("\n" + "-" * 60)
    print(f"VIDEO {uid or ''} {page_url}")

    candidates = []

    # ---- ۱) صفحه‌ی ویدئو با همان استخراج‌کننده‌ی ربات ----
    result = fetch(page_url, "text/html")
    show("video page", page_url, result)

    if result[0] == 200:
        video, vtype, image, embed = extract_page_media(result[2], page_url)
        title = re.search(r"<title>(.*?)</title>", result[2], re.S)
        title_text = re.sub(r"\s+", " ", title.group(1)).strip()[:90] if title else "-"
        print(f"      title: {title_text}")
        print(f"      media_extractor -> video={video or '-'}")
        print(f"                         type={vtype or '-'} | embed={embed or '-'} | image={'yes' if image else 'no'}")
        print(f"      og:video present: {'og:video' in result[2]} | VideoObject: {'VideoObject' in result[2]}")

        if video:
            candidates.append(video)

        candidates += [u for u in media_urls(result[2]) if u not in candidates]

    # ---- ۲) API قدیمی آپارات ----
    if uid:
        api_url = f"{BASE}/etc/api/video/videohash/{uid}"
        result = fetch(api_url, "application/json")
        show("legacy API", api_url, result)

        if result[0] == 200:
            try:
                data = json.loads(result[2])
                print(f"      json keys: {list(data)[:8]}")
            except ValueError:
                pass

            candidates += [u for u in media_urls(result[2]) if u not in candidates]

        # ---- ۳) صفحه‌ی embed ----
        embed_url = f"{BASE}/video/video/embed/videohash/{uid}/vt/frame"
        result = fetch(embed_url, "text/html")
        show("embed page", embed_url, result)

        if result[0] == 200:
            candidates += [u for u in media_urls(result[2]) if u not in candidates]

    # ---- ۴) ffprobe روی آدرس‌های پیداشده ----
    if not candidates:
        print("      NO media URL found for this video")
        return

    summary["videos_with_media"] += 1
    print(f"      media URLs found: {len(candidates)}")

    for url in candidates[:4]:
        duration, note = ffprobe(url)
        kind = "m3u8" if ".m3u8" in url.lower() else "mp4"

        if duration:
            summary["ffprobe_ok"] += 1

        print(f"      [{kind}] {url[:150]}")
        print(f"            ffprobe: {'OK duration=%.0fs %s' % (duration, note) if duration else 'FAILED - ' + note}")


def main():
    print(f"Aparat check | channel={CHANNEL} | base={BASE}\n")

    uids = []

    if VIDEO_URL:
        match = re.search(r"/v/([A-Za-z0-9]{3,14})", VIDEO_URL)
        check_video(VIDEO_URL, match.group(1) if match else None)

    else:
        for label, url, accept in (
            ("channel page", f"{BASE}/{CHANNEL}", "text/html"),
            ("legacy list API", f"{BASE}/etc/api/videoByUser/username/{CHANNEL}", "application/json"),
            ("category list page", f"{BASE}/user/video/list_cat/username/{CHANNEL}/page/1/perpage/12", "text/html"),
        ):
            result = fetch(url, accept)
            show(label, url, result)

            if result[0] == 200:
                summary["channel_ok"] = True

                for uid in find_uids(result[2]):
                    if uid not in uids:
                        uids.append(uid)

        summary["uids"] = len(uids)
        print(f"\nvideo ids found: {len(uids)} {uids[:8]}")

        for uid in uids[:MAX_VIDEOS]:
            check_video(f"{BASE}/v/{uid}", uid)

    print("\n" + "=" * 60)
    print(
        "RESULT | channel_reachable={channel_ok} | video_ids={uids} | "
        "videos_checked={videos_checked} | videos_with_media_url={videos_with_media} | "
        "ffprobe_ok={ffprobe_ok} | blocked_or_captcha={blocked}".format(**summary)
    )


if __name__ == "__main__":
    main()
