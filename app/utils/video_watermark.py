"""
KhabarF24 Video Watermark
افزودن لوگوی KhabarF24 به ویدئو بدون تغییر ابعاد ویدئوی اصلی.

پشتیبانی:
- ویدئوی مستقیم MP4 / WebM / MOV / M4V / AVI / MKV
- استریم HLS با M3U8
- استریم MPEG-DASH با MPD
- لینک‌های CDN بدون پسوند مشخص
- رد کردن صفحات HTML / Player

نیازمندی‌ها:
- ffmpeg
- ffprobe
- aiohttp
- Pillow

خروجی:
- فایل موقت MP4 واترمارک‌شده
- در صورت خطا یا عبور از محدودیت‌ها: None
"""

import asyncio
import logging
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
from PIL import Image


logger = logging.getLogger(__name__)


# ======================================================================
# مسیر پایه
# ======================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "khabarf24_header_transparent_final.png"
)


# ======================================================================
# محدودیت‌ها
# ======================================================================

# حداکثر حجم دانلود فایل ویدئویی مستقیم
MAX_DOWNLOAD_BYTES = 150 * 1024 * 1024

# حداکثر حجم خروجی برای ارسال به تلگرام
# کمی پایین‌تر از سقف 50MB نگه داشته شده تا حاشیه امن داشته باشیم.
MAX_OUTPUT_BYTES = 49 * 1024 * 1024

# حداکثر مدت ویدئو
MAX_DURATION_SECONDS = 180

# timeout دانلود فایل مستقیم
DOWNLOAD_TIMEOUT_SECONDS = 90

# timeout پردازش FFmpeg
PROCESS_TIMEOUT_SECONDS = 240


# ======================================================================
# تنظیمات ویدئو
# ======================================================================

# عرض لوگو نسبت به عرض ویدئو
LOGO_WIDTH_RATIO = 0.24

# فاصله لوگو از لبه‌ها
LOGO_MARGIN_RATIO = 0.04

# کیفیت خروجی
VIDEO_CRF = "23"

# سرعت پردازش
VIDEO_PRESET = "veryfast"


# ======================================================================
# پسوندها
# ======================================================================

DIRECT_VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
    ".avi",
    ".mkv",
)

STREAM_EXTENSIONS = (
    ".m3u8",
    ".mpd",
)


# ======================================================================
# ابزارهای کمکی
# ======================================================================

def _tool_exists(name: str) -> bool:
    """
    بررسی نصب بودن ابزار سیستمی.
    """

    return shutil.which(name) is not None


def _is_stream_url(url: str) -> bool:
    """
    تشخیص لینک HLS / DASH.

    مثال:

        https://cdn.example.com/video/index.m3u8
        https://cdn.example.com/stream/manifest.mpd
    """

    if not url:
        return False

    try:
        parsed = urlparse(url)
        path = (parsed.path or "").lower()

        return path.endswith(STREAM_EXTENSIONS)

    except Exception:
        return False


def _is_direct_video_url(url: str) -> bool:
    """
    تشخیص تقریبی لینک ویدئوی مستقیم.
    """

    if not url:
        return False

    try:
        parsed = urlparse(url)
        path = (parsed.path or "").lower()

        return path.endswith(DIRECT_VIDEO_EXTENSIONS)

    except Exception:
        return False


def _format_bytes(size: int) -> str:
    """
    تبدیل تعداد بایت به نمایش خوانا.
    """

    if size < 1024:
        return f"{size} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"

    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"

    return f"{size / (1024 * 1024 * 1024):.2f} GB"


async def _run_command(
    *args: str,
    timeout: int = PROCESS_TIMEOUT_SECONDS,
):
    """
    اجرای دستور سیستمی به‌صورت غیرهم‌زمان.

    خروجی stdout و stderr را برمی‌گرداند.
    """

    logger.debug(
        "Running command: %s",
        " ".join(str(arg) for arg in args),
    )

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout,
        )

    except asyncio.TimeoutError:

        logger.error(
            "Command timed out after %ss: %s",
            timeout,
            args[0],
        )

        try:
            process.kill()
        except ProcessLookupError:
            pass

        await process.communicate()

        raise RuntimeError(
            f"Command timed out: {args[0]}"
        )

    if process.returncode != 0:

        error_text = stderr.decode(
            "utf-8",
            errors="replace",
        )[-6000:]

        logger.error(
            "Command failed | returncode=%s | command=%s | stderr=%s",
            process.returncode,
            args[0],
            error_text,
        )

        raise RuntimeError(
            f"Command failed ({process.returncode}): "
            f"{args[0]}\n{error_text}"
        )

    return stdout, stderr


