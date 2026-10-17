"""
KhabarF24 Video Watermark
افزودن لوگوی KhabarF24 به ویدئو بدون تغییر ابعاد ویدئوی اصلی.

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
LOGO_PATH = BASE_DIR / "assets" / "khabarf24_header_transparent_final.png"

# محدودیت‌ها برای جلوگیری از مصرف بیش از حد حافظه و زمان GitHub Actions
MAX_DOWNLOAD_BYTES = 150 * 1024 * 1024

# ربات‌های تلگرام حداکثر ۵۰ مگابایت آپلود می‌کنند. اگر خروجی بزرگ‌تر
# باشد ارسال شکست می‌خورد و زمان چرخه بیهوده تلف شده است؛ پس سقف را
# کمی زیر ۵۰ مگابایت نگه می‌داریم.
MAX_OUTPUT_BYTES = 49 * 1024 * 1024

MAX_DURATION_SECONDS = 180
DOWNLOAD_TIMEOUT_SECONDS = 90
PROCESS_TIMEOUT_SECONDS = 240

# لوگو حدود 24 درصد عرض ویدئو خواهد بود.
LOGO_WIDTH_RATIO = 0.24

# کیفیت خروجی ویدئو؛ عدد کمتر یعنی کیفیت بالاتر و حجم بیشتر.
# CRF 23 + preset veryfast: حجم کمتر، پردازش خیلی سریع‌تر روی
# سرور گیت‌هاب، و کیفیت برای شبکه‌های اجتماعی کاملاً مناسب.
VIDEO_CRF = "23"
VIDEO_PRESET = "veryfast"


def _tool_exists(name: str) -> bool:
    """بررسی نصب بودن ابزار سیستمی."""
    return shutil.which(name) is not None


async def _run_command(*args: str, timeout: int = PROCESS_TIMEOUT_SECONDS):
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
        raise RuntimeError(f"Command timed out: {args[0]}")

    if process.returncode != 0:
        error_text = stderr.decode("utf-8", errors="replace")[-3000:]
        raise RuntimeError(
            f"Command failed ({process.returncode}): "
            f"{args[0]}\n{error_text}"
        )

    return stdout, stderr


async def _download_video(
    url: str,
    destination: Path,
    session: aiohttp.ClientSession,
) -> bool:
    """دانلود ویدئو با محدودیت حجم."""
    if not url or not url.startswith(("http://", "https://")):
        logger.warning("Video URL is missing or invalid.")
        return False

    try:
        timeout = aiohttp.ClientTimeout(
            total=DOWNLOAD_TIMEOUT_SECONDS,
            connect=20,
            sock_read=30,
        )

        async with session.get(url, timeout=timeout) as response:
            if response.status != 200:
                logger.warning(
                    "Video download failed: HTTP %s",
                    response.status,
                )
                return False

            content_length = response.headers.get("Content-Length")
            if content_length:
                try:
                    if int(content_length) > MAX_DOWNLOAD_BYTES:
                        logger.warning("Video exceeds download size limit.")
                        return False
                except ValueError:
                    pass

            downloaded = 0

            with destination.open("wb") as output:
                async for chunk in response.content.iter_chunked(64 * 1024):
                    downloaded += len(chunk)

                    if downloaded > MAX_DOWNLOAD_BYTES:
                        logger.warning("Video exceeded download size limit.")
                        return False

                    output.write(chunk)

        if downloaded == 0:
            logger.warning("Downloaded video is empty.")
            return False

        return True

    except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as exc:
        logger.warning("Video download error: %s", exc)
        return False


async def _get_video_info(video_path: Path) -> dict:
    """خواندن مدت و ابعاد ویدئو با ffprobe."""
    stdout, _ = await _run_command(
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration",
        "-of", "default=noprint_wrappers=1",
        str(video_path),
        timeout=30,
    )

    info = {}

    for line in stdout.decode("utf-8", errors="replace").splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        info[key.strip()] = value.strip()

    try:
        width = int(info.get("width", "0"))
        height = int(info.get("height", "0"))
        duration = float(info.get("duration", "0"))
    except (ValueError, TypeError):
        raise RuntimeError("Could not read video dimensions or duration.")

    if width <= 0 or height <= 0:
        raise RuntimeError("Invalid video dimensions.")

    if duration <= 0:
        raise RuntimeError("Invalid video duration.")

    return {
        "width": width,
        "height": height,
        "duration": duration,
    }


def _prepare_logo(source_logo: Path, destination: Path, video_width: int):
    """ساخت نسخه‌ای از لوگو با عرض متناسب با ویدئو."""
    if not source_logo.is_file():
        raise FileNotFoundError(f"Logo file not found: {source_logo}")

    with Image.open(source_logo) as image:
        logo = image.convert("RGBA")

        target_width = max(1, int(video_width * LOGO_WIDTH_RATIO))
        target_width = min(target_width, video_width)

        target_height = max(
            1,
            round(logo.height * target_width / logo.width),
        )

        # فقط خود لوگو تغییر اندازه می‌دهد؛ ویدئوی اصلی تغییر نمی‌کند.
        logo = logo.resize(
            (target_width, target_height),
            Image.Resampling.LANCZOS,
        )

        logo.save(destination, format="PNG", optimize=True)

    return destination


async def build_watermarked_video(video_url: str):
    """
    دانلود ویدئو و افزودن لوگو در پایین سمت چپ.

    Args:
        video_url: لینک مستقیم فایل ویدئو.

    Returns:
        مسیر فایل MP4 موقت یا None در صورت شکست.

    نکته:
        فایل خروجی داخل پوشه موقت ساخته می‌شود.
        فراخواننده باید بعد از ارسال ویدئو، پوشه موقت را پاک کند
        یا از TemporaryDirectory برای مدیریت چرخه عمر فایل استفاده کند.
    """
    if not _tool_exists("ffmpeg") or not _tool_exists("ffprobe"):
        logger.error("ffmpeg or ffprobe is not installed.")
        return None

    if not LOGO_PATH.is_file():
        logger.error("KhabarF24 logo not found: %s", LOGO_PATH)
        return None

    temp_dir = tempfile.mkdtemp(prefix="khabarf24_video_")
    temp_path = Path(temp_dir)

    input_path = temp_path / "input_video"
    logo_path = temp_path / "logo.png"
    output_path = temp_path / "khabarf24_watermarked.mp4"

    try:
        connector = aiohttp.TCPConnector(ssl=False, limit=5)
        timeout = aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT_SECONDS)

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; KhabarF24Bot/1.0)"
                )
            },
        ) as session:
            downloaded = await _download_video(
                video_url,
                input_path,
                session,
            )

        if not downloaded:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None

        video_info = await _get_video_info(input_path)

        if video_info["duration"] > MAX_DURATION_SECONDS:
            logger.warning(
                "Video duration %.1f seconds exceeds limit (%s seconds).",
                video_info["duration"],
                MAX_DURATION_SECONDS,
            )
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None

        _prepare_logo(
            LOGO_PATH,
            logo_path,
            video_info["width"],
        )

        # لوگو پایین سمت چپ قرار می‌گیرد.
        # هیچ scale یا crop روی تصویر اصلی ویدئو اعمال نمی‌شود.
        filter_graph = (
            "[1:v]format=rgba[logo];"
            "[0:v][logo]overlay="
            "x=main_w*0.04:"
            "y=main_h-overlay_h-main_h*0.04:"
            "format=auto[v]"
        )

        await _run_command(
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", str(input_path),
            "-i", str(logo_path),
            "-filter_complex", filter_graph,
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", VIDEO_PRESET,
            "-crf", VIDEO_CRF,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-max_muxing_queue_size", "2048",
            str(output_path),
        )

        if not output_path.is_file():
            raise RuntimeError("FFmpeg did not create the output video.")

        output_size = output_path.stat().st_size

        if output_size <= 0:
            raise RuntimeError("Output video is empty.")

        if output_size > MAX_OUTPUT_BYTES:
            logger.warning(
                "Watermarked video exceeds output size limit: %.1f MB",
                output_size / (1024 * 1024),
            )
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None

        logger.info(
            "Video watermark completed: %sx%s, %.1f seconds, %.1f MB",
            video_info["width"],
            video_info["height"],
            video_info["duration"],
            output_size / (1024 * 1024),
        )

        # مسیر فایل را برمی‌گردانیم؛ فایل تا زمان پاک‌سازی باقی می‌ماند.
        return str(output_path)

    except Exception:
        logger.exception("Failed to watermark video.")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None


def cleanup_watermarked_video(video_path: str) -> None:
    """پاک‌سازی فایل و پوشه موقت پس از ارسال ویدئو."""
    if not video_path:
        return

    try:
        path = Path(video_path).resolve()
        parent = path.parent

        # فقط پوشه‌های موقت متعلق به همین تابع حذف می‌شوند.
        if (
            path.name == "khabarf24_watermarked.mp4"
            and parent.name.startswith("khabarf24_video_")
        ):
            shutil.rmtree(parent, ignore_errors=True)

    except (OSError, ValueError):
        logger.exception("Could not clean up temporary video files.")
