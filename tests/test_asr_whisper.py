import pytest
import httpx
from backend.app.asr.whisper import WhisperProvider
from backend.app.core.errors import ASRRateLimitedError, ASRProviderUnavailableError

@pytest.mark.asyncio
async def test_whisper_provider_availability():
    p_no_token = WhisperProvider(token="")
    assert p_no_token.is_available() is False

    p_with_token = WhisperProvider(token="hf_valid_token_test")
    assert p_with_token.is_available() is True

@pytest.mark.asyncio
async def test_whisper_transcribe_mock(monkeypatch, tmp_path):
    dummy_wav = tmp_path / "test_whisper.wav"
    dummy_wav.write_bytes(b"RIFF" + b"\x00" * 500)

    mock_hf_response = {
        "text": "This is a high quality test transcription from Whisper large v3.",
        "chunks": [
            {
                "text": "This is a high quality test",
                "timestamp": [0.0, 2.0]
            },
            {
                "text": "transcription from Whisper large v3.",
                "timestamp": [2.0, 4.5]
            }
        ]
    }

    async def mock_post(*args, **kwargs):
        # Verify Authorization header contains Bearer token
        assert "Authorization" in kwargs.get("headers", {})
        assert kwargs["headers"]["Authorization"] == "Bearer hf_test_token"
        return httpx.Response(200, json=mock_hf_response)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    provider = WhisperProvider(token="hf_test_token", model_name="openai/whisper-large-v3")
    result = await provider.transcribe(dummy_wav)

    assert result.provider_name == "whisper"
    assert result.model_name == "openai/whisper-large-v3"
    assert "Whisper large v3" in result.raw_transcript
    assert len(result.chunks) == 2
    assert result.chunks[0].start_time == 0.0
    assert result.chunks[0].end_time == 2.0
    assert result.fallback_used is True

@pytest.mark.asyncio
async def test_whisper_rate_limit_and_503(monkeypatch, tmp_path):
    dummy_wav = tmp_path / "test_whisper.wav"
    dummy_wav.write_bytes(b"RIFF" + b"\x00" * 500)

    async def mock_post_503(*args, **kwargs):
        return httpx.Response(503, json={"error": "Model is loading"})

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post_503)

    provider = WhisperProvider(token="hf_test_token")
    with pytest.raises(ASRProviderUnavailableError):
        await provider.transcribe(dummy_wav)