# ======================================================================
# دانلود ویدئوی مستقیم
# ======================================================================

async def _download_video(
    url: str,
    destination: Path,
    session: aiohttp.ClientSession,
) -> bool:
    """
    دانلود ویدئوی مستقیم با محدودیت حجم.

    این تابع برای MP4/WebM/MOV و CDNهای مستقیم استفاده می‌شود.

    صفحات HTML و استریم‌های M3U8/MPD عمداً اینجا دانلود نمی‌شوند.
    """

    if not url or not url.startswith(
        ("http://", "https://")
    ):
        logger.warning(
            "VIDEO_DOWNLOAD_INVALID_URL | url=%s",
            url[:180] if url else "",
        )
        return False

    try:

        logger.info(
            "VIDEO_DOWNLOAD_START | url=%s",
            url[:180],
        )

        timeout = aiohttp.ClientTimeout(
            total=DOWNLOAD_TIMEOUT_SECONDS,
            connect=20,
            sock_read=30,
        )

        async with session.get(
            url,
            timeout=timeout,
            allow_redirects=True,
        ) as response:

            final_url = str(response.url)

            content_type = (
                response.headers.get("Content-Type")
                or ""
            ).lower()

            content_length = (
                response.headers.get("Content-Length")
                or ""
            )

            logger.info(
                "VIDEO_HTTP_RESPONSE | status=%s | "
                "content_type=%s | content_length=%s | "
                "final_url=%s",
                response.status,
                content_type,
                content_length or "-",
                final_url[:180],
            )

            if response.status != 200:

                logger.warning(
                    "VIDEO_DOWNLOAD_HTTP_ERROR | "
                    "status=%s | url=%s",
                    response.status,
                    url[:180],
                )

                return False

            # ----------------------------------------------------------
            # رد HTML / صفحه Player
            # ----------------------------------------------------------

            if (
                content_type.startswith("image/")
                or content_type.startswith("text/")
                or "html" in content_type
            ):

                logger.warning(
                    "VIDEO_URL_NOT_DIRECT_MEDIA | "
                    "content_type=%s | url=%s",
                    content_type,
                    url[:180],
                )

                return False

            # ----------------------------------------------------------
            # Manifest
            # ----------------------------------------------------------

            if (
                "mpegurl" in content_type
                or "m3u8" in content_type
                or "dash+xml" in content_type
            ):

                logger.warning(
                    "VIDEO_STREAM_MANIFEST_DETECTED | "
                    "content_type=%s | url=%s",
                    content_type,
                    url[:180],
                )

                return False

            # ----------------------------------------------------------
            # بررسی Content-Length
            # ----------------------------------------------------------

            if content_length:

                try:

                    declared_size = int(
                        content_length
                    )

                    if declared_size > MAX_DOWNLOAD_BYTES:

                        logger.warning(
                            "VIDEO_DOWNLOAD_TOO_LARGE | "
                            "declared=%s | limit=%s | url=%s",
                            _format_bytes(declared_size),
                            _format_bytes(
                                MAX_DOWNLOAD_BYTES
                            ),
                            url[:180],
                        )

                        return False

                except ValueError:
                    logger.debug(
                        "Invalid Content-Length: %s",
                        content_length,
                    )

            # ----------------------------------------------------------
            # دانلود
            # ----------------------------------------------------------

            downloaded = 0

            with destination.open("wb") as output:

                async for chunk in response.content.iter_chunked(
                    64 * 1024
                ):

                    if not chunk:
                        continue

                    downloaded += len(chunk)

                    if downloaded > MAX_DOWNLOAD_BYTES:

                        logger.warning(
                            "VIDEO_DOWNLOAD_LIMIT_EXCEEDED | "
                            "downloaded=%s | limit=%s | url=%s",
                            _format_bytes(downloaded),
                            _format_bytes(
                                MAX_DOWNLOAD_BYTES
                            ),
                            url[:180],
                        )

                        return False

                    output.write(chunk)

            if downloaded == 0:

                logger.warning(
                    "VIDEO_DOWNLOAD_EMPTY | url=%s",
                    url[:180],
                )

                return False

            logger.info(
                "VIDEO_DOWNLOAD_SUCCESS | "
                "size=%s | content_type=%s | url=%s",
                _format_bytes(downloaded),
                content_type or "unknown",
                url[:180],
            )

            return True

    except (
        aiohttp.ClientError,
        asyncio.TimeoutError,
        OSError,
    ) as exc:

        logger.warning(
            "VIDEO_DOWNLOAD_ERROR | "
            "type=%s | error=%s | url=%s",
            type(exc).__name__,
            exc,
            url[:180],
        )

        return False


