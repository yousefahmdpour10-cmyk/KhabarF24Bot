"""
Media Extractor

پیدا کردن ویدئو و عکس داخل HTML یک صفحه.

منابع بررسی‌شده:
- <video>
- <source>
- <iframe>
- Open Graph
- Twitter Card
- JSON-LD
- JSONهای تو در تو
- data-* attributes
- URLهای خام داخل HTML / JavaScript
- VideoObject / ImageObject
- CDNهای ویدئویی بدون پسوند

خروجی:
    direct_video_url,
    video_content_type,
    image_url,
    embedded_player_url

نکته:
- direct_video_url باید قابل دانلود مستقیم باشد.
- embedded_player_url فقط آدرس player / iframe است و
  نباید مستقیماً به video downloader داده شود.
"""

import json
import re
from typing import Any, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


# ----------------------------------------------------------------------
# ثابت‌ها
# ----------------------------------------------------------------------

VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
    ".mkv",
    ".avi",
    ".m3u8",
    ".mpd",
)

STREAM_EXTENSIONS = (
    ".m3u8",
    ".mpd",
)

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".avif",
)

VIDEO_MIME_TYPES = (
    "video/",
    "application/vnd.apple.mpegurl",
    "application/x-mpegurl",
    "application/dash+xml",
)

STRONG_VIDEO_KEYS = {
    "videourl",
    "video_url",
    "video",
    "video_src",
    "videosrc",
    "video_source",
    "videosource",
    "playbackurl",
    "playback_url",
    "playback",
    "streamurl",
    "stream_url",
    "stream",
    "videofile",
    "video_file",
    "videofileurl",
    "video_file_url",
    "videoasset",
    "video_asset",
    "videoasseturl",
    "video_asset_url",
    "mediafile",
    "media_file",
}

AMBIGUOUS_MEDIA_KEYS = {
    "contenturl",
    "content_url",
    "mediacontent",
    "media_content",
    "mediacontenturl",
    "media_content_url",
    "mediaurl",
    "media_url",
    "fileurl",
    "file_url",
    "downloadurl",
    "download_url",
    "source",
    "src",
}

IMAGE_KEYS = {
    "thumbnailurl",
    "thumbnail_url",
    "image",
    "imageurl",
    "image_url",
    "thumbnail",
    "poster",
    "posterurl",
    "poster_url",
    "coverimage",
    "cover_image",
}

VIDEO_URL_RE = re.compile(
    r"""https?://[^\s"'<>\\]+""",
    re.IGNORECASE,
)

# URLهای escape شده داخل JSON/JS
ESCAPED_VIDEO_URL_RE = re.compile(
    r"""https?:\\?/\\?/[^\s"'<>\\]+""",
    re.IGNORECASE,
)

PLAYER_PATH_MARKERS = (
    "/av/embed/",
    "/iplayer/",
    "/video/",
    "/player/",
    "/embed/",
    "/watch/",
    "/live/",
    "/stream/",
    "/clip/",
    "/clips/",
)

EMBED_HOSTS = (
    "youtube.com",
    "youtu.be",
    "youtube-nocookie.com",
    "player.vimeo.com",
    "vimeo.com",
)

DATA_ATTRS = (
    "data-video",
    "data-video-url",
    "data-video-src",
    "data-video-source",
    "data-src",
    "data-media-url",
    "data-media-src",
    "data-playback-url",
    "data-playback-src",
    "data-stream-url",
    "data-stream-src",
    "data-file-url",
    "data-video-id",
)

OG_VIDEO_NAMES = {
    "og:video",
    "og:video:url",
    "og:video:secure_url",
    "twitter:player:stream",
}

OG_IMAGE_NAMES = {
    "og:image",
    "og:image:url",
    "twitter:image",
    "twitter:image:src",
}

JSON_SCRIPT_IDS = {
    "__NEXT_DATA__",
    "__NUXT_DATA__",
    "__APOLLO_STATE__",
}

