"""
KhabarF24 Video Watermark
افزودن لوگوی KhabarF24 به ویدئو بدون تغییر ابعاد ویدئوی اصلی.

پشتیبانی:
- ویدئوی مستقیم MP4 / WebM / MOV / M4V
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
import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
from PIL import Image

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parents[2]

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "khabarf24_header_transparent_final.png"
)


# ---------------------------------------------------------------------
# محدودیت‌ها
# ---------------------------------------------------------------------

# حداکثر حجم دانلود فایل ویدئویی مستقیم
MAX_DOWNLOAD_BYTES = 150 * 1024 * 1024

# حداکثر حجم خروجی برای ارسال به تلگرام
MAX_OUTPUT_BYTES = 49 * 1024 * 1024

# حداکثر مدت ویدئو
MAX_DURATION_SECONDS = 180

# timeout دانلود فایل مستقیم
DOWNLOAD_TIMEOUT_SECONDS = 90

# timeout پردازش FFmpeg
PROCESS_TIMEOUT_SECONDS = 240

# ---------------------------------------------------------------------
# تنظیمات ویدئو
# ---------------------------------------------------------------------

# عرض لوگو نسبت به عرض ویدئو
LOGO_WIDTH_RATIO = 0.24

# کیفیت خروجی
VIDEO_CRF = "23"

# سرعت پردازش
VIDEO_PRESET = "veryfast"

# پسوندهای ویدئوی مستقیم
DIRECT_VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
    ".avi",
    ".mkv",
)

# فرمت‌های استریم
STREAM_EXTENSIONS = (
    ".m3u8",
    ".mpd",
)


# ---------------------------------------------------------------------
# ابزارهای کمکی
# ---------------------------------------------------------------------

def _tool_exists(name: str) -> bool:
    """بررسی نصب بودن ابزار سیستمی."""
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
    """تشخیص تقریبی لینک ویدئوی مستقیم."""
    if not url:
        return False

    try:
        parsed = urlparse(url)
        path = (parsed.path or "").lower()

        return path.endswith(DIRECT_VIDEO_EXTENSIONS)

    except Exception:
        return False


async def _run_command(
    *args: str,
    timeout: int = PROCESS_TIMEOUT_SECONDS,
):
    """اجرای دستور سیستمی به‌صورت غیرهم‌زمان."""

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
        process.kill()
        await process.communicate()

        raise RuntimeError(
            f"Command timed out: {args[0]}"
        )

    if process.returncode != 0:
        error_text = stderr.decode(
            "utf-8",
            errors="replace",
        )[-4000:]

        raise RuntimeError(
            f"Command failed ({process.returncode}): "
            f"{args[0]}\n{error_text}"
        )

    return stdout, stderr


# ---------------------------------------------------------------------
# دانلود ویدئوی مستقیم
# ---------------------------------------------------------------------

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
            "Video URL is missing or invalid."
        )
        return False

    try:
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

            if response.status != 200:
                logger.warning(
                    "Video download failed: HTTP %s",
                    response.status,
                )
                return False

            content_type = (
                response.headers.get("Content-Type")
                or ""
            ).lower()

            # صفحه HTML، عکس یا متن قطعاً ویدئوی مستقیم نیست.
            if (
                content_type.startswith("image/")
                or content_type.startswith("text/")
                or "html" in content_type
            ):
                logger.warning(
                    "URL is not a direct video "
                    "(Content-Type=%s): %s",
                    content_type,
                    url[:180],
                )
                return False

            # اگر پاسخ M3U8 یا MPD بود، این تابع نباید آن را
            # مثل فایل ویدئویی دانلود کند.
            if (
                "mpegurl" in content_type
                or "m3u8" in content_type
                or "dash+xml" in content_type
            ):
                logger.warning(
                    "Streaming manifest detected during direct download: %s",
                    url[:180],
                )
                return False

            content_length = response.headers.get(
                "Content-Length"
            )

            if content_length:
                try:
                    if (
                        int(content_length)
                        > MAX_DOWNLOAD_BYTES
                    ):
                        logger.warning(
                            "Video exceeds download size limit."
                        )
                        return False

                except ValueError:
                    pass

            downloaded = 0

            with destination.open("wb") as output:

                async for chunk in response.content.iter_chunked(
                    64 * 1024
                ):
                    downloaded += len(chunk)

                    if downloaded > MAX_DOWNLOAD_BYTES:
                        logger.warning(
                            "Video exceeded download size limit."
                        )
                        return False

                    output.write(chunk)

        if downloaded == 0:
            logger.warning(
                "Downloaded video is empty."
            )
            return False

        logger.info(
            "Direct video downloaded: %.1f MB",
            downloaded / (1024 * 1024),
        )

        return True

    except (
        aiohttp.ClientError,
        asyncio.TimeoutError,
        OSError,
    ) as exc:

        logger.warning(
            "Video download error: %s",
            exc,
        )

        return False


# ---------------------------------------------------------------------
# اطلاعات ویدئو
# ---------------------------------------------------------------------

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

    stdout, _ = await _run_command(
        *command,
        timeout=60,
    )

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
    ):

        raise RuntimeError(
            "Could not read video dimensions or duration."
        )

    if width <= 0 or height <= 0:
        raise RuntimeError(
            "Invalid video dimensions."
        )

    if duration <= 0:
        raise RuntimeError(
            "Invalid video duration."
        )

    return {
        "width": width,
        "height": height,
        "duration": duration,
    }


# ---------------------------------------------------------------------
# لوگو
# ---------------------------------------------------------------------

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

    with Image.open(source_logo) as image:

        logo = image.convert("RGBA")

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

    return destination


# ---------------------------------------------------------------------
# پردازش ویدئو
# ---------------------------------------------------------------------

async def _encode_watermarked_video(
    input_source: str | Path,
    logo_path: Path,
    output_path: Path,
) -> None:
    """
    اجرای FFmpeg و افزودن لوگو.

    input_source می‌تواند فایل محلی یا URL مستقیم/استریم باشد.
    """

    filter_graph = (
        "[1:v]format=rgba[logo];"
        "[0:v][logo]overlay="
        "x=main_w*0.04:"
        "y=main_h-overlay_h-main_h*0.04:"
        "format=auto[v]"
    )

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
    ]

    # اگر ورودی استریم است، مستقیماً از URL خوانده می‌شود.
    if isinstance(input_source, str) and input_source.startswith(
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

    command.extend(
        [
            "-i",
            str(input_source),

            "-i",
            str(logo_path),

            "-filter_complex",
            filter_graph,

            "-map",
            "[v]",

            "-map",
            "0:a?",

            "-c:v",
            "libx264",

            "-preset",
            VIDEO_PRESET,

            "-crf",
            VIDEO_CRF,

            "-pix_fmt",
            "yuv420p",

            "-c:a",
            "aac",

            "-b:a",
            "192k",

            "-movflags",
            "+faststart",

            "-max_muxing_queue_size",
            "2048",

            str(output_path),
        ]
    )

    # برای M3U8 / MPD لازم است FFmpeg بتواند پروتکل‌های
    # HTTP/HTTPS و streamهای مربوطه را بخواند.
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

    await _run_command(
        *command,
        timeout=PROCESS_TIMEOUT_SECONDS,
    )


# ---------------------------------------------------------------------
# تابع اصلی
# ---------------------------------------------------------------------

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
        در این حالت publisher باید به عکس یا متن fallback کند.
    """

    if not video_url:
        logger.warning(
            "VIDEO_WATERMARK_SKIP | empty video URL"
        )
        return None

    if not _tool_exists("ffmpeg"):
        logger.error(
            "ffmpeg is not installed."
        )
        return None

    if not _tool_exists("ffprobe"):
        logger.error(
            "ffprobe is not installed."
        )
        return None

    if not LOGO_PATH.is_file():
        logger.error(
            "KhabarF24 logo not found: %s",
            LOGO_PATH,
        )
        return None

    # ---------------------------------------------------------------
    # تشخیص نوع ورودی
    # ---------------------------------------------------------------

    is_stream = _is_stream_url(video_url)

    is_direct = _is_direct_video_url(video_url)

    if is_stream:
        logger.info(
            "VIDEO_STREAM_INPUT | type=%s | url=%s",
            (
                "HLS/M3U8"
                if video_url.lower().split("?")[0].endswith(
                    ".m3u8"
                )
                else "MPEG-DASH/MPD"
            ),
            video_url[:180],
        )

    elif is_direct:
        logger.info(
            "VIDEO_DIRECT_INPUT | url=%s",
            video_url[:180],
        )

    else:
        logger.info(
            "VIDEO_UNKNOWN_INPUT | url=%s",
            video_url[:180],
        )

    temp_dir = tempfile.mkdtemp(
        prefix="khabarf24_video_"
    )

    temp_path = Path(temp_dir)

    input_path = temp_path / "input_video"
    logo_path = temp_path / "logo.png"
    output_path = (
        temp_path
        / "khabarf24_watermarked.mp4"
    )

    try:

        # -----------------------------------------------------------
        # مرحله ۱:
        # اگر Stream باشد، مستقیم به FFmpeg داده می‌شود.
        # اگر فایل مستقیم باشد، ابتدا دانلود می‌شود.
        # -----------------------------------------------------------

        input_source: str | Path

        if is_stream:

            # M3U8 / MPD مستقیماً توسط FFmpeg خوانده می‌شود.
            input_source = video_url

        else:

            connector = aiohttp.TCPConnector(
                ssl=False,
                limit=5,
            )

            timeout = aiohttp.ClientTimeout(
                total=DOWNLOAD_TIMEOUT_SECONDS
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
                    "VIDEO_INPUT_REJECTED | url=%s",
                    video_url[:180],
                )

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True,
                )

                return None

            input_source = input_path

        # -----------------------------------------------------------
        # مرحله ۲:
        # بررسی مدت و ابعاد
        # -----------------------------------------------------------

        video_info = await _get_video_info(
            input_source
        )

        logger.info(
            "VIDEO_INFO | width=%s | height=%s | "
            "duration=%.1fs",
            video_info["width"],
            video_info["height"],
            video_info["duration"],
        )

        if (
            video_info["duration"]
            > MAX_DURATION_SECONDS
        ):

            logger.warning(
                "Video duration %.1f seconds exceeds "
                "limit (%s seconds).",
                video_info["duration"],
                MAX_DURATION_SECONDS,
            )

            shutil.rmtree(
                temp_dir,
                ignore_errors=True,
            )

            return None

        # -----------------------------------------------------------
        # مرحله ۳:
        # آماده‌سازی لوگو
        # -----------------------------------------------------------

        _prepare_logo(
            LOGO_PATH,
            logo_path,
            video_info["width"],
        )

        # -----------------------------------------------------------
        # مرحله ۴:
        # افزودن واترمارک
        # -----------------------------------------------------------

        await _encode_watermarked_video(
            input_source,
            logo_path,
            output_path,
        )

        # -----------------------------------------------------------
        # مرحله ۵:
        # بررسی خروجی
        # -----------------------------------------------------------

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

        # -----------------------------------------------------------
        # بررسی سقف حجم تلگرام
        # -----------------------------------------------------------

        if output_size > MAX_OUTPUT_BYTES:

            logger.warning(
                "Watermarked video exceeds "
                "output size limit: %.1f MB",
                output_size
                / (1024 * 1024),
            )

            shutil.rmtree(
                temp_dir,
                ignore_errors=True,
            )

            return None

        logger.info(
            "VIDEO_WATERMARK_SUCCESS | "
            "type=%s | %sx%s | %.1f sec | %.1f MB",
            (
                "stream"
                if is_stream
                else "direct"
            ),
            video_info["width"],
            video_info["height"],
            video_info["duration"],
            output_size
            / (1024 * 1024),
        )

        # مسیر فایل را برمی‌گردانیم.
        return str(output_path)

    except Exception:

        logger.exception(
            "VIDEO_WATERMARK_FAILED | url=%s",
            video_url[:180],
        )

        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )

        return None


# ---------------------------------------------------------------------
# پاک‌سازی
# ---------------------------------------------------------------------

def cleanup_watermarked_video(
    video_path: str,
) -> None:
    """
    پاک‌سازی فایل و پوشه موقت پس از ارسال ویدئو.
    """

    if not video_path:
        return

    try:

        path = Path(
            video_path
        ).resolve()

        parent = path.parent

        # فقط پوشه‌هایی که همین تابع ساخته است
        # اجازه حذف دارند.
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

    except (
        OSError,
        ValueError,
    ):

        logger.exception(
            "Could not clean up "
            "temporary video files."
        )