# ======================================================================
# اطلاعات ویدئو
# ======================================================================

async def _get_video_info(
    video_input: str | Path,
) -> dict:
    """
    خواندن مدت و ابعاد ویدئو با ffprobe.

    video_input می‌تواند:
    - مسیر فایل محلی
    - URL مستقیم
    - M3U8
    - MPD
    باشد.
    """

    input_value = str(video_input)

    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height:format=duration",
        "-of",
        "default=noprint_wrappers=1",
    ]

    # برای URLهای HTTP/HTTPS یک User-Agent بده.
    if input_value.startswith(
        ("http://", "https://")
    ):

        command.extend(
            [
                "-user_agent",
                (
                    "Mozilla/5.0 "
                    "(compatible; KhabarF24Bot/1.0)"
                ),
            ]
        )

    command.append(input_value)

    logger.info(
        "VIDEO_PROBE_START | input=%s",
        input_value[:180],
    )

    try:

        stdout, stderr = await _run_command(
            *command,
            timeout=60,
        )

    except Exception as exc:

        logger.error(
            "VIDEO_PROBE_FAILED | "
            "type=%s | error=%s | input=%s",
            type(exc).__name__,
            exc,
            input_value[:180],
        )

        raise

    info = {}

    for line in stdout.decode(
        "utf-8",
        errors="replace",
    ).splitlines():

        if "=" not in line:
            continue

        key, value = line.split(
            "=",
            1,
        )

        info[key.strip()] = value.strip()

    try:

        width = int(
            info.get("width", "0")
        )

        height = int(
            info.get("height", "0")
        )

        duration = float(
            info.get("duration", "0")
        )

    except (
        ValueError,
        TypeError,
    ) as exc:

        raise RuntimeError(
            "Could not read video dimensions or duration."
        ) from exc

    if width <= 0 or height <= 0:

        raise RuntimeError(
            f"Invalid video dimensions: "
            f"{width}x{height}"
        )

    if duration <= 0:

        raise RuntimeError(
            f"Invalid video duration: {duration}"
        )

    result = {
        "width": width,
        "height": height,
        "duration": duration,
    }

    logger.info(
        "VIDEO_PROBE_SUCCESS | "
        "width=%s | height=%s | duration=%.2fs",
        width,
        height,
        duration,
    )

    return result


# ======================================================================
# لوگو
# ======================================================================

def _prepare_logo(
    source_logo: Path,
    destination: Path,
    video_width: int,
):
    """
    ساخت نسخه‌ای از لوگو با عرض متناسب با ویدئو.
    """

    if not source_logo.is_file():

        raise FileNotFoundError(
            f"Logo file not found: {source_logo}"
        )

    logger.info(
        "VIDEO_LOGO_PREPARE | source=%s | video_width=%s",
        source_logo,
        video_width,
    )

    with Image.open(source_logo) as image:

        logo = image.convert("RGBA")

        if logo.width <= 0 or logo.height <= 0:

            raise RuntimeError(
                "Invalid logo dimensions."
            )

        target_width = max(
            1,
            int(
                video_width
                * LOGO_WIDTH_RATIO
            ),
        )

        target_width = min(
            target_width,
            video_width,
        )

        target_height = max(
            1,
            round(
                logo.height
                * target_width
                / logo.width
            ),
        )

        logo = logo.resize(
            (
                target_width,
                target_height,
            ),
            Image.Resampling.LANCZOS,
        )

        logo.save(
            destination,
            format="PNG",
            optimize=True,
        )

    logger.info(
        "VIDEO_LOGO_READY | width=%s | height=%s | path=%s",
        target_width,
        target_height,
        destination,
    )

    return destination


# ======================================================================
# پردازش ویدئو
# ======================================================================