PLACEHOLDER_IMAGE_RE = re.compile(
    r"(googleusercontent\.com|news\.google\.com|gstatic\.com"
    r"|favicon|apple-touch-icon"
    r"|[/_.\-]logo[/_.\-]|[/_.\-]logo\."
    r"|placeholder|default[-_]?(?:image|og|share|thumb)"
    r"|no[-_]?image|blank\.(?:png|jpe?g|gif)|spacer\.|sprite)",
    re.IGNORECASE,
)

URL_PREFIXES = (
    "http://",
    "https://",
    "//",
    "/",
)


# ----------------------------------------------------------------------
# URL helpers
# ----------------------------------------------------------------------

def url_path(url: str) -> str:
    """مسیر URL؛ برای آدرس خراب رشته خالی."""
    try:
        return urlparse(url).path.lower()
    except ValueError:
        return ""


def url_host(url: str) -> str:
    """نام host؛ برای URL خراب رشته خالی."""
    try:
        return (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""


def is_http_url(url: str) -> bool:
    """آیا URL معتبر HTTP/HTTPS است؟"""
    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )

    except Exception:
        return False


def is_placeholder_image(url: str) -> bool:
    """آیا URL مربوط به لوگو/آیکن/placeholder است؟"""
    return bool(
        PLACEHOLDER_IMAGE_RE.search(url or "")
    )


def looks_like_image(url: str) -> bool:
    """تشخیص تصویر بر اساس پسوند."""
    return url_path(url).endswith(
        IMAGE_EXTENSIONS
    )


def looks_like_video(
    url: str,
    media_type: str = "",
) -> bool:
    """
    تشخیص ویدئو بر اساس MIME یا پسوند.

    نکته:
    URLهای بدون پسوند فقط زمانی ویدئو شناخته می‌شوند
    که media_type صراحتاً ویدئویی باشد.
    """

    media_type = (
        media_type or ""
    ).lower().split(";")[0].strip()

    if any(
        media_type.startswith(media)
        for media in VIDEO_MIME_TYPES
    ):
        return True

    return url_path(url).endswith(
        VIDEO_EXTENSIONS
    )


def guess_video_type(url: str) -> str:
    """حدس MIME type بر اساس پسوند."""

    path = url_path(url)

    types = {
        ".m3u8": "application/vnd.apple.mpegurl",
        ".mpd": "application/dash+xml",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
        ".m4v": "video/x-m4v",
        ".mkv": "video/x-matroska",
        ".avi": "video/x-msvideo",
        ".mp4": "video/mp4",
    }

    for extension, media_type in types.items():
        if path.endswith(extension):
            return media_type

    return ""


def make_soup(markup: str) -> BeautifulSoup:
    """ساخت BeautifulSoup با lxml و fallback."""

    try:
        return BeautifulSoup(
            markup,
            "lxml",
        )
    except Exception:
        return BeautifulSoup(
            markup,
            "html.parser",
        )


def normalize_candidate_url(
    url: Any,
    base_url: str,
) -> str:
    """تبدیل URL نسبی/escape شده به URL مطلق."""

    if not isinstance(url, str):
        return ""

    value = (
        url.strip()
        .replace("&amp;", "&")
        .replace("\\/", "/")
        .replace("\\u002F", "/")
        .replace("\\u002f", "/")
        .replace("\\u0026", "&")
    )

    if not value:
        return ""

    try:
        value = urljoin(
            base_url,
            value,
        )
    except ValueError:
        return ""

    if not is_http_url(value):
        return ""

    return value


# ----------------------------------------------------------------------
# Media Collector
# ----------------------------------------------------------------------

