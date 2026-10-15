"""
Video Watermark Utility - KhabarF24

درج هدر شفاف کانال روی ویدئو با حفظ وضوح اصلی و صدا.
ویدئو کوچک یا بریده نمی‌شود.
نیازمند FFmpeg و FFprobe است.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional

import aiohttp
from PIL import Image

from app.utils.logger import logger

LOGO_PATH = Path("assets/khabarf24_header_transparent_final.png")

DOWNLOAD_TIMEOUT = 120
MAX_VIDEO_BYTES = 150 * 1024 * 1024
MAX_VIDEO_SECONDS = 180

# اندازه هدر نسبت به عرض ویدئو
LOGO_WIDTH_RATIO = 0.24

# کیفیت رمزگذاری؛ عدد کمتر یعنی کیفیت بالاتر
VIDEO_CRF = "18"
VIDEO_PRESET = "medium"


async def _download_video(url: str, destination: str) -> bool:
    timeout = aiohttp.ClientTimeout(
        total=DOWNLOAD_TIMEOUT,
        connect=20,
        sock_read=40,
    )

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                url,
                allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 KhabarF24Bot"},
            ) as response:

                if response.status != 200:
                    logger.warning(
                        f"Video watermark: HTTP {response.status}"
                    )
                    return False

                content_type = response.headers.get(
                    "Content-Type", ""
                ).lower()

                if content_type and not (
                    content_type.startswith("video/")
                    or "octet-stream" in content_type
                    or "application/mp4" in content_type
                ):
                    logger.warning(
                        "Video watermark: URL did not return a direct "
                        f"video file ({content_type})"
                    )
                    return False

                content_length = response.headers.get("Content-Length")
                if content_length:
                    try:
                        if int(content_length) > MAX_VIDEO_BYTES:
                            logger.warning(
                                "Video watermark: video exceeds size limit"
                            )
                            return False
                    except ValueError:
                        pass

                size = 0

                with open(destination, "wb") as output:
                    async for chunk in response.content.iter_chunked(
                        64 * 1024
                    ):
                        size += len(chunk)

                        if size > MAX_VIDEO_BYTES:
                            logger.warning(
                                "Video watermark: download exceeded size limit"
                            )
                            return False

                        output.write(chunk)

                return size > 0

    except Exception as exc:
        logger.warning(
            f"Video watermark: download failed: {exc}"
        )
        return False


async def _run_command(args: list[str], timeout: int = 120):
    """اجرای دستور خارجی بدون مسدود کردن event loop."""

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
        raise

    return process.returncode, stdout, stderr


async def _get_video_info(video_path: str) -> Optional[dict]:
    """استخراج ابعاد و مدت ویدئو بدون تغییر فایل."""

    args = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration",
        "-of", "default=noprint_wrappers=1",
        video_path,
    ]

    try:
        code, stdout, stderr = await _run_command(args, timeout=20)

        if code != 0:
            logger.warning(
                "Video watermark: ffprobe failed: "
                + stderr.decode("utf-8", errors="replace")[-1000:]
            )
            return None

        values = {}

        for line in stdout.decode(
            "utf-8", errors="replace"
        ).splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()

        width = int(values.get("width", "0"))
        height = int(values.get("height", "0"))
        duration = float(values.get("duration", "0"))

        if width <= 0 or height <= 0 or duration <= 0:
            return None

        return {
            "width": width,
            "height": height,
            "duration": duration,
        }

    except Exception as exc:
        logger.warning(
            f"Video watermark: unable to inspect video: {exc}"
        )
        return None


async def _encode_video(
    input_path: str,
    output_path: str,
    logo_path: str,
    logo_width: int,
) -> bool:
    """
    درج هدر روی ویدئو.

    وضوح تصویر اصلی حفظ می‌شود؛ هیچ scale یا crop روی ویدئوی اصلی
    اعمال نمی‌شود. فقط فایل لوگو برای قرارگیری روی تصویر اندازه‌گیری
    و مقیاس‌بندی می‌شود.
    """

    filter_graph = (
        f"[1:v]scale={logo_width}:-1[logo];"
        "[0:v][logo]overlay="
        "x=main_w*0.04:"
        "y=main_h-overlay_h-main_h*0.04:"
        "format=auto[v]"
    )

    args = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", input_path,
        "-i", logo_path,
        "-filter_complex", filter_graph,
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", VIDEO_PRESET,
        "-crf", VIDEO_CRF,
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map_metadata", "0",
        "-movflags", "+faststart",
        output_path,
    ]

    try:
        code, _, stderr = await _run_command(
            args,
            timeout=DOWNLOAD_TIMEOUT,
        )

        if code != 0:
            logger.warning(
                "Video watermark: FFmpeg failed: "
                + stderr.decode("utf-8", errors="replace")[-1500:]
            )
            return False

        return os.path.isfile(output_path) and (
            os.path.getsize(output_path) > 0
        )

    except Exception as exc:
        logger.warning(
            f"Video watermark: encoding failed: {exc}"
        )
        return False


async def build_watermarked_video(url: str) -> Optional[bytes]:
    """
    دانلود ویدئوی مستقیم، افزودن هدر کانال و برگرداندن خروجی MP4.

    در صورت شکست، None برمی‌گرداند تا ناشر بتواند عکس یا متن را ارسال کند.
    """

    if not url:
        return None

    if not LOGO_PATH.is_file():
        logger.warning(
            f"Video watermark: logo file not found: {LOGO_PATH}"
        )
        return None

    with tempfile.TemporaryDirectory(
        prefix="khabarf24_video_"
    ) as temp_dir:

        input_path = os.path.join(temp_dir, "input_video")
        output_path = os.path.join(temp_dir, "output.mp4")

        if not await _download_video(url, input_path):
            return None

        video_info = await _get_video_info(input_path)

        if not video_info:
            return None

        duration = video_info["duration"]
        video_width = video_info["width"]

        # ویدئوهای طولانی‌تر از سقف پردازش نمی‌شوند؛ بریده نمی‌شوند.
        if duration > MAX_VIDEO_SECONDS:
            logger.warning(
                "Video watermark: video is longer than the supported "
                f"limit ({duration:.1f}s); original will not be trimmed"
            )
            return None

        # تنها لوگو تغییر اندازه می‌دهد؛ وضوح ویدئو دست‌نخورده می‌ماند.
        logo_width = max(
            1,
            int(video_width * LOGO_WIDTH_RATIO),
        )

        try:
            with Image.open(LOGO_PATH) as logo:
                if logo.width <= 0 or logo.height <= 0:
                    return None
        except Exception as exc:
            logger.warning(
                f"Video watermark: invalid logo file: {exc}"
            )
            return None

        success = await _encode_video(
            input_path=input_path,
            output_path=output_path,
            logo_path=str(LOGO_PATH.resolve()),
            logo_width=logo_width,
        )

        if not success:
            return None

        try:
            output_size = os.path.getsize(output_path)

            if output_size > MAX_VIDEO_BYTES:
                logger.warning(
                    "Video watermark: processed video exceeds upload "
                    "size limit; falling back to photo/text"
                )
                return None

            with open(output_path, "rb") as video_file:
                return video_file.read()

        except Exception as exc:
            logger.warning(
                f"Video watermark: cannot read output: {exc}"
            )
            return None