async def _encode_watermarked_video(
    input_source: str | Path,
    logo_path: Path,
    output_path: Path,
) -> None:
    """
    اجرای FFmpeg و افزودن لوگو.

    input_source می‌تواند:
    - فایل محلی
    - URL مستقیم
    - M3U8
    - MPD
    باشد.
    """

    filter_graph = (
        "[1:v]format=rgba[logo];"
        "[0:v][logo]overlay="
        f"x=main_w*{LOGO_MARGIN_RATIO}:"
        f"y=main_h-overlay_h-main_h*{LOGO_MARGIN_RATIO}:"
        "format=auto[v]"
    )

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-y",
    ]

    # ----------------------------------------------------------
    # ورودی اصلی
    # ----------------------------------------------------------

    if (
        isinstance(input_source, str)
        and input_source.startswith(
            ("http://", "https://")
        )
    ):

        command.extend(
            [
                "-user_agent",
                (
                    "Mozilla/5.0 "
                    "(compatible; KhabarF24Bot/1.0)"
                ),
            ]
        )

    command.extend(
        [
            "-i",
            str(input_source),

            # --------------------------------------------------
            # لوگو
            # --------------------------------------------------

            "-loop",
            "1",
            "-i",
            str(logo_path),

            # --------------------------------------------------
            # فیلتر
            # --------------------------------------------------

            "-filter_complex",
            filter_graph,

            # --------------------------------------------------
            # ویدئو
            # --------------------------------------------------

            "-map",
            "[v]",

            # --------------------------------------------------
            # صدا
            # --------------------------------------------------

            "-map",
            "0:a?",

            # --------------------------------------------------
            # Video codec
            # --------------------------------------------------

            "-c:v",
            "libx264",

            "-preset",
            VIDEO_PRESET,

            "-crf",
            VIDEO_CRF,

            "-pix_fmt",
            "yuv420p",

            # --------------------------------------------------
            # Audio codec
            # --------------------------------------------------

            "-c:a",
            "aac",

            "-b:a",
            "192k",

            # --------------------------------------------------
            # MP4
            # --------------------------------------------------

            "-movflags",
            "+faststart",

            "-max_muxing_queue_size",
            "2048",

            # --------------------------------------------------
            # خروجی
            # --------------------------------------------------

            str(output_path),
        ]
    )

    # ----------------------------------------------------------
    # برای M3U8 / MPD
    # ----------------------------------------------------------

    if (
        isinstance(input_source, str)
        and _is_stream_url(input_source)
    ):

        command.insert(
            1,
            "-protocol_whitelist",
        )

        command.insert(
            2,
            "file,http,https,tcp,tls,crypto",
        )

    logger.info(
        "VIDEO_FFMPEG_START | input=%s | output=%s",
        str(input_source)[:180],
        output_path,
    )

    try:

        await _run_command(
            *command,
            timeout=PROCESS_TIMEOUT_SECONDS,
        )

    except Exception as exc:

        logger.error(
            "VIDEO_FFMPEG_FAILED | "
            "type=%s | error=%s | input=%s",
            type(exc).__name__,
            exc,
            str(input_source)[:180],
        )

        raise

    logger.info(
        "VIDEO_FFMPEG_FINISHED | output=%s",
        output_path,
    )


# ======================================================================
# تابع اصلی
# ======================================================================

