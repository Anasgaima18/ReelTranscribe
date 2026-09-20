"""
Industry-standard yt-dlp media provider for Reels, Shorts, TikTok, and Direct media.
"""
import asyncio
from pathlib import Path
from typing import Optional, Set
import yt_dlp

from backend.app.config import settings
from backend.app.core.errors import (
    MediaNotFoundError,
    MediaPrivateError,
    MediaDownloadFailedError,
    MediaTooLargeError,
    MediaTooLongError
)
from backend.app.media.providers.base import BaseMediaProvider, MediaInfo


class YtDlpProvider(BaseMediaProvider):
    def __init__(self, name: str, supported_domains: Optional[Set[str]] = None):
        self.name = name
        self.supported_domains = supported_domains or set()

    def can_handle(self, url: str) -> bool:
        if not self.supported_domains:
            # Fallback direct/generic provider
            return True
        url_lower = url.lower()
        return any(domain in url_lower for domain in self.supported_domains)

    def _get_ydl_opts(self, target_dir: Optional[Path] = None) -> dict:
        opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "socket_timeout": 15,
            # Prefer mp4/m4a/webm best quality
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }
        if target_dir:
            opts["outtmpl"] = str(target_dir / "%(id)s.%(ext)s")
        if settings.MAX_FILE_SIZE_MB:
            opts["max_filesize"] = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        return opts

    def _sync_extract_info(self, url: str, download: bool = False, target_dir: Optional[Path] = None) -> dict:
        opts = self._get_ydl_opts(target_dir=target_dir)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=download)
                return info
        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e).lower()
            if "private" in err_msg or "login required" in err_msg:
                raise MediaPrivateError(f"Media is private or requires login: {str(e)}")
            elif "not found" in err_msg or "404" in err_msg or "does not exist" in err_msg:
                raise MediaNotFoundError(f"Media could not be found: {str(e)}")
            elif "filesize" in err_msg or "too large" in err_msg:
                raise MediaTooLargeError(f"Media exceeds maximum allowed size: {str(e)}")
            else:
                raise MediaDownloadFailedError(f"Failed to download media: {str(e)}")
        except Exception as e:
            raise MediaDownloadFailedError(f"Unexpected error extracting media: {str(e)}")

    async def extract_info(self, url: str) -> MediaInfo:
        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(None, self._sync_extract_info, url, False, None)

        duration = info.get("duration")
        if duration and duration > settings.MAX_DURATION_SECONDS:
            raise MediaTooLongError(
                f"Video duration ({duration}s) exceeds maximum allowed ({settings.MAX_DURATION_SECONDS}s)."
            )

        return MediaInfo(
            source_url=url,
            provider_name=self.name,
            title=info.get("title", "Untitled"),
            duration_seconds=duration,
            has_audio=info.get("acodec") != "none",
            metadata={"uploader": info.get("uploader"), "view_count": info.get("view_count")}
        )

    async def download(self, url: str, target_dir: Path) -> MediaInfo:
        target_dir.mkdir(parents=True, exist_ok=True)
        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(None, self._sync_extract_info, url, True, target_dir)

        duration = info.get("duration")
        if duration and duration > settings.MAX_DURATION_SECONDS:
            raise MediaTooLongError(
                f"Video duration ({duration}s) exceeds maximum allowed ({settings.MAX_DURATION_SECONDS}s)."
            )

        # Find downloaded file
        downloaded_file = None
        if "_filename" in info and Path(info["_filename"]).is_file():
            downloaded_file = Path(info["_filename"])
        else:
            # Fallback search in target_dir
            for f in target_dir.iterdir():
                if f.is_file():
                    downloaded_file = f
                    break

        return MediaInfo(
            source_url=url,
            provider_name=self.name,
            title=info.get("title", "Untitled"),
            duration_seconds=duration,
            file_path=downloaded_file,
            has_audio=info.get("acodec") != "none",
            metadata={"format": info.get("ext")}
        )


class InstagramProvider(YtDlpProvider):
    def __init__(self):
        super().__init__(name="instagram", supported_domains={"instagram.com", "instagr.am"})


class YouTubeProvider(YtDlpProvider):
    def __init__(self):
        super().__init__(name="youtube", supported_domains={"youtube.com", "youtu.be"})


class TikTokProvider(YtDlpProvider):
    def __init__(self):
        super().__init__(name="tiktok", supported_domains={"tiktok.com"})


class DirectMediaProvider(YtDlpProvider):
    def __init__(self):
        super().__init__(name="direct", supported_domains=set())