class MediaCollector:
    """
    جمع‌آوری کاندیدهای ویدئو، player و تصویر.

    direct:
        ویدئویی که احتمالاً مستقیماً قابل دانلود است.

    weak:
        URLی که در یک فیلد ویدئویی آمده ولی پسوند/MIME واضح ندارد.

    embeds:
        player / iframe / صفحه پخش.

    images:
        تصاویر کاندید.
    """

    def __init__(
        self,
        page_url: str,
    ):
        self.page_url = page_url

        self.direct: List[
            Tuple[str, str]
        ] = []

        self.weak: List[
            Tuple[str, str]
        ] = []

        self.embeds: List[str] = []

        self.images: List[str] = []

    # --------------------------------------------------------------
    # URL
    # --------------------------------------------------------------

    def absolute(
        self,
        url: Any,
    ) -> str:
        return normalize_candidate_url(
            url,
            self.page_url,
        )

    # --------------------------------------------------------------
    # Player
    # --------------------------------------------------------------

    @staticmethod
    def is_player_page(
        url: str,
    ) -> bool:
        path = url_path(url)
        host = url_host(url)

        if any(
            marker in path
            for marker in PLAYER_PATH_MARKERS
        ):
            return True

        return any(
            host == host_name
            or host.endswith("." + host_name)
            for host_name in EMBED_HOSTS
        )

    # --------------------------------------------------------------
    # Add embed
    # --------------------------------------------------------------

    def add_embed(
        self,
        url: Any,
    ) -> None:
        url = self.absolute(url)

        if not url:
            return

        if url not in self.embeds:
            self.embeds.append(url)

    # --------------------------------------------------------------
    # Add image
    # --------------------------------------------------------------

    def add_image(
        self,
        url: Any,
    ) -> None:
        url = self.absolute(url)

        if not url:
            return

        if is_placeholder_image(url):
            return

        if looks_like_video(url):
            return

        if url not in self.images:
            self.images.append(url)

    # --------------------------------------------------------------
    # Add video
    # --------------------------------------------------------------

    def add_video(
        self,
        url: Any,
        media_type: str = "",
    ) -> None:
        url = self.absolute(url)

        if not url:
            return

        media_type = (
            media_type or ""
        ).lower().split(";")[0].strip()

        # ویدئوی مستقیم یا stream
        if looks_like_video(
            url,
            media_type,
        ):
            if url not in [
                item[0]
                for item in self.direct
            ]:
                self.direct.append(
                    (
                        url,
                        media_type
                        or guess_video_type(url),
                    )
                )

            return

        # Player / iframe
        if self.is_player_page(url):
            self.add_embed(url)
            return

        # تصویر را هرگز ویدئو حساب نکن
        if looks_like_image(url):
            return

        # اگر صراحتاً در فیلد ویدئو آمده ولی پسوند ندارد،
        # به عنوان weak candidate نگه می‌داریم.
        if url not in [
            item[0]
            for item in self.weak
        ]:
            self.weak.append(
                (
                    url,
                    media_type or "video",
                )
            )

    # --------------------------------------------------------------
    # Result
    # --------------------------------------------------------------

    def result(
        self,
    ) -> Tuple[str, str, str, str]:
        """
        خروجی:

        direct_video_url,
        video_content_type,
        image_url,
        embedded_player_url
        """

        progressive = [
            item
            for item in self.direct
            if not url_path(
                item[0]
            ).endswith(
                STREAM_EXTENSIONS
            )
        ]

        streams = [
            item
            for item in self.direct
            if url_path(
                item[0]
            ).endswith(
                STREAM_EXTENSIONS
            )
        ]

        chosen: Optional[
            Tuple[str, str]
        ] = None

        # اول MP4/WebM/MOV و ...
        if progressive:
            chosen = progressive[0]

        # سپس CDN بدون پسوند
        elif self.weak:
            chosen = self.weak[0]

        # m3u8/mpd فعلاً به عنوان embed
        # برگردانده می‌شود تا publisher آن را
        # به عنوان فایل معمولی دانلود نکند.
        if self.embeds:
            embed = self.embeds[0]

        elif streams:
            embed = streams[0][0]

        else:
            embed = ""

        image = (
            self.images[0]
            if self.images
            else ""
        )

        if chosen:
            return (
                chosen[0],
                chosen[1],
                image,
                embed,
            )

        return (
            "",
            "",
            image,
            embed,
        )


# ----------------------------------------------------------------------
# Video tag
# ----------------------------------------------------------------------