async def build_watermarked_video(
    video_url: str,
):
    """
    دانلود/دریافت ویدئو و افزودن لوگوی KhabarF24.

    پشتیبانی:
        1. فایل مستقیم MP4/WebM/MOV/M4V
        2. لینک CDN مستقیم
        3. HLS / M3U8
        4. MPEG-DASH / MPD

    Args:
        video_url:
            لینک ویدئو.

    Returns:
        مسیر فایل MP4 موقت یا None در صورت شکست.

    نکته:
        صفحات Player / HTML مستقیماً قابل پردازش نیستند.
    """

    # ==================================================================
    # بررسی اولیه
    # ==================================================================

    if not video_url:

        logger.warning(
            "VIDEO_WATERMARK_SKIP | empty video URL"
        )

        return None

    video_url = str(
        video_url
    ).strip()

    if not video_url.startswith(
        ("http://", "https://")
    ):

        logger.warning(
            "VIDEO_WATERMARK_SKIP | invalid URL | url=%s",
            video_url[:180],
        )

        return None

    # ==================================================================
    # بررسی ابزارها
    # ==================================================================

    if not _tool_exists("ffmpeg"):

        logger.error(
            "VIDEO_WATERMARK_TOOL_MISSING | ffmpeg"
        )

        return None

    if not _tool_exists("ffprobe"):

        logger.error(
            "VIDEO_WATERMARK_TOOL_MISSING | ffprobe"
        )

        return None

    # ==================================================================
    # بررسی لوگو
    # ==================================================================

    if not LOGO_PATH.is_file():

        logger.error(
            "VIDEO_WATERMARK_LOGO_MISSING | path=%s",
            LOGO_PATH,
        )

        return None

    # ==================================================================
    # تشخیص نوع ورودی
    # ==================================================================

    is_stream = _is_stream_url(
        video_url
    )

    is_direct = _is_direct_video_url(
        video_url
    )

    if is_stream:

        stream_type = (
            "HLS/M3U8"
            if video_url.lower()
            .split("?")[0]
            .endswith(".m3u8")
            else "MPEG-DASH/MPD"
        )

        logger.info(
            "VIDEO_STREAM_INPUT | "
            "type=%s | url=%s",
            stream_type,
            video_url[:180],
        )

    elif is_direct:

        logger.info(
            "VIDEO_DIRECT_INPUT | url=%s",
            video_url[:180],
        )

    else:

        logger.info(
            "VIDEO_UNKNOWN_INPUT | "
            "treating as direct media | url=%s",
            video_url[:180],
        )

    # ==================================================================
    # ساخت پوشه موقت
    # ==================================================================

    temp_dir = tempfile.mkdtemp(
        prefix="khabarf24_video_"
    )

    temp_path = Path(
        temp_dir
    )

    input_path = (
        temp_path
        / "input_video"
    )

    logo_path = (
        temp_path
        / "logo.png"
    )

    output_path = (
        temp_path
        / "khabarf24_watermarked.mp4"
    )

    logger.info(
        "VIDEO_WATERMARK_WORKDIR | path=%s",
        temp_dir,
    )

    try:

        # ==============================================================
        # مرحله ۱:
        # دریافت ویدئو
        # ==============================================================

        input_source: str | Path

        if is_stream:

            # ----------------------------------------------------------
            # M3U8 / MPD مستقیماً توسط FFmpeg خوانده می‌شود.
            # ----------------------------------------------------------

            input_source = video_url

            logger.info(
                "VIDEO_INPUT_MODE | stream_direct_to_ffmpeg"
            )

        else:

            # ----------------------------------------------------------
            # فایل مستقیم ابتدا دانلود می‌شود.
            # ----------------------------------------------------------

            connector = aiohttp.TCPConnector(
                ssl=False,
                limit=5,
            )

            timeout = aiohttp.ClientTimeout(
                total=DOWNLOAD_TIMEOUT_SECONDS,
                connect=20,
                sock_read=30,
            )

            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(compatible; KhabarF24Bot/1.0)"
                    )
                },
            ) as session:

                downloaded = await _download_video(
                    video_url,
                    input_path,
                    session,
                )

            if not downloaded:

                logger.warning(
                    "VIDEO_INPUT_REJECTED | "
                    "download failed | url=%s",
                    video_url[:180],
                )

                return None

            # ----------------------------------------------------------
            # بررسی واقعی فایل دانلودشده
            # ----------------------------------------------------------

            if not input_path.is_file():

                logger.error(
                    "VIDEO_INPUT_FILE_MISSING | path=%s",
                    input_path,
                )

                return None

            input_size = input_path.stat().st_size

            if input_size <= 0:

                logger.error(
                    "VIDEO_INPUT_FILE_EMPTY | path=%s",
                    input_path,
                )

                return None

            logger.info(
                "VIDEO_INPUT_READY | "
                "size=%s | path=%s",
                _format_bytes(input_size),
                input_path,
            )

            input_source = input_path

        # ==============================================================
        # مرحله ۲:
        # بررسی مدت و ابعاد
        # ==============================================================

        video_info = await _get_video_info(
            input_source
        )

        logger.info(
            "VIDEO_INFO | "
            "width=%s | height=%s | duration=%.1fs",
            video_info["width"],
            video_info["height"],
            video_info["duration"],
        )

        # --------------------------------------------------------------
        # محدودیت مدت
        # --------------------------------------------------------------

        if (
            video_info["duration"]
            > MAX_DURATION_SECONDS
        ):

            logger.warning(
                "VIDEO_DURATION_TOO_LONG | "
                "duration=%.1fs | limit=%ss | url=%s",
                video_info["duration"],
                MAX_DURATION_SECONDS,
                video_url[:180],
            )

            return None

        # ==============================================================
        # مرحله ۳:
        # آماده‌سازی لوگو
        # ==============================================================

        _prepare_logo(
            LOGO_PATH,
            logo_path,
            video_info["width"],
        )

        if not logo_path.is_file():

            raise RuntimeError(
                "Prepared logo file was not created."
            )

        logo_size = logo_path.stat().st_size

        if logo_size <= 0:

            raise RuntimeError(
                "Prepared logo file is empty."
            )

        logger.info(
            "VIDEO_LOGO_FILE_READY | size=%s",
            _format_bytes(logo_size),
        )

        # ==============================================================
        # مرحله ۴:
        # افزودن واترمارک
        # ==============================================================

        await _encode_watermarked_video(
            input_source,
            logo_path,
            output_path,
        )

        # ==============================================================
        # مرحله ۵:
        # بررسی خروجی
        # ==============================================================

        if not output_path.is_file():

            raise RuntimeError(
                "FFmpeg did not create "
                "the output video."
            )

        output_size = (
            output_path.stat().st_size
        )

        if output_size <= 0:

            raise RuntimeError(
                "Output video is empty."
            )

        logger.info(
            "VIDEO_OUTPUT_CREATED | "
            "size=%s | path=%s",
            _format_bytes(output_size),
            output_path,
        )

        # --------------------------------------------------------------
        # سقف حجم تلگرام
        # --------------------------------------------------------------

        if (
            output_size
            > MAX_OUTPUT_BYTES
        ):

            logger.warning(
                "VIDEO_OUTPUT_TOO_LARGE | "
                "size=%s | limit=%s | url=%s",
                _format_bytes(output_size),
                _format_bytes(
                    MAX_OUTPUT_BYTES
                ),
                video_url[:180],
            )

            return None

        # ==============================================================
        # مرحله ۶:
        # بررسی نهایی خروجی با ffprobe
        # ==============================================================

        output_info = await _get_video_info(
            output_path
        )

        logger.info(
            "VIDEO_OUTPUT_VALIDATED | "
            "width=%s | height=%s | "
            "duration=%.1fs | size=%s",
            output_info["width"],
            output_info["height"],
            output_info["duration"],
            _format_bytes(output_size),
        )

        # --------------------------------------------------------------
        # اطمینان از اینکه خروجی واقعاً ویدئو است
        # --------------------------------------------------------------

        if (
            output_info["width"] <= 0
            or output_info["height"] <= 0
            or output_info["duration"] <= 0
        ):

            raise RuntimeError(
                "Watermarked output failed final validation."
            )

        # ==============================================================
        # موفقیت
        # ==============================================================

        logger.info(
            "VIDEO_WATERMARK_SUCCESS | "
            "type=%s | %sx%s | %.1f sec | %.2f MB | "
            "logo=%s",
            (
                "stream"
                if is_stream
                else "direct"
            ),
            output_info["width"],
            output_info["height"],
            output_info["duration"],
            output_size
            / (1024 * 1024),
            LOGO_PATH.name,
        )

        # --------------------------------------------------------------
        # مسیر فایل را برمی‌گردانیم.
        #
        # Publisher بعد از ارسال آن را با
        # cleanup_watermarked_video()
        # پاک می‌کند.
        # --------------------------------------------------------------

        return str(output_path)

    except Exception as exc:

        logger.exception(
            "VIDEO_WATERMARK_FAILED | "
            "type=%s | error=%s | url=%s",
            type(exc).__name__,
            exc,
            video_url[:180],
        )

        # --------------------------------------------------------------
        # اگر هر مرحله شکست خورد، فایل موقت نباید باقی بماند.
        # --------------------------------------------------------------

        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )

        return None


# ======================================================================
# پاک‌سازی
# ======================================================================

def cleanup_watermarked_video(
    video_path: str,
) -> None:
    """
    پاک‌سازی فایل و پوشه موقت پس از ارسال ویدئو.

    فقط فایل‌هایی که توسط همین تابع ساخته شده‌اند
    اجازه حذف دارند.
    """

    if not video_path:
        return

    try:

        path = Path(
            video_path
        ).resolve()

        parent = path.parent

        # --------------------------------------------------------------
        # فقط پوشه‌هایی که همین تابع ساخته است
        # اجازه حذف دارند.
        # --------------------------------------------------------------

        if (
            path.name
            == "khabarf24_watermarked.mp4"
            and parent.name.startswith(
                "khabarf24_video_"
            )
        ):

            shutil.rmtree(
                parent,
                ignore_errors=True,
            )

            logger.debug(
                "Temporary video cleaned: %s",
                parent,
            )

        else:

            logger.warning(
                "VIDEO_CLEANUP_SKIPPED | "
                "unsafe path=%s",
                path,
            )

    except (
        OSError,
        ValueError,
    ):

        logger.exception(
            "Could not clean up "
            "temporary video files."
        )
