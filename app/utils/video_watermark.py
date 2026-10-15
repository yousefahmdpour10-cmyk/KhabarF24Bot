"""
Video Watermark Utility - KhabarF24

دانلود ویدئوی مستقیم و قراردادن هدر PNG روی گوشه پایین‌چپ.
نیازمند FFmpeg و FFprobe است.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional

import aiohttp

from app.utils.logger import logger

LOGO_PATH = Path("assets/khabarf24_header_transparent_final.png")

DOWNLOAD_TIMEOUT = 90
MAX_VIDEO_BYTES = 150 * 1024 * 1024
MAX_VIDEO_SECONDS = 180


async def _download_video(url: str, destination: str) -> bool:
    timeout = aiohttp.ClientTimeout(
        total=DOWNLOAD_TIMEOUT,
        connect=15,
        sock_read=30,
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
                        f"Video watermark: download HTTP {response.status}"
                    )
                    return False

                content_type = response.headers.get(
                    "Content-Type", ""
                ).lower()

                if (
                    content_type
                    and not (
                        content_type.startswith("video/")
                        or "octet-stream" in content_type
                        or "application/mp4" in content_type
                    )
                ):
                    logger.warning(
                        "Video watermark: URL did not return a video "
                        f"(Content-Type={content_type})"
                    )
                    return False

                length = response.headers.get("Content-Length")
                if length and int(length) > MAX_VIDEO_BYTES:
                    logger.warning("Video watermark: file exceeds size limit")
                    return False

                size = 0
                with open(destination, "wb") as output:
                    async for chunk in response.content.iter_chunked(64 * 1024):
                        size += len(chunk)
                        if size > MAX_VIDEO_BYTES:
                            logger.warning(
                                "Video watermark: download exceeded size limit"
                            )
                            return False
                        output.write(chunk)

                return size > 0

    except Exception as exc:
        logger.warning(f"Video watermark: download failed: {exc}")
        return False


async def _run_ffmpeg(args: list[str]) -> bool:
    try:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=DOWNLOAD_TIMEOUT,
        )

        if process.returncode != 0:
            logger.warning(
                "Video watermark: FFmpeg failed: "
                + stderr.decode("utf-8", errors="replace")[-1200:]
            )
            return False

        return True

    except Exception as exc:
        logger.warning(f"Video watermark: FFmpeg error: {exc}")
        return False


async def build_watermarked_video(url: str) -> Optional[bytes]:
    """
    برای یک URL مستقیم ویدئو، بایت‌های MP4 واترمارک‌دار برمی‌گرداند.
    در صورت شکست، None برمی‌گرداند تا ناشر عکس یا متن را امتحان کند.
    """

    if not url or not LOGO_PATH.is_file():
        if not LOGO_PATH.is_file():
            logger.warning(f"Video watermark: logo missing: {LOGO_PATH}")
        return None

    with tempfile.TemporaryDirectory(prefix="khabarf24_video_") as temp_dir:
        input_path = os.path.join(temp_dir, "input_video")
        output_path = os.path.join(temp_dir, "output.mp4")

        downloaded = await _download_video(url, input_path)
        if not downloaded:
            return None

        probe = await asyncio.create_subprocess_exec(
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, _ = await asyncio.wait_for(
                probe.communicate(), timeout=20
            )
            duration = float(stdout.decode().strip())
        except Exception as exc:
            logger.warning(f"Video watermark: ffprobe failed: {exc}")
            return None

        if duration <= 0 or duration > MAX_VIDEO_SECONDS:
            logger.warning(
                f"Video watermark: unsupported duration {duration}"
            )
            return None

        logo = str(LOGO_PATH.resolve())

        # لوگو با عرض ۲۴ درصد و حاشیه ۴ درصد روی ویدئو قرار می‌گیرد.
        filter_graph = (
            "[1:v]scale=iw*min(1\\,0.24*W/iw):-1[logo];"
            "[0:v][logo]overlay="
            "x=W*0.04:y=H-h-H*0.04:"
            "format=auto[v]"
        )

        args = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-y",
            "-i", input_path,
            "-i", logo,
            "-filter_complex", filter_graph,
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            "-t", str(MAX_VIDEO_SECONDS),
            output_path,
        ]

        success = await _run_ffmpeg(args)
        if not success or not os.path.isfile(output_path):
            return None

        try:
            if os.path.getsize(output_path) > MAX_VIDEO_BYTES:
                logger.warning(
                    "Video watermark: processed video exceeds size limit"
                )
                return None

            with open(output_path, "rb") as file:
                return file.read()
        except Exception as exc:
            logger.warning(f"Video watermark: output read failed: {exc}")
            return None
