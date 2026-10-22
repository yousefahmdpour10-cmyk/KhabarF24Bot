"""
Media Extractor

پیدا کردن ویدئو و عکس داخل HTML یک صفحه (تگ video، متای Open Graph،
JSON-LD، ویژگی‌های data-* و ...). این فایل به شبکه یا RSS وابسته
نیست و فقط HTML را تحلیل می‌کند.
"""

import json
import re
from typing import Any, List, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

VIDEO_EXTENSIONS = (".mp4", ".webm", ".mov", ".m4v", ".m3u8", ".mpd")

# این دو قالب «پلی‌لیست» هستند، نه فایل ویدئو؛ مستقیم دانلود نمی‌شوند.
STREAM_EXTENSIONS = (".m3u8", ".mpd")

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")

VIDEO_MIME_TYPES = (
    "video/",
    "application/vnd.apple.mpegurl",
    "application/x-mpegurl",
    "application/dash+xml",
)

VIDEO_KEYS = {
    "contenturl", "content_url", "videourl", "video_url", "video",
    "video_src", "videosrc", "playbackurl", "playback_url",
    "streamurl", "stream_url", "mediacontent", "media_content_url",
    "mediaurl", "media_url", "fileurl", "file_url",
    "downloadurl", "download_url",
}

IMAGE_KEYS = {
    "thumbnailurl", "thumbnail_url", "image", "imageurl", "image_url",
    "thumbnail", "poster", "posterurl", "poster_url",
}

VIDEO_URL_RE = re.compile(r"""https?://[^\s"'<>\\]+""", re.IGNORECASE)

PLAYER_PATH_MARKERS = (
    "/av/embed/", "/iplayer/", "/video/", "/player/", "/embed/",
)

EMBED_HOSTS = ("youtube.com", "youtu.be", "player.vimeo.com")

OG_VIDEO_NAMES = {
    "og:video", "og:video:url", "og:video:secure_url",
    "twitter:player:stream",
}

OG_IMAGE_NAMES = {
    "og:image", "og:image:url", "twitter:image", "twitter:image:src",
}

DATA_ATTRS = (
    "data-video", "data-video-url", "data-video-src", "data-src",
    "data-media-url", "data-playback-url",
)

JSON_SCRIPT_IDS = {"__NEXT_DATA__", "__NUXT_DATA__"}

URL_PREFIXES = ("http://", "https://", "//", "/")


# ----------------------------------------------------------------------
# توابع ساده
# ----------------------------------------------------------------------

def url_path(url: str) -> str:
    """مسیر URL؛ برای آدرس خراب (مثل "https://[x") رشته‌ی خالی."""
    try:
        return urlparse(url).path.lower()
    except ValueError:
        return ""


