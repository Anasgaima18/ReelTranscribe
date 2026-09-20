import pytest
import httpx
from backend.app.asr.hinglish import HinglishProvider

def test_hinglish_models_verified():
    provider = HinglishProvider(token="test")
    assert "Oriserve/Whisper-Hindi2Hinglish-Prime" in provider.SUPPORTED_MODELS
    assert "Oriserve/Whisper-Hindi2Hinglish-Apex" in provider.SUPPORTED_MODELS
    assert "shunyalabs/zero-stt-hinglish" in provider.SUPPORTED_MODELS

@pytest.mark.asyncio
async def test_hinglish_preserves_code_switching(monkeypatch, tmp_path):
    dummy_wav = tmp_path / "hinglish_sample.wav"
    dummy_wav.write_bytes(b"RIFF" + b"\x00" * 500)

    expected_code_mix = "Guys aaj hum deployment karne wale hain but production mein issue aa gaya."

    async def mock_post(*args, **kwargs):
        return httpx.Response(200, json={"text": expected_code_mix, "chunks": []})

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    provider = HinglishProvider(token="hf_test_token")
    result = await provider.transcribe(dummy_wav)

    assert result.provider_name == "hinglish_specialist"
    assert result.language_code == "hi-en"
    assert result.raw_transcript == expected_code_mix
    assert result.final_transcript == expected_code_mix
    # Crucial check: verify that words are NOT translated to English
    assert "aaj" in result.final_transcript
    assert "production mein issue" in result.final_transcript