def _scan_video_tags(
    soup: BeautifulSoup,
    collector: MediaCollector,
) -> None:
    for video in soup.find_all("video"):
        collector.add_video(
            video.get("src")
        )

        collector.add_video(
            video.get("data-src")
        )

        collector.add_video(
            video.get("data-video")
        )

        collector.add_video(
            video.get("data-video-url")
        )

        for source in video.find_all("source"):
            collector.add_video(
                source.get("src")
                or source.get("data-src"),
                source.get("type", ""),
            )

        collector.add_image(
            video.get("poster")
            or video.get("data-poster")
        )


# ----------------------------------------------------------------------
# Iframe
# ----------------------------------------------------------------------

def _scan_iframes(
    soup: BeautifulSoup,
    collector: MediaCollector,
) -> None:
    for iframe in soup.find_all("iframe"):
        src = collector.absolute(
            iframe.get("src")
            or iframe.get("data-src")
        )

        if not src:
            continue

        if collector.is_player_page(src):
            collector.add_embed(src)

        elif looks_like_video(src):
            collector.add_video(src)

        else:
            # iframeهای ناشناس ممکن است
            # player اختصاصی سایت باشند.
            path = url_path(src)

            if any(
                marker in path
                for marker in PLAYER_PATH_MARKERS
            ):
                collector.add_embed(src)


# ----------------------------------------------------------------------
# Meta
# ----------------------------------------------------------------------

def _scan_meta(
    soup: BeautifulSoup,
    collector: MediaCollector,
) -> None:
    for meta in soup.find_all("meta"):
        key = (
            meta.get("property")
            or meta.get("name")
            or meta.get("itemprop")
            or ""
        ).lower().strip()

        value = meta.get(
            "content",
            "",
        )

        if not value:
            continue

        if key in OG_VIDEO_NAMES:
            collector.add_video(
                value,
                meta.get("type", ""),
            )

        elif key in OG_IMAGE_NAMES:
            collector.add_image(value)

        elif key in (
            "video",
            "video:url",
            "video:secure_url",
        ):
            collector.add_video(
                value,
                meta.get("type", ""),
            )

        elif key in (
            "image",
            "image:url",
        ):
            collector.add_image(value)


# ----------------------------------------------------------------------
# Data attributes
# ----------------------------------------------------------------------

def _scan_data_attributes(
    soup: BeautifulSoup,
    collector: MediaCollector,
) -> None:
    for tag in soup.find_all(True):
        for attr in DATA_ATTRS:
            value = tag.get(attr)

            if not isinstance(
                value,
                str,
            ):
                continue

            if not value.strip():
                continue

            candidate = collector.absolute(
                value
            )

            if not candidate:
                continue

            # data-src روی img معمولاً عکس است.
            if (
                attr == "data-src"
                and tag.name == "img"
            ):
                if looks_like_image(
                    candidate
                ):
                    collector.add_image(
                        candidate
                    )

                continue

            if (
                looks_like_video(candidate)
                or attr != "data-src"
            ):
                collector.add_video(
                    candidate
                )


# ----------------------------------------------------------------------
# Raw URL extraction
# ----------------------------------------------------------------------

def _clean_raw_url(
    value: str,
) -> str:
    return (
        value
        .replace("\\/", "/")
        .replace("\\u002F", "/")
        .replace("\\u002f", "/")
        .replace("\\u0026", "&")
        .rstrip(
            "\\),;]}"
        )
    )


def _scan_raw_urls(
    text: str,
    collector: MediaCollector,
) -> None:
    if not text:
        return

    # URLهای عادی
    for match in VIDEO_URL_RE.findall(
        text
    ):
        candidate = _clean_raw_url(
            match
        )

        if looks_like_video(candidate):
            collector.add_video(
                candidate
            )

        elif (
            collector.is_player_page(
                candidate
            )
        ):
            collector.add_embed(
                candidate
            )

    # URLهای escape شده
    for match in ESCAPED_VIDEO_URL_RE.findall(
        text
    ):
        candidate = _clean_raw_url(
            match
        )

        if looks_like_video(candidate):
            collector.add_video(
                candidate
            )

        elif (
            collector.is_player_page(
                candidate
            )
        ):
            collector.add_embed(
                candidate
            )