def url_host(url: str) -> str:
    """نام سایت؛ برای آدرس خراب رشته‌ی خالی."""
    try:
        return (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""


def is_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def looks_like_image(url: str) -> bool:
    return url_path(url).endswith(IMAGE_EXTENSIONS)


def looks_like_video(url: str, media_type: str = "") -> bool:
    media_type = (media_type or "").lower()

    if any(media_type.startswith(t) for t in VIDEO_MIME_TYPES):
        return True

    return url_path(url).endswith(VIDEO_EXTENSIONS)


def guess_video_type(url: str) -> str:
    path = url_path(url)

    types = {
        ".m3u8": "application/vnd.apple.mpegurl",
        ".mpd": "application/dash+xml",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
        ".m4v": "video/x-m4v",
        ".mp4": "video/mp4",
    }

    for extension, media_type in types.items():
        if path.endswith(extension):
            return media_type

    return ""


def make_soup(markup: str) -> BeautifulSoup:
    """lxml چند برابر سریع‌تر است؛ اگر نبود به html.parser برمی‌گردیم."""
    try:
        return BeautifulSoup(markup, "lxml")
    except Exception:
        return BeautifulSoup(markup, "html.parser")


# ----------------------------------------------------------------------
# جمع‌کننده‌ی نتایج
# ----------------------------------------------------------------------

class MediaCollector:
    """کاندیدهای ویدئو و عکس را جمع می‌کند و بهترین‌ها را انتخاب می‌کند."""

    def __init__(self, page_url: str):
        self.page_url = page_url
        self.direct: List[Tuple[str, str]] = []
        self.weak: List[Tuple[str, str]] = []
        self.embeds: List[str] = []
        self.images: List[str] = []

    def absolute(self, url: Any) -> str:
        if not isinstance(url, str) or not url.strip():
            return ""

        try:
            url = urljoin(self.page_url, url.strip().replace("&amp;", "&"))
        except ValueError:
            return ""

        return url if is_http_url(url) else ""

    @staticmethod
    def is_player_page(url: str) -> bool:
        path = url_path(url)
        host = url_host(url)

        if any(marker in path for marker in PLAYER_PATH_MARKERS):
            return True

        return any(host == h or host.endswith("." + h) for h in EMBED_HOSTS)

    def add_embed(self, url: Any) -> None:
        url = self.absolute(url)

        if url and url not in self.embeds:
            self.embeds.append(url)

    def add_image(self, url: Any) -> None:
        url = self.absolute(url)

        if url and url not in self.images:
            self.images.append(url)

    def add_video(self, url: Any, media_type: str = "") -> None:
        url = self.absolute(url)

        if not url:
            return

        if looks_like_video(url, media_type):
            if url not in [u for u, _ in self.direct]:
                self.direct.append(
                    (url, media_type or guess_video_type(url))
                )

        elif self.is_player_page(url):
            self.add_embed(url)

        elif url not in [u for u, _ in self.weak]:
            # آدرسی که صراحتاً در یک فیلد «ویدئو» آمده ولی پسوند ندارد
            # (مثلاً CDN)؛ فقط اگر چیز بهتری نبود استفاده می‌شود.
            self.weak.append((url, media_type or "video"))

    def result(self) -> Tuple[str, str, str, str]:
        """
        (آدرس ویدئو، نوع ویدئو، آدرس عکس، آدرس player). هر مقدار پیدا
        نشد، رشته‌ی خالی است.
        """

        progressive = [
            item for item in self.direct
            if not url_path(item[0]).endswith(STREAM_EXTENSIONS)
        ]
        streams = [
            item[0] for item in self.direct if item not in progressive
        ]

        chosen = None
        if progressive:
            chosen = progressive[0]
        elif self.weak:
            chosen = self.weak[0]

        if self.embeds:
            embed = self.embeds[0]
        else:
            embed = streams[0] if streams else ""

        image = self.images[0] if self.images else ""

        if chosen:
            return chosen[0], chosen[1], image, embed

        return "", "", image, embed


# ----------------------------------------------------------------------
# اسکن بخش‌های مختلف صفحه
# ----------------------------------------------------------------------

def _scan_video_tags(soup: BeautifulSoup, c: MediaCollector) -> None:
    for video in soup.find_all("video"):
        c.add_video(video.get("src"))
        c.add_video(video.get("data-src"))

        for source in video.find_all("source"):
            c.add_video(
                source.get("src") or source.get("data-src"),
                source.get("type", ""),
            )

        c.add_image(video.get("poster") or video.get("data-poster"))


def _scan_iframes(soup: BeautifulSoup, c: MediaCollector) -> None:
    for iframe in soup.find_all("iframe"):
        src = c.absolute(iframe.get("src") or iframe.get("data-src"))

        if src and c.is_player_page(src):
            c.add_embed(src)


def _scan_meta(soup: BeautifulSoup, c: MediaCollector) -> None:
    for meta in soup.find_all("meta"):
        key = (
            meta.get("property")
            or meta.get("name")
            or meta.get("itemprop")
            or ""
        ).lower()

        value = meta.get("content", "")

        if not value:
            continue

        if key in OG_VIDEO_NAMES:
            c.add_video(value, meta.get("type", ""))
        elif key == "twitter:player":
            c.add_embed(value)
        elif key in OG_IMAGE_NAMES:
            c.add_image(value)


def _scan_scripts(soup: BeautifulSoup, c: MediaCollector) -> None:
    for script in soup.find_all("script"):
        script_type = str(script.get("type", "")).lower()
        text = script.string or script.get_text(strip=True)

        if not text:
            continue

        if (
            "json" in script_type
            or script.get("id") in JSON_SCRIPT_IDS
            or script_type == ""
        ):
            scan_json(text, c)


def _scan_data_attributes(soup: BeautifulSoup, c: MediaCollector) -> None:
    for tag in soup.find_all(True):
        for attr in DATA_ATTRS:
            value = tag.get(attr)

            if not (isinstance(value, str) and value.startswith(URL_PREFIXES)):
                continue

            candidate = c.absolute(value)

            if not candidate:
                continue

            # data-src روی تگ img عکس است؛ فقط اگر واقعاً شبیه ویدئو
            # بود قبول می‌کنیم.
            if looks_like_video(candidate) or attr != "data-src":
                c.add_video(candidate)


def _scan_raw_urls(text: str, c: MediaCollector) -> None:
    for match in VIDEO_URL_RE.findall(text):
        candidate = (
            match.replace("\\/", "/")
            .replace("\\u0026", "&")
            .rstrip("\\),;]}")
        )

        if looks_like_video(candidate):
            c.add_video(candidate)


def scan_json(text: str, c: MediaCollector) -> None:
    """آدرس ویدئو و عکس را از JSON-LD یا داده‌ی JSON داخل صفحه می‌گیرد."""

    def is_url_like(value: Any) -> bool:
        return isinstance(value, str) and value.strip().startswith(
            URL_PREFIXES
        )

    def handle_string(key: str, value: str) -> None:
        if not is_url_like(value):
            return

        if key in VIDEO_KEYS:
            c.add_video(value)
        elif key in IMAGE_KEYS:
            c.add_image(value)
        elif key in {"url", "src", "embedurl"} and looks_like_video(value):
            c.add_video(value)

    def walk(value: Any, depth: int = 0) -> None:
        if depth > 12:
            return

        if isinstance(value, dict):
            for raw_key, child in value.items():
                key = re.sub(r"[^a-z0-9_]", "", str(raw_key).lower())

                if isinstance(child, str):
                    handle_string(key, child)
                elif isinstance(child, (dict, list)):
                    walk(child, depth + 1)

        elif isinstance(value, list):
            for item in value:
                walk(item, depth + 1)

    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError, ValueError):
        # بعضی اسکریپت‌ها فقط تکه‌ای JSON دارند، نه یک سند کامل.
        data = None

    if data is not None:
        walk(data)

    # آدرس‌های escape شده، حتی وقتی کل اسکریپت JSON معتبر نیست.
    _scan_raw_urls(text, c)


# ----------------------------------------------------------------------
# تابع اصلی
# ----------------------------------------------------------------------

def extract_page_media(
    html: str,
    page_url: str,
) -> Tuple[str, str, str, str]:
    """
    Return:
        direct_video_url, video_content_type, image_url, embedded_player_url

    هر مقدار پیدا نشد، رشته‌ی خالی برمی‌گردد (نه None).
    """

    soup = make_soup(html)
    collector = MediaCollector(page_url)

    # هر مرحله مستقل است: اگر یکی با یک صفحه‌ی عجیب خطا داد، نتیجه‌ی
    # مرحله‌های دیگر از بین نرود.
    steps = (
        lambda: _scan_video_tags(soup, collector),
        lambda: _scan_iframes(soup, collector),
        lambda: _scan_meta(soup, collector),
        lambda: _scan_scripts(soup, collector),
        lambda: _scan_data_attributes(soup, collector),
        lambda: _scan_raw_urls(html, collector),
    )

    for step in steps:
        try:
            step()
        except Exception:
            continue

    return collector.result()
