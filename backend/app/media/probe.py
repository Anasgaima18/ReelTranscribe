"""
Media Container and Stream Inspector.
"""
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import imageio_ffmpeg

from backend.app.core.errors import NoAudioError, AudioProcessingFailedError


@dataclass
class StreamInfo:
    index: int
    stream_type: str  # "video", "audio", "subtitle"
    codec: str
    language: Optional[str] = None


@dataclass
class ContainerProbeResult:
    duration_seconds: Optional[float]
    streams: List[StreamInfo]
    has_audio: bool
    has_video: bool
    has_embedded_subtitles: bool


MediaProbeResult = ContainerProbeResult


def get_ffmpeg_binary() -> str:
    # 1. System PATH
    sys_path = shutil.which("ffmpeg")
    if sys_path:
        return sys_path
    # 2. imageio-ffmpeg bundled binary
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def probe_media(file_path: Path) -> ContainerProbeResult:
    """
    Inspects media container streams and duration using ffmpeg -i.
    """
    if not file_path.exists():
        raise AudioProcessingFailedError(f"File not found for probing: {file_path}")

    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [ffmpeg_bin, "-i", str(file_path)]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        output = proc.stderr  # FFmpeg outputs metadata to stderr
    except Exception as e:
        raise AudioProcessingFailedError(f"Failed executing media probe: {str(e)}")

    duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", output)
    duration_seconds = None
    if duration_match:
        hours = float(duration_match.group(1))
        minutes = float(duration_match.group(2))
        seconds = float(duration_match.group(3))
        duration_seconds = hours * 3600 + minutes * 60 + seconds

    streams: List[StreamInfo] = []
    has_audio = False
    has_video = False
    has_subtitles = False

    # Example stream line:
    # Stream #0:0(und): Video: h264 ...
    # Stream #0:1(eng): Audio: aac ...
    # Stream #0:2(eng): Subtitle: subrip ...
    stream_pattern = re.compile(
        r"Stream\s+#0:(\d+)(?:\(([a-zA-Z0-9_-]+)\))?:\s*(Video|Audio|Subtitle):\s*([a-zA-Z0-9_-]+)",
        re.IGNORECASE
    )

    for line in output.splitlines():
        match = stream_pattern.search(line)
        if match:
            idx = int(match.group(1))
            lang = match.group(2)
            stype = match.group(3).lower()
            codec = match.group(4).lower()

            if stype == "audio":
                has_audio = True
            elif stype == "video":
                has_video = True
            elif stype == "subtitle":
                has_subtitles = True

            streams.append(StreamInfo(index=idx, stream_type=stype, codec=codec, language=lang))

    return ContainerProbeResult(
        duration_seconds=duration_seconds,
        streams=streams,
        has_audio=has_audio,
        has_video=has_video,
        has_embedded_subtitles=has_subtitles
    )