# ----------------------------------------------------------------------
# JSON
# ----------------------------------------------------------------------

def scan_json(
    text: str,
    collector: MediaCollector,
) -> None:
    """
    استخراج ویدئو/عکس از JSON-LD و JSONهای داخلی.

    برای جلوگیری از خطا در JSONهای بزرگ یا ناقص،
    هم JSON کامل و هم raw URL scan انجام می‌شود.
    """

    def is_url_like(
        value: Any,
    ) -> bool:
        return (
            isinstance(value, str)
            and value.strip().startswith(
                URL_PREFIXES
            )
        )

    def normalize_key(
        raw_key: Any,
    ) -> str:
        return re.sub(
            r"[^a-z0-9_]",
            "",
            str(raw_key).lower(),
        )

    def handle_string(
        key: str,
        value: str,
        is_video_node: bool,
        is_image_node: bool,
        media_type: str = "",
    ) -> None:
        if not is_url_like(
            value
        ):
            return

        if key in IMAGE_KEYS:
            collector.add_image(
                value
            )
            return

        if key in STRONG_VIDEO_KEYS:
            collector.add_video(
                value,
                media_type,
            )
            return

        if key in AMBIGUOUS_MEDIA_KEYS:
            if is_image_node:
                collector.add_image(
                    value
                )

            elif (
                is_video_node
                or looks_like_video(
                    value,
                    media_type,
                )
            ):
                collector.add_video(
                    value,
                    media_type,
                )

            elif looks_like_image(
                value
            ):
                collector.add_image(
                    value
                )

            return

        if key in (
            "embedurl",
            "embed_url",
            "playerurl",
            "player_url",
        ):
            collector.add_embed(
                value
            )
            return

        if key in (
            "url",
            "src",
        ):
            if is_video_node:
                collector.add_video(
                    value,
                    media_type,
                )

            elif is_image_node:
                collector.add_image(
                    value
                )

            elif looks_like_video(
                value,
                media_type,
            ):
                collector.add_video(
                    value,
                    media_type,
                )

            return

    def walk(
        value: Any,
        depth: int = 0,
        inherited_video: bool = False,
        inherited_image: bool = False,
    ) -> None:
        # عمق بالا می‌تواند JSONهای بسیار بزرگ ایجاد کند.
        if depth > 16:
            return

        if isinstance(
            value,
            dict,
        ):
            node_type = str(
                value.get("@type")
                or value.get("type")
                or ""
            ).lower()

            encoding = str(
                value.get(
                    "encodingFormat"
                )
                or value.get(
                    "contentType"
                )
                or value.get(
                    "mimeType"
                )
                or ""
            ).lower()

            current_video = (
                inherited_video
                or "video" in node_type
                or encoding.startswith(
                    "video/"
                )
            )

            current_image = (
                inherited_image
                or "image" in node_type
                or encoding.startswith(
                    "image/"
                )
            )

            media_type = (
                encoding
                if encoding
                else str(
                    value.get(
                        "type",
                        "",
                    )
                )
            )

            for raw_key, child in value.items():
                key = normalize_key(
                    raw_key
                )

                if isinstance(
                    child,
                    str,
                ):
                    handle_string(
                        key,
                        child,
                        current_video,
                        current_image,
                        media_type,
                    )

                elif isinstance(
                    child,
                    (
                        dict,
                        list,
                    ),
                ):
                    walk(
                        child,
                        depth + 1,
                        current_video,
                        current_image,
                    )

        elif isinstance(
            value,
            list,
        ):
            for item in value:
                walk(
                    item,
                    depth + 1,
                    inherited_video,
                    inherited_image,
                )

    try:
        data = json.loads(
            text
        )

        walk(data)

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):
        # بعضی JSها JSON کامل نیستند.
        # در این حالت raw URL scan پایین‌تر
        # همچنان کار می‌کند.
        pass

    # URLهای داخل JSON/JS حتی اگر JSON کامل parse نشود.
    _scan_raw_urls(
        text,
        collector,
    )


