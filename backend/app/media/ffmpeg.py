"""
FFmpeg Audio and Video extraction and normalization pipeline.
"""
import subprocess
from pathlib import Path
from backend.app.core.errors import NoAudioError, AudioProcessingFailedError
from backend.app.media.probe import get_ffmpeg_binary, probe_media


def extract_normalized_audio(
    input_file: Path,
    output_wav_file: Path,
    sample_rate: int = 16000,
    channels: int = 1
) -> Path:
    """
    Validates audio stream existence and extracts 16 kHz mono PCM WAV.
    """
    probe = probe_media(input_file)
    if not probe.has_audio:
        raise NoAudioError("Input media contains no audio stream to transcribe.")

    output_wav_file.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_binary()

    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(input_file),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(sample_rate),
        "-ac", str(channels),
        str(output_wav_file)
    ]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        if proc.returncode != 0:
            raise AudioProcessingFailedError(f"FFmpeg audio extraction failed: {proc.stderr}")
    except Exception as e:
        if isinstance(e, AudioProcessingFailedError):
            raise
        raise AudioProcessingFailedError(f"Error running FFmpeg extraction: {str(e)}")

    if not output_wav_file.exists() or output_wav_file.stat().st_size == 0:
        raise AudioProcessingFailedError("Extracted audio file is missing or empty.")

    return output_wav_file


def sample_video_frames(
    video_file: Path,
    output_dir: Path,
    fps: float = 1.0,
    max_frames: int = 60
) -> list[Path]:
    """
    Samples video frames at specified fps for burned-in caption OCR analysis.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_bin = get_ffmpeg_binary()

    out_pattern = output_dir / "frame_%04d.jpg"
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(video_file),
        "-vf", f"fps={fps}",
        "-vframes", str(max_frames),
        "-q:v", "2",
        str(out_pattern)
    ]

    try:
        subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
    except Exception as e:
        raise AudioProcessingFailedError(f"Error sampling video frames: {str(e)}")

    frames = sorted(list(output_dir.glob("frame_*.jpg")))
    return frames
