import math
import struct
import wave
from pathlib import Path
import pytest

from backend.app.core.errors import NoAudioError
from backend.app.media.probe import probe_media
from backend.app.media.ffmpeg import extract_normalized_audio


def create_synthetic_wav(path: Path, duration_sec: float = 1.0, sample_rate: int = 44100):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)  # Stereo 44.1kHz
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        # Generate 440Hz sine wave
        num_frames = int(duration_sec * sample_rate)
        data = []
        for i in range(num_frames):
            val = int(32767 * 0.5 * math.sin(2 * math.pi * 440 * i / sample_rate))
            data.append(struct.pack("<hh", val, val))
        wf.writeframes(b"".join(data))


def test_probe_and_extract_audio(tmp_path):
    src_wav = tmp_path / "source_44k_stereo.wav"
    create_synthetic_wav(src_wav, duration_sec=1.5, sample_rate=44100)

    # 1. Probe
    probe = probe_media(src_wav)
    assert probe.has_audio is True
    assert probe.duration_seconds is not None
    assert 1.4 <= probe.duration_seconds <= 1.6

    # 2. Extract & Normalize to 16 kHz Mono
    norm_wav = tmp_path / "normalized_16k_mono.wav"
    result_path = extract_normalized_audio(src_wav, norm_wav, sample_rate=16000, channels=1)

    assert result_path.exists()
    assert result_path.stat().st_size > 0

    # Verify extracted WAV header parameters
    with wave.open(str(result_path), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 16000
        assert wf.getsampwidth() == 2


def test_no_audio_error_handling(tmp_path):
    # Dummy non-audio file
    fake_video = tmp_path / "silent.mp4"
    fake_video.write_bytes(b"\x00" * 2048)

    norm_wav = tmp_path / "out.wav"
    with pytest.raises(Exception) as excinfo:
        extract_normalized_audio(fake_video, norm_wav)
    # Must raise NoAudioError or AudioProcessingFailedError
    assert excinfo.value.code in ("NO_AUDIO", "AUDIO_PROCESSING_FAILED")