# ----------------------------------------------------------------------
# Script scanner
# ----------------------------------------------------------------------

def _scan_scripts(
    soup: BeautifulSoup,
    collector: MediaCollector,
) -> None:
    for script in soup.find_all(
        "script"
    ):
        script_type = str(
            script.get(
                "type",
                "",
            )
        ).lower()

        script_id = script.get(
            "id"
        )

        text = (
            script.string
            or script.get_text(
                strip=True
            )
        )

        if not text:
            continue

        # JSON-LD / Next.js / Nuxt / Apollo
        if (
            "json" in script_type
            or script_id in JSON_SCRIPT_IDS
            or script_type == ""
        ):
            scan_json(
                text,
                collector,
            )

        # حتی scriptهای غیر JSON نیز
        # ممکن است URL ویدئو داشته باشند.
        else:
            _scan_raw_urls(
                text,
                collector,
            )


# ----------------------------------------------------------------------
# Link tags
# ----------------------------------------------------------------------

def _scan_links(
    soup: BeautifulSoup,
    collector: MediaCollector,
) -> None:
    for link in soup.find_all(
        "link"
    ):
        href = link.get(
            "href"
        )

        if not href:
            continue

        rel = " ".join(
            link.get(
                "rel",
                [],
            )
        ).lower()

        media_type = str(
            link.get(
                "type",
                "",
            )
        ).lower()

        candidate = collector.absolute(
            href
        )

        if not candidate:
            continue

        if (
            "video" in rel
            or looks_like_video(
                candidate,
                media_type,
            )
        ):
            collector.add_video(
                candidate,
                media_type,
            )

        elif (
            "image" in rel
            or looks_like_image(
                candidate
            )
        ):
            collector.add_image(
                candidate
            )


# ----------------------------------------------------------------------
# HTML source tags
# ----------------------------------------------------------------------

def _scan_source_tags(
    soup: BeautifulSoup,
    collector: MediaCollector,
) -> None:
    for source in soup.find_all(
        "source"
    ):
        src = (
            source.get("src")
            or source.get("data-src")
        )

        if not src:
            continue

        media_type = str(
            source.get(
                "type",
                "",
            )
        )

        collector.add_video(
            src,
            media_type,
        )


# ----------------------------------------------------------------------
# Main extractor
# ----------------------------------------------------------------------

def extract_page_media(
    html: str,
    page_url: str,
) -> Tuple[str, str, str, str]:
    """
    Return:

        direct_video_url,
        video_content_type,
        image_url,
        embedded_player_url

    هر مقدار پیدا نشد، رشته خالی برمی‌گرداند.

    ترتیب جست‌وجو:
    1. video/source
    2. iframe
    3. meta
    4. link
    5. scripts / JSON-LD
    6. data-* attributes
    7. raw URLs
    """

    if not html or not page_url:
        return (
            "",
            "",
            "",
            "",
        )

    soup = make_soup(
        html
    )

    collector = MediaCollector(
        page_url
    )

    steps = (
        lambda: _scan_video_tags(
            soup,
            collector,
        ),
        lambda: _scan_source_tags(
            soup,
            collector,
        ),
        lambda: _scan_iframes(
            soup,
            collector,
        ),
        lambda: _scan_meta(
            soup,
            collector,
        ),
        lambda: _scan_links(
            soup,
            collector,
        ),
        lambda: _scan_scripts(
            soup,
            collector,
        ),
        lambda: _scan_data_attributes(
            soup,
            collector,
        ),
        lambda: _scan_raw_urls(
            html,
            collector,
        ),
    )

    for step in steps:
        try:
            step()
        except Exception:
            # خرابی یک بخش نباید استخراج
            # بخش‌های دیگر را متوقف کند.
            continue

    return collector.result()
