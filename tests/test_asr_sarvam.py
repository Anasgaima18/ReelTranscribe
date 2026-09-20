from pathlib import Path
import pytest
import httpx
from backend.app.asr.sarvam import SarvamProvider
from backend.app.asr.base import TranscriptResult
from backend.app.core.errors import ASRRateLimitedError, ASRProviderUnavailableError

@pytest.mark.asyncio
async def test_sarvam_provider_availability():
    p_no_key = SarvamProvider(api_key="")
    assert p_no_key.is_available() is False

    p_with_key = SarvamProvider(api_key="valid-test-key")
    assert p_with_key.is_available() is True

@pytest.mark.asyncio
async def test_sarvam_transcribe_mock(monkeypatch, tmp_path):
    dummy_wav = tmp_path / "test.wav"
    dummy_wav.write_bytes(b"RIFF" + b"\x00" * 500)

    # Mock response
    mock_response_data = {
        "transcript": "Guys aaj hum deployment karne wale hain but production mein issue aa gaya.",
        "language_code": "hi-IN",
        "language_probability": 0.98,
        "timestamps": [
            {
                "text": "Guys aaj hum deployment karne wale hain",
                "start_time_seconds": 0.0,
                "end_time_seconds": 2.5
            },
            {
                "text": "but production mein issue aa gaya.",
                "start_time_seconds": 2.5,
                "end_time_seconds": 4.8
            }
        ]
    }

    async def mock_post(*args, **kwargs):
        return httpx.Response(200, json=mock_response_data)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    provider = SarvamProvider(api_key="test-key", model="saaras:v4", default_mode="codemix")
    result: TranscriptResult = await provider.transcribe(dummy_wav)

    assert result.provider_name == "sarvam"
    assert result.model_name == "saaras:v4"
    assert result.language_code == "hi-IN"
    assert result.language_probability == 0.98
    assert "Guys aaj hum deployment" in result.raw_transcript
    assert len(result.chunks) == 2
    assert result.chunks[0].start_time == 0.0
    assert result.chunks[0].end_time == 2.5

@pytest.mark.asyncio
async def test_sarvam_rate_limit(monkeypatch, tmp_path):
    dummy_wav = tmp_path / "test.wav"
    dummy_wav.write_bytes(b"RIFF" + b"\x00" * 500)

    async def mock_post_429(*args, **kwargs):
        return httpx.Response(429, json={"error": "Rate limit exceeded"})

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post_429)

    provider = SarvamProvider(api_key="test-key")
    with pytest.raises(ASRRateLimitedError):
        await provider.transcribe(dummy_wav)
